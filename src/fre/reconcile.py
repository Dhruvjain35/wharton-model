"""Reconciliation gate: every reported fact against the statement line it came from.

Outcomes per fact:
  matched      the source filing's statement (or that fiscal year's own 10-K) shows this tag, period and value
               at its presentation precision;
               when the tag also carries dimensional breakdown lines, one line must equal the value
  matched-negated  same, printed with the opposite sign on the cash flow statement
  mismatch     the statement shows a different value -> blocks the fact
  ambiguous    the tag is on several lines and none equals the value -> blocks
  matched-in-notes  not on a primary statement, but a note detail table shows this tag, period and value
  matched-in-text   weakest tier: the printed value (or an explicit "no ... outstanding") sits next to
               the metric's keyword in the filing document; the snippet is kept as evidence
  from-notes   not found on a primary statement, a parsed note table or the text; verify by hand
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
    scale: float | None = None  # presentation scale of the statement the value was found on

    def to_dict(self) -> dict:
        return asdict(self)


def _scale_for(st: Statement, unit: str) -> float:
    return st.usd_scale if unit == "USD" else st.share_scale if unit == "shares" else 1.0


def _tolerance(unit: str, value: float) -> float:
    if unit == "USD/shares":
        return 0.005
    # statements present in millions (or thousands); allow half a presentation unit
    return 0.5e6 if abs(value) >= 1e6 else 0.5


# tags a cash flow statement prints with the opposite sign: outflows, and gains removed from net income
NEGATED_ON_CASH_FLOW = __import__("re").compile(r":(Payments|Repayments|.*GainLoss|IncreaseDecrease|.*FvNi)")

TEXT_KEYWORDS = {
    "commercial_paper": r"commercial paper",
    "debt_lt_current": r"short-term debt|current portion",
    "operating_lease_liability": r"operating lease liabilit",
    "finance_lease_liability": r"finance lease liabilit",
    "shares_outstanding": r"shares (issued and )?outstanding|outstanding shares",
    "unvested_rsus": r"unvested",
    "preferred_dividends": r"preferred",
}


def _in_text(key, f, src, fetch_text) -> ReconRecord | None:
    """Weakest tier: the value as printed, next to the metric's own keyword, in the filing document."""
    import re

    kw = TEXT_KEYWORDS.get(f.metric)
    if not kw or fetch_text is None or not src.url.endswith(".htm") or src.url.endswith("-index.htm"):
        return None
    text = fetch_text(src.url)
    if f.value == 0:
        m = re.search(rf"\bno (?:{kw})[^.]{{0,80}}outstanding", text, re.I)
        if m:
            return ReconRecord(fact=key, outcome="matched-in-text", expected=0.0, found=0.0,
                               statement="filing text", line=m.group(0), url=src.url)
        return None
    scale = 1e6 if abs(f.value) >= 1e6 else 1.0
    if abs(abs(f.value) / scale - round(abs(f.value) / scale)) > 1e-9:
        return None
    forms = [re.escape(f"{abs(f.value) / scale:,.0f}")]
    if abs(f.value) >= 1e9 and abs(f.value) % 1e8 == 0:  # "$2.3 billion", "$ 2.3 billion"
        forms.append(rf"\$ ?{re.escape(f'{abs(f.value) / 1e9:.1f}')} billion")
    for m in re.finditer(rf"(?<![\d,.])(?:{'|'.join(forms)})(?![\d,]|\.\d)", text):
        window = text[max(0, m.start() - 250):m.end() + 60]  # keyword must sit right next to the figure
        if re.search(kw, window, re.I):
            return ReconRecord(fact=key, outcome="matched-in-text", expected=f.value, found=f.value,
                               statement="filing text", line=text[max(0, m.start() - 120):m.end() + 20], url=src.url)
    return None


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
                                       statement=st.title, line=row.label, url=st.url, snapshot_id=st.snapshot_id,
                                       scale=_scale_for(st, f.unit))
    return ReconRecord(fact=key, outcome="from-notes", expected=f.value)


def reconcile(ds: Dataset, fetch=primary_statements, fetch_notes=None, fetch_text=None) -> list[ReconRecord]:
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
            rec = _in_notes(key, f, src, months, cik, fetch_notes, notes_cache)
            if rec.outcome == "from-notes":
                rec = _in_text(key, f, src, fetch_text) or rec
            records.append(rec)
            continue
        tol = _tolerance(f.unit, f.value)
        exact = [h for h in hits if abs(h[2] - f.value) <= tol]
        # cash flow statements print many items with the opposite sign (outflows, gains removed from CFO)
        negated = [h for h in hits if h[0].is_cash_flow and NEGATED_ON_CASH_FLOW.search(src.locator)
                   and abs(h[2] + f.value) <= tol]
        if exact:
            (st, row, found), outcome = exact[0], "matched"
        elif negated:
            (st, row, found), outcome = negated[0], "matched-negated"
        else:
            (st, row, found) = hits[0]
            outcome = "ambiguous" if len({h[2] for h in hits}) > 1 else "mismatch"
        records.append(ReconRecord(fact=key, outcome=outcome, expected=f.value, found=found, statement=st.title,
                                   line=row.label, url=st.url, snapshot_id=st.snapshot_id,
                                   scale=_scale_for(st, f.unit)))

    for r in records:  # record the filing's presentation scale on every fact a statement or table verified
        f = ds.facts[r.fact]
        if r.outcome in ("matched", "matched-negated", "matched-in-notes") and r.scale:
            ds.facts[r.fact] = f.model_copy(update={"scale": int(r.scale)})
        elif r.outcome == "matched-in-text":
            ds.facts[r.fact] = f.model_copy(update={"scale": 1_000_000 if abs(f.value or 0) >= 1e6 else 1})
    for r in records:
        metric, label = r.fact.split("@")
        if r.outcome in ("mismatch", "ambiguous"):
            # PRD section 8: an unreconciled input must not feed any calculation
            f = ds.facts[r.fact]
            ds.facts[r.fact] = f.model_copy(update={
                "value": None, "status": FactStatus.CONFLICTING,
                "candidates": sorted({f.value, r.found} - {None}),
                "notes": f.notes + [f"Withheld: filed statement shows {r.found:g} on '{r.line}'"]})
        if r.outcome == "mismatch":
            ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: normalized {r.expected:g} but '{r.line}' on {r.statement} shows {r.found:g}"))
        elif r.outcome == "ambiguous":
            ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="reconciliation",
                                        message=f"{r.fact}: tag is on several statement lines and none shows {r.expected:g}"))
    return records
