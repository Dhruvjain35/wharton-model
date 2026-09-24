"""SEC Company Facts -> one reviewed annual Fact per (metric, fiscal year).

Selection policy, in order:
  1. Only 10-K / 10-K/A observations whose period matches the company's fiscal year
     end (within 10 days for 52/53-week years) and, for flows, lasts one year.
  2. The first tag in the metric's priority list that has such an observation.
  3. The most recently filed accession: current research uses restated values.
  4. Two different values inside that one accession = CONFLICTING (value withheld).
  5. Older accessions with different values are kept as `restated_from`; a stock
     split that fully explains the difference is labelled, anything else is a warning.
  6. Per-share and share-count values filed before a split are rebased to the
     current share basis and marked DERIVED, never silently mixed.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from .concepts import METRICS, MetricSpec
from .models import Company, Fact, FactStatus, Restatement, ReviewItem, Source

ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT"}
FYE_TOLERANCE_DAYS = 10


@dataclass(frozen=True)
class CorporateAction:
    kind: str  # "split"
    ratio: float  # new shares per old share
    effective: date
    source: str


@dataclass
class Dataset:
    company: Company
    fiscal_years: list[int]
    snapshot_ids: dict[str, str]
    facts: dict[str, Fact] = field(default_factory=dict)
    review: list[ReviewItem] = field(default_factory=list)
    actions: list[CorporateAction] = field(default_factory=list)
    annual_filings: dict[str, str] = field(default_factory=dict)  # "FY2025" -> accession of that year's 10-K

    @property
    def labels(self) -> list[str]:
        return [f"FY{y}" for y in self.fiscal_years]

    def fact(self, metric: str, label: str) -> Fact:
        return self.facts[f"{metric}@{label}"]

    def value(self, metric: str, label: str) -> float | None:
        f = self.facts.get(f"{metric}@{label}")
        return None if f is None else f.value

    def add(self, fact: Fact) -> None:
        self.facts[fact.key] = fact


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _fye_end(fye_mmdd: str, year: int) -> date:
    return date(year, int(fye_mmdd[:2]), int(fye_mmdd[2:]))


def _matches_year(o: dict, spec: MetricSpec, fye: str, year: int) -> bool:
    if o.get("form") not in ANNUAL_FORMS:
        return False
    end = _d(o["end"])
    if abs((end - _fye_end(fye, year)).days) > FYE_TOLERANCE_DAYS:
        return False
    if spec.kind == "instant":
        return "start" not in o
    if "start" not in o:
        return False
    return 350 <= (end - _d(o["start"])).days <= 380


def _pending_split_factor(filed: date, actions: list[CorporateAction]) -> float:
    """Splits that happened after this filing: its share-basis values predate them."""
    f = 1.0
    for a in actions:
        if a.kind == "split" and a.effective > filed:
            f *= a.ratio
    return f


def _to_current_basis(value: float, unit: str, factor: float) -> float:
    if factor == 1.0:
        return value
    return value / factor if unit == "USD/shares" else value * factor


def _close(a: float, b: float, unit: str) -> bool:
    if unit == "USD/shares":
        return abs(a - b) <= 0.006  # both sides rounded to cents
    return abs(a - b) <= max(abs(b) * 0.002, 0.5)


def _rounding_unit(v: float) -> float:
    """Largest power of ten that divides the value: 18,900,000,000 -> 100,000,000."""
    n = abs(int(round(v)))
    if n == 0 or n != abs(v):
        return 0.0
    unit = 1
    while n % (unit * 10) == 0:
        unit *= 10
    return float(unit)


def _precision_difference(a: float, b: float) -> bool:
    """True when one disclosure is just a rounded version of the other."""
    coarse = max(_rounding_unit(a), _rounding_unit(b))
    return coarse >= 1_000_000 and abs(a - b) <= coarse / 2


def _filing_url(cik: int, accn: str, primary_docs: dict[str, str]) -> str:
    folder = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace('-', '')}"
    doc = primary_docs.get(accn)
    return f"{folder}/{doc}" if doc else f"{folder}/{accn}-index.htm"


def _select_tag(gaap: dict, spec: MetricSpec, fye: str, year: int) -> tuple[str | None, list[dict]]:
    for tag in spec.tags:
        units = gaap.get(tag, {}).get("units", {})
        found = [o for o in units.get(spec.unit, []) if _matches_year(o, spec, fye, year)]
        if found:
            return tag, found
    return None, []


def _latest_value_for_tag(gaap: dict, tag: str, spec: MetricSpec, fye: str, year: int) -> float | None:
    found = [o for o in gaap.get(tag, {}).get("units", {}).get(spec.unit, []) if _matches_year(o, spec, fye, year)]
    if not found:
        return None
    latest = max(found, key=lambda o: (o["filed"], o["accn"]))
    vals = {o["val"] for o in found if o["accn"] == latest["accn"]}
    return next(iter(vals)) if len(vals) == 1 else None


def annual_accessions(companyfacts: dict, fye: str) -> dict[int, str]:
    """Each fiscal year's own 10-K: the annual filing whose latest reported period ends on that year's FYE.

    Built from Company Facts, which lists every filing; the submissions 'recent' list is
    truncated to roughly the last thousand filings and can miss older 10-Ks entirely.
    """
    latest_fy: dict[str, int] = {}
    for tag in companyfacts["facts"].get("us-gaap", {}).values():
        for obs_list in tag.get("units", {}).values():
            for o in obs_list:
                if o.get("form") not in ANNUAL_FORMS:
                    continue
                e = _d(o["end"])
                for year in (e.year - 1, e.year, e.year + 1):
                    # only fiscal-year-end dates count; subsequent-event dates are ignored
                    if abs((e - _fye_end(fye, year)).days) <= FYE_TOLERANCE_DAYS:
                        latest_fy[o["accn"]] = max(latest_fy.get(o["accn"], year), year)
    out: dict[int, str] = {}
    for accn, year in sorted(latest_fy.items()):
        out.setdefault(year, accn)  # original 10-K before any amendment
    return out


def normalize(
    companyfacts: dict,
    submissions: dict,
    *,
    snapshot_ids: dict[str, str],
    retrieved_at: str,
    actions: list[CorporateAction],
    fiscal_years: list[int],
    metrics: dict[str, MetricSpec] = METRICS,
) -> Dataset:
    cik = int(companyfacts["cik"])
    fye = submissions["fiscalYearEnd"]
    recent = submissions["filings"]["recent"]
    primary_docs = dict(zip(recent["accessionNumber"], recent["primaryDocument"]))
    company = Company(
        cik=str(cik).zfill(10),
        legal_name=companyfacts["entityName"],
        tickers=list(submissions.get("tickers", [])),
        fiscal_year_end=fye,
    )
    gaap = companyfacts["facts"].get("us-gaap", {})
    ds = Dataset(company=company, fiscal_years=sorted(fiscal_years), snapshot_ids=snapshot_ids, actions=actions)
    for year, accn in annual_accessions(companyfacts, fye).items():
        if year in ds.fiscal_years:
            ds.annual_filings[f"FY{year}"] = accn

    for spec in metrics.values():
        tags_used: dict[int, str] = {}
        for year in ds.fiscal_years:
            label = f"FY{year}"
            tag, found = _select_tag(gaap, spec, fye, year)
            end = _fye_end(fye, year)
            if tag is None:
                ds.add(Fact(company=company.cik, metric=spec.id, value=None, unit=spec.unit,
                            period_start=None, period_end=end, fiscal_label=label, status=FactStatus.MISSING,
                            notes=[f"No annual 10-K observation under {', '.join(spec.tags)}"]))
                ds.review.append(ReviewItem(severity="info" if spec.optional else "warn", metric=spec.id,
                                            fiscal_label=label, kind="missing",
                                            message=f"{spec.label} {label}: not found under any mapped tag"
                                                    + (" (alternative presentation; expected for some filers)" if spec.optional else "")))
                continue
            tags_used[year] = tag
            ds.add(_build_fact(ds, spec, tag, found, label, cik, primary_docs, snapshot_ids, retrieved_at, actions))

        if len(set(tags_used.values())) > 1:
            ds.review.append(_tag_switch_item(gaap, spec, fye, tags_used))
    return ds


def _build_fact(ds, spec, tag, found, label, cik, primary_docs, snapshot_ids, retrieved_at, actions) -> Fact:
    by_accn: dict[str, list[dict]] = defaultdict(list)
    for o in found:
        by_accn[o["accn"]].append(o)
    latest_accn = max(by_accn, key=lambda a: (by_accn[a][0]["filed"], a))
    latest = by_accn[latest_accn]
    head = latest[0]
    filed = _d(head["filed"])
    src = Source(accession=latest_accn, form=head["form"], filed=filed,
                 url=_filing_url(cik, latest_accn, primary_docs), locator=f"us-gaap:{tag}",
                 snapshot_id=snapshot_ids["companyfacts"], retrieved_at=retrieved_at)
    start = _d(head["start"]) if "start" in head else None
    end = _d(head["end"])
    base = dict(company=ds.company.cik, metric=spec.id, unit=spec.unit, period_start=start,
                period_end=end, fiscal_label=label, sources=[src])

    distinct = sorted({o["val"] for o in latest})
    if len(distinct) > 1:
        ds.review.append(ReviewItem(severity="block", metric=spec.id, fiscal_label=label, kind="conflicting",
                                    message=f"{spec.label} {label}: {latest_accn} reports {distinct}; resolve before use"))
        return Fact(**base, value=None, status=FactStatus.CONFLICTING, candidates=distinct)

    raw = distinct[0]
    factor = _pending_split_factor(filed, actions) if spec.share_basis else 1.0
    value = _to_current_basis(raw, spec.unit, factor)

    restated = []
    for accn, group in by_accn.items():
        if accn == latest_accn:
            continue
        old_filed = _d(group[0]["filed"])
        for old in sorted({o["val"] for o in group}):
            if old == raw:
                continue
            old_factor = _pending_split_factor(old_filed, actions) if spec.share_basis else 1.0
            rebased = _to_current_basis(old, spec.unit, old_factor)
            if old_factor != factor and _close(rebased, value, spec.unit):
                splits = [a for a in actions if a.kind == "split" and old_filed < a.effective]
                reason = "; ".join(f"{a.ratio:g}-for-1 stock split effective {a.effective}" for a in splits)
            elif spec.unit == "USD" and _precision_difference(old, raw):
                reason = "precision difference: one disclosure is rounded"
            else:
                reason = "unexplained"
            restated.append(Restatement(accession=accn, filed=old_filed, value=old, reason=reason))
    restated.sort(key=lambda r: r.filed)
    notes: list[str] = []
    # A later filing that only rounds an earlier precise value (e.g. "$18.9 billion" for 18,892m)
    # must not replace the statement figure: keep the most precise disclosure.
    precise = [r for r in restated if r.reason.startswith("precision") and _rounding_unit(r.value) < _rounding_unit(raw)]
    if precise:
        best = min(precise, key=lambda r: (_rounding_unit(r.value), -r.filed.toordinal()))
        restated = [r for r in restated if r is not best] + [Restatement(
            accession=latest_accn, filed=filed, value=raw, reason="precision difference: later disclosure is rounded")]
        restated.sort(key=lambda r: r.filed)
        raw = value = best.value
        latest_accn, filed = best.accession, best.filed
        src = src.model_copy(update={"accession": latest_accn, "filed": filed,
                                     "url": _filing_url(cik, latest_accn, primary_docs)})
        base["sources"] = [src]
        notes.append(f"Kept the precise value from {latest_accn}; a later filing states it rounded")
    for r in restated:
        explained = r.reason != "unexplained"
        ds.review.append(ReviewItem(
            severity="info" if explained else "warn", metric=spec.id, fiscal_label=label, kind="restated",
            message=f"{spec.label} {label}: {r.accession} reported {r.value:g}, latest filing reports {raw:g}"
                    + (f" ({r.reason})" if explained else "; confirm the reason in the later filing")))

    if factor != 1.0:
        splits = [a for a in actions if a.kind == "split" and a.effective > filed]
        ds.review.append(ReviewItem(severity="info", metric=spec.id, fiscal_label=label, kind="split-adjusted",
                                    message=f"{spec.label} {label}: only a pre-split filing reports this; rebased by {factor:g}x"))
        op = "/" if spec.unit == "USD/shares" else "×"
        return Fact(**base, value=value, status=FactStatus.DERIVED, restated_from=restated,
                    formula=f"reported {raw:g} {op} {factor:g} (split effective "
                            + ", ".join(str(a.effective) for a in splits) + ")",
                    notes=["Rebased to the post-split share basis"])
    return Fact(**base, value=value, status=FactStatus.REPORTED, restated_from=restated, notes=notes)


def _tag_switch_item(gaap, spec, fye, tags_used: dict[int, str]) -> ReviewItem:
    tags = sorted(set(tags_used.values()), key=spec.tags.index)
    overlaps, disagreements = 0, []
    years = range(min(tags_used) - 3, max(tags_used) + 1)
    for year in years:
        vals = {t: _latest_value_for_tag(gaap, t, spec, fye, year) for t in tags}
        present = {t: v for t, v in vals.items() if v is not None}
        if len(present) > 1:
            overlaps += 1
            if len(set(present.values())) > 1:
                disagreements.append(f"FY{year}: {present}")
    mix = ", ".join(f"FY{y}={t}" for y, t in sorted(tags_used.items()))
    if disagreements:
        return ReviewItem(severity="warn", metric=spec.id, fiscal_label=None, kind="tag-switch",
                          message=f"{spec.label} mixes tags ({mix}) and they disagree: {'; '.join(disagreements)}")
    if overlaps == 0:
        return ReviewItem(severity="warn", metric=spec.id, fiscal_label=None, kind="tag-switch",
                          message=f"{spec.label} mixes tags ({mix}) with no overlapping period to verify equivalence")
    return ReviewItem(severity="info", metric=spec.id, fiscal_label=None, kind="tag-switch",
                      message=f"{spec.label} mixes tags ({mix}); values agree on all {overlaps} overlapping periods")
