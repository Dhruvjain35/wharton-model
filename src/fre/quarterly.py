"""Quarterly, year-to-date and trailing-twelve-month facts.

Rules (PRD section 8):
  - flows are matched on exact start and end dates; a YTD value is never mistaken for a quarter
  - TTM = last fiscal year + current YTD - prior-year YTD (never a sum of four quarters)
  - a standalone quarter is the reported three-month value, or YTD minus the prior YTD
    of the same fiscal year, labelled DERIVED with its formula
  - balance-sheet values are points in time and are never summed
"""

from __future__ import annotations

from datetime import date, timedelta

from .concepts import METRICS
from .models import Fact, FactStatus, Source

FORMS = {"10-Q", "10-Q/A", "10-K", "10-K/A"}


class QuarterlyError(ValueError):
    pass


def _hits(cf: dict, metric: str, start: date | None, end: date, only_tag: str | None = None):
    spec = METRICS[metric]
    gaap = cf["facts"].get("us-gaap", {})
    for tag in ([only_tag] if only_tag else spec.tags):
        hits = [x for x in gaap.get(tag, {}).get("units", {}).get(spec.unit, [])
                if x.get("form") in FORMS and x["end"] == str(end)
                and (x.get("start") == str(start) if start else "start" not in x)]
        if hits:
            return hits, tag
    return [], None


def _find(cf: dict, metric: str, start: date | None, end: date, only_tag: str | None = None):
    """Latest-filed observation with exactly this period, over the metric's tags in priority order."""
    hits, tag = _hits(cf, metric, start, end, only_tag)
    return (max(hits, key=lambda x: (x["filed"], x["accn"])), tag) if hits else None


def _source(cf: dict, obs: dict, tag: str) -> Source:
    cik = int(cf["cik"])
    return Source(accession=obs["accn"], form=obs["form"], filed=date.fromisoformat(obs["filed"]),
                  url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{obs['accn'].replace('-', '')}/{obs['accn']}-index.htm",
                  locator=f"us-gaap:{tag}", snapshot_id="companyfacts", retrieved_at="")


def _reported(cf, metric, start, end, label, actions=(), only_tag=None) -> Fact:
    spec = METRICS[metric]
    hit = _find(cf, metric, start, end, only_tag)
    if hit is None:
        return Fact(company=str(cf["cik"]), metric=metric, value=None, unit=spec.unit, period_start=start,
                    period_end=end, fiscal_label=label, status=FactStatus.MISSING,
                    notes=[f"No 10-Q/10-K observation of {metric} for {start or ''}..{end}"])
    obs, tag = hit
    value, status, formula = float(obs["val"]), FactStatus.REPORTED, None
    if spec.share_basis:  # same split rule as annual facts: rebase values filed before a later split
        from .normalize import _pending_split_factor, _to_current_basis
        factor = _pending_split_factor(date.fromisoformat(obs["filed"]), list(actions))
        if factor != 1.0:
            value = _to_current_basis(value, spec.unit, factor)
            status, formula = FactStatus.DERIVED, f"reported {obs['val']:g} rebased by {factor:g}x for later stock split"
    from .models import Restatement
    older = {}
    for x in _hits(cf, metric, start, end, tag)[0]:
        if x["accn"] != obs["accn"] and float(x["val"]) != float(obs["val"]):
            older.setdefault(x["accn"], x)
    restated = [Restatement(accession=a, filed=date.fromisoformat(x["filed"]), value=float(x["val"]), reason="unexplained")
                for a, x in sorted(older.items(), key=lambda kv: kv[1]["filed"])]
    return Fact(company=str(cf["cik"]), metric=metric, value=value, unit=spec.unit, period_start=start,
                period_end=end, fiscal_label=label, status=status, formula=formula, sources=[_source(cf, obs, tag)],
                restated_from=restated)


def ytd(cf: dict, metric: str, start: date, end: date, actions=()) -> Fact:
    return _reported(cf, metric, start, end, f"YTD{end}", actions)


