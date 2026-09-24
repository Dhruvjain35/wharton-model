"""Reconciliation gate: every reported fact against the statement line it came from.

Outcomes per fact:
  matched      the source filing's statement (or that fiscal year's own 10-K) shows this tag, period and value
               at its presentation precision;
               when the tag also carries dimensional breakdown lines, one line must equal the value
  matched-negated  same, printed with the opposite sign on the cash flow statement
  mismatch     the statement shows a different value -> blocks the fact
  ambiguous    the tag is on several lines and none equals the value -> blocks
  matched-in-notes  not on a primary statement, but a note detail table shows this tag, period and value
  from-notes   not found on a primary statement or a parsed note table; verify by hand
  not-checked  derived, missing or conflicting facts (their own review items already cover them)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import FactStatus, ReviewItem
from .normalize import Dataset
from .statements import Statement, primary_statements


@dataclass(frozen=True)
class ReconRecord:
    fact: str
    outcome: str
    expected: float | None
    found: float | None = None
    statement: str | None = None
    line: str | None = None
    url: str | None = None
    snapshot_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _tolerance(unit: str, value: float) -> float:
    if unit == "USD/shares":
        return 0.005
    # statements present in millions (or thousands); allow half a presentation unit
    return 0.5e6 if abs(value) >= 1e6 else 0.5


def _in_notes(key, f, src, months, cik, fetch_notes, notes_cache) -> ReconRecord:
    """Look for the value in the filing's note detail tables: same tag, same period, same value."""
    if fetch_notes is None:
        return ReconRecord(fact=key, outcome="from-notes", expected=f.value)
    if src.accession not in notes_cache:
        notes_cache[src.accession] = fetch_notes(cik, src.accession)
    tol = _tolerance(f.unit, f.value)
    for st in notes_cache[src.accession]:
        for i, c in enumerate(st.columns):
            if c.end != f.period_end or (c.months != months and not (months is None and c.months is None)):
                continue
            for row in st.rows_for(src.locator):
                v = st.scaled(row, i, f.unit)
                if v is not None and (abs(v - f.value) <= tol or abs(v + f.value) <= tol):
                    return ReconRecord(fact=key, outcome="matched-in-notes", expected=f.value, found=v,
                                       statement=st.title, line=row.label, url=st.url, snapshot_id=st.snapshot_id)
    return ReconRecord(fact=key, outcome="from-notes", expected=f.value)


def reconcile(ds: Dataset, fetch=primary_statements, fetch_notes=None) -> list[ReconRecord]:
    cik = int(ds.company.cik)
    cache: dict[str, list[Statement]] = {}
    notes_cache: dict[str, list[Statement]] = {}
    records = []
    for key, f in sorted(ds.facts.items()):
        if f.status != FactStatus.REPORTED or not f.sources:
            records.append(ReconRecord(fact=key, outcome="not-checked", expected=f.value))
            continue
        src = f.sources[0]
        months = None if f.period_start is None else round((f.period_end - f.period_start).days / 30.44)
        hits = []
        own = ds.annual_filings.get(f.fiscal_label)
        filings = [src.accession] + ([own] if own and own != src.accession else [])
        for accn in filings:
            if accn not in cache:
                cache[accn] = fetch(cik, accn)
        for st in (st for accn in filings for st in cache[accn]):
            col = st.column_index(months, f.period_end)
            if col is None:
                continue
            for row in st.rows_for(src.locator):
                v = st.scaled(row, col, f.unit)
                if v is not None:
                    hits.append((st, row, v))
        if not hits:
            records.append(_in_notes(key, f, src, months, cik, fetch_notes, notes_cache))
            continue
        tol = _tolerance(f.unit, f.value)
        exact = [h for h in hits if abs(h[2] - f.value) <= tol]
        # cash flow statements print many items with the opposite sign (outflows, gains removed from CFO)
        negated = [h for h in hits if h[0].is_cash_flow and abs(h[2] + f.value) <= tol]
        if exact:
            (st, row, found), outcome = exact[0], "matched"
        elif negated:
            (st, row, found), outcome = negated[0], "matched-negated"
        else:
            (st, row, found) = hits[0]
            outcome = "ambiguous" if len({h[2] for h in hits}) > 1 else "mismatch"
        records.append(ReconRecord(fact=key, outcome=outcome, expected=f.value, found=found, statement=st.title,
                                   line=row.label, url=st.url, snapshot_id=st.snapshot_id))

    for r in records:
        metric, label = r.fact.split("@")
        if r.outcome == "mismatch":
            ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: normalized {r.expected:g} but '{r.line}' on {r.statement} shows {r.found:g}"))
        elif r.outcome == "ambiguous":
            ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: tag is on several statement lines and none shows {r.expected:g}"))
    return records
