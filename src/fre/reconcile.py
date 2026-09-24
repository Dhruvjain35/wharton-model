"""Reconciliation gate: every reported fact against the statement line it came from.

Outcomes per fact:
  matched      the filing's own statement shows this tag, period and value (at its presentation precision)
  mismatch     the statement shows a different value -> blocks the fact
  ambiguous    the tag appears on several lines with different values
  from-notes   the tag is not on a primary statement; the value comes from the notes
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


def reconcile(ds: Dataset, fetch=primary_statements) -> list[ReconRecord]:
    cik = int(ds.company.cik)
    cache: dict[str, list[Statement]] = {}
    records = []
    for key, f in sorted(ds.facts.items()):
        if f.status != FactStatus.REPORTED or not f.sources:
            records.append(ReconRecord(fact=key, outcome="not-checked", expected=f.value))
            continue
        src = f.sources[0]
        if src.accession not in cache:
            cache[src.accession] = fetch(cik, src.accession)
        months = None if f.period_start is None else 12
        hits = []
        for st in cache[src.accession]:
            col = st.column_index(months, f.period_end)
            if col is None:
                continue
            for row in st.rows_for(src.locator):
                if col < len(row.values) and row.values[col] is not None:
                    hits.append((st, row, row.values[col]))
        if not hits:
            records.append(ReconRecord(fact=key, outcome="from-notes", expected=f.value))
            continue
        distinct = {v for _, _, v in hits}
        st, row, found = hits[0]
        if len(distinct) > 1:
            outcome = "ambiguous"
        elif abs(found - f.value) <= _tolerance(f.unit, f.value):
            outcome = "matched"
        elif src.locator.startswith("us-gaap:Payments") and abs(found + f.value) <= _tolerance(f.unit, f.value):
            # cash outflows are positive in XBRL and shown in parentheses on the cash flow statement
            outcome = "matched"
        else:
            outcome = "mismatch"
        records.append(ReconRecord(fact=key, outcome=outcome, expected=f.value, found=found, statement=st.title,
                                   line=row.label, url=st.url, snapshot_id=st.snapshot_id))

    for r in records:
        metric, label = r.fact.split("@")
        if r.outcome == "mismatch":
            ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: normalized {r.expected:g} but '{r.line}' on {r.statement} shows {r.found:g}"))
        elif r.outcome == "ambiguous":
            ds.review.append(ReviewItem(severity="warn", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: tag appears on several statement lines with different values"))
    return records