def instant(cf: dict, metric: str, on: date, actions=()) -> Fact:
    if METRICS[metric].kind != "instant":
        raise QuarterlyError(f"{metric} is a flow, not a balance-sheet value")
    return _reported(cf, metric, None, on, f"AT{on}", actions)


def _derived(cf, metric, start, end, label, parts: list[tuple[int, Fact]], formula: str) -> Fact:
    spec = METRICS[metric]
    missing = [f for _, f in parts if f.value is None]
    inputs = [f"{f.metric}@{f.period_start}..{f.period_end}" for _, f in parts]
    if missing:
        return Fact(company=str(cf["cik"]), metric=metric, value=None, unit=spec.unit, period_start=start,
                    period_end=end, fiscal_label=label, status=FactStatus.MISSING, formula=formula, inputs=inputs,
                    notes=[f"Blocked: {m.metric} {m.period_start}..{m.period_end} (YTD) is missing" for m in missing])
    return Fact(company=str(cf["cik"]), metric=metric, value=sum(sign * f.value for sign, f in parts), unit=spec.unit,
                period_start=start, period_end=end, fiscal_label=label, status=FactStatus.DERIVED, formula=formula,
                inputs=inputs, sources=[s for _, f in parts for s in f.sources])


def _fy_start(end: date, fye: str) -> date:
    """First day of the fiscal year containing `end`."""
    m, d = int(fye[:2]), int(fye[2:])
    fy_end = date(end.year, m, d)
    if fy_end < end:
        fy_end = date(end.year + 1, m, d)
    prev_end = date(fy_end.year - 1, m, d)
    return prev_end + timedelta(days=1)


def ttm(cf: dict, metric: str, end: date, fye: str) -> Fact:
    if METRICS[metric].kind == "instant":
        raise QuarterlyError(f"{metric} is a balance-sheet value; a TTM would sum points in time")
    start = _fy_start(end, fye)
    fy_end = start - timedelta(days=1)
    fy = _reported(cf, metric, _fy_start(fy_end, fye), fy_end, "FY")
    cur = ytd(cf, metric, start, end)
    prior = ytd(cf, metric, _fy_start(fy_end, fye), date(end.year - 1, end.month, end.day))
    formula = f"FY ending {fy_end} + YTD ending {end} - YTD ending {prior.period_end}"
    ttm_start = date(end.year - 1, end.month, end.day) + timedelta(days=1)
    return _derived(cf, metric, ttm_start, end, f"TTM{end}", [(1, fy), (1, cur), (-1, prior)], formula)


def standalone_quarter(cf: dict, metric: str, start: date, end: date) -> Fact:
    """Reported three-month value in the SAME concept as the YTD figure, else YTD minus the prior YTD."""
    spec = METRICS[metric]
    gaap = cf["facts"].get("us-gaap", {})
    starts = sorted({x["start"] for t in spec.tags for x in gaap.get(t, {}).get("units", {}).get(spec.unit, [])
                     if x.get("form") in FORMS and x["end"] == str(end) and "start" in x and x["start"] < str(start)})
    if not starts:
        return _reported(cf, metric, start, end, f"Q{end}")
    fy_start = date.fromisoformat(starts[0])
    ytd_hit = _find(cf, metric, fy_start, end)
    tag = ytd_hit[1] if ytd_hit else None
    direct = _reported(cf, metric, start, end, f"Q{end}", only_tag=tag)
    if direct.value is not None:
        return direct
    ytd_end = _reported(cf, metric, fy_start, end, f"YTD{end}", only_tag=tag)
    ytd_prev = _reported(cf, metric, fy_start, start - timedelta(days=1), f"YTD{start - timedelta(days=1)}", only_tag=tag)
    formula = f"YTD ending {end} - YTD ending {start - timedelta(days=1)}"
    return _derived(cf, metric, start, end, f"Q{end}", [(1, ytd_end), (-1, ytd_prev)], formula)
