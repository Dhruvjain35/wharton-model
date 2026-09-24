"""The latest reported period after the last 10-K: YTD, prior-year YTD, TTM and the balance sheet.

The same gate as annual facts applies: every reported YTD and balance value is
reconciled to the 10-Q statement it came from, and a mismatch withholds it. TTM is
derived only from reconciled inputs: last fiscal year + YTD - prior-year YTD.
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Fact, FactStatus
from .normalize import Dataset, _filing_url
from .quarterly import instant, standalone_quarter, ytd
from .reconcile import ReconRecord, reconcile

FLOWS = ["revenue", "operating_income", "net_income", "equity_securities_gain", "pretax_income", "income_tax",
         "cfo", "capex", "dna", "sbc", "buybacks", "dividends", "preferred_dividends"]
BALANCE = ["cash", "st_investments", "other_lt_investments", "debt_lt_noncurrent", "debt_lt_current",
           "finance_lease_liability", "commercial_paper", "operating_lease_liability", "preferred_equity",
           "shares_outstanding", "unvested_rsus", "equity"]


def _shift_year(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 February
        return d.replace(year=d.year + years, day=28)


def _quarter_start(end: date) -> date:
    m = end.month - 2
    y = end.year
    if m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)


def latest_end(cf: dict, fy_start: date) -> date | None:
    ends = [date.fromisoformat(o["end"]) for u in cf["facts"]["us-gaap"].get("Revenues", {}).get("units", {}).values()
            for o in u if o.get("form", "").startswith("10-Q") and o.get("start") == str(fy_start)]
    ends += [date.fromisoformat(o["end"]) for u in cf["facts"]["us-gaap"].get(
        "RevenueFromContractWithCustomerExcludingAssessedTax", {}).get("units", {}).values()
             for o in u if o.get("form", "").startswith("10-Q") and o.get("start") == str(fy_start)]
    return max(ends) if ends else None


def build_latest(annual: Dataset, cf: dict, submissions: dict, fetch, fetch_notes) -> tuple[Dataset | None, list[ReconRecord], dict]:
    last = annual.labels[-1]
    fy_end = annual.fact("revenue", last).period_end
    start = fy_end + timedelta(days=1)
    end = latest_end(cf, start)
    if end is None:
        return None, [], {}
    prior_start, prior_end = _shift_year(start, -1), _shift_year(end, -1)
    labels = {"cur": f"YTD{end}", "prior": f"YTD{prior_end}", "ttm": f"TTM{end}", "bs": f"AT{end}", "q": f"Q{end}"}
    q_start = _quarter_start(end)
    recent = submissions["filings"]["recent"]
    docs = dict(zip(recent["accessionNumber"], recent["primaryDocument"]))
    cik = int(cf["cik"])

    ds = Dataset(company=annual.company, fiscal_years=[], snapshot_ids=annual.snapshot_ids,
                 filing_dates=annual.filing_dates)

    def put(f: Fact, label: str) -> None:
        srcs = [s.model_copy(update={"snapshot_id": annual.snapshot_ids["companyfacts"],
                                     "url": _filing_url(cik, s.accession, docs)}) for s in f.sources]
        ds.add(f.model_copy(update={"fiscal_label": label, "sources": srcs}))

    for m in FLOWS:
        put(ytd(cf, m, start, end, annual.actions), labels["cur"])
        put(ytd(cf, m, prior_start, prior_end, annual.actions), labels["prior"])
    for m in BALANCE:
        put(instant(cf, m, end, annual.actions), labels["bs"])
    for m in FLOWS:  # the latest standalone quarter: reported three-month value, or YTD - prior YTD (derived)
        put(standalone_quarter(cf, m, q_start, end), labels["q"])
    from .filing_text import text_at
    recon = reconcile(ds, fetch=fetch, fetch_notes=fetch_notes, fetch_text=text_at if fetch_notes else None)

    for m in FLOWS:  # TTM from reconciled inputs only
        parts = [(1, annual.facts.get(f"{m}@{last}")), (1, ds.facts[f"{m}@{labels['cur']}"]),
                 (-1, ds.facts[f"{m}@{labels['prior']}"])]
        inputs = [f"{m}@{last}", f"{m}@{labels['cur']}", f"{m}@{labels['prior']}"]
        missing = [k for (_, f), k in zip(parts, inputs) if f is None or f.value is None]
        unit = ds.facts[f"{m}@{labels['cur']}"].unit
        common = dict(company=annual.company.cik, metric=m, unit=unit, period_start=prior_end + timedelta(days=1),
                      period_end=end, fiscal_label=labels["ttm"], inputs=inputs,
                      formula=f"{m} {last} + YTD to {end} - YTD to {prior_end}")
        if missing:
            ds.add(Fact(**common, value=None, status=FactStatus.MISSING,
                        notes=[f"Blocked: {k} is missing, unreconciled or withheld" for k in missing]))
        else:
            ds.add(Fact(**common, value=sum(sign * f.value for sign, f in parts), status=FactStatus.DERIVED))

    for lab in (labels["cur"], labels["prior"], labels["ttm"], labels["q"]):  # cash FCF on each window
        c, x = ds.facts[f"cfo@{lab}"], ds.facts[f"capex@{lab}"]
        v = None if c.value is None or x.value is None else c.value - x.value
        ds.add(Fact(company=annual.company.cik, metric="fcf", value=v, unit="USD", period_start=c.period_start,
                    period_end=c.period_end, fiscal_label=lab, status=FactStatus.DERIVED if v is not None else FactStatus.MISSING,
                    formula="cfo - capex", inputs=[f"cfo@{lab}", f"capex@{lab}"]))
    return ds, recon, labels
