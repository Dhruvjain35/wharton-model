"""Zero attestations, verified by the machine against the filing (never assumed).

A component the company simply does not have (no commercial paper, no current debt)
has no XBRL fact, so it is MISSING, and missing is not zero. An attestation turns it
into a DERIVED 0 only when all of these hold for that year's 10-K:
  - the fact is missing under every mapped tag,
  - no line on the primary statements carries a mapped tag or matches the label pattern,
  - no note detail table carries a mapped tag or matches the label pattern.
Otherwise the fact stays missing and a blocking review item says why.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .concepts import METRICS
from .models import FactStatus, ReviewItem, Source
from .normalize import Dataset
from .statements import note_details, primary_statements

ROOT = Path(__file__).resolve().parents[2]


def load_rules(ticker: str) -> list[dict]:
    path = ROOT / "reviews" / ticker / "attestations.yaml"
    if not path.exists():
        return []
    return (yaml.safe_load(path.read_text()) or {}).get("zero_if_not_presented") or []


def apply_zero_attestations(ds: Dataset, rules: list[dict], fetch=primary_statements,
                            fetch_notes=note_details) -> Dataset:
    cik = int(ds.company.cik)
    for rule in rules:
        metric = rule["metric"]
        tags = {f"us-gaap:{t}" for t in METRICS[metric].tags}
        pattern = re.compile(rule["absent_label_pattern"])
        for label in rule["fiscal_labels"]:
            key = f"{metric}@{label}"
            f = ds.facts.get(key)
            if f is None or f.status != FactStatus.MISSING:
                continue
            accn = ds.annual_filings.get(label)
            primary = fetch(cik, accn) if accn else []
            months = None if METRICS[metric].kind == "instant" else 12
            sheets = [st for st in primary if st.column_index(months, f.period_end) is not None]
            if not sheets:
                _fail(ds, metric, label, "no filed statement covering this period was found to check against")
                continue
            hits = [(st.title, r.label) for st in primary + fetch_notes(cik, accn) for r in st.rows
                    if r.tag in tags or pattern.search(r.label)]
            if hits:
                _fail(ds, metric, label, f"the filing shows {hits[0][1]!r} on {hits[0][0][:60]!r}")
                continue
            st = sheets[0]
            src = Source(accession=accn, form="10-K" if label.startswith("FY") else "10-Q",
                         filed=ds.filing_dates.get(accn, f.period_end), url=st.url,
                         locator=f"absent from {st.title.split(' - ')[0]} and note details",
                         snapshot_id=st.snapshot_id, retrieved_at="")
            ds.facts[key] = f.model_copy(update={
                "value": 0.0, "status": FactStatus.DERIVED, "sources": [src],
                "formula": f"0: not presented (no XBRL fact; no line matching the mapped tags or "
                           f"/{rule['absent_label_pattern']}/ in {accn})",
                "notes": f.notes + [rule["rationale"]]})
            ds.review[:] = [i for i in ds.review if not (i.kind == "missing" and i.metric == metric and i.fiscal_label == label)]
            ds.review.append(ReviewItem(severity="info", metric=metric, fiscal_label=label, kind="zero-attested",
                                        message=f"{METRICS[metric].label} {label}: verified not presented; set to 0"))
    return ds


def _fail(ds: Dataset, metric: str, label: str, why: str) -> None:
    ds.review.append(ReviewItem(severity="block", metric=metric, fiscal_label=label, kind="attestation-failed",
                                message=f"{METRICS[metric].label} {label}: cannot attest zero, {why}"))
