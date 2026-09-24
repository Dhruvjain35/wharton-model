"""Check every quote in a ledger against the snapshotted filing text."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from . import snapshot
from .filing_text import plain_text
from .ledger import ROOT, verify_quotes
from .normalize import Dataset


@lru_cache(maxsize=None)
def _text(sid: str) -> str:
    return plain_text(snapshot.load_bytes(sid))


def verify_ledger(ds: Dataset, ticker: str) -> list[str]:
    path: Path = ROOT / "reviews" / ticker / "adjustments.yaml"
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text()) or {}
    entries = [e for e in (doc.get("adjustments") or []) if e["fiscal_label"] in ds.labels]
    for o in doc.get("observations") or []:
        entries.append({"id": o["id"], "fiscal_label": o["fiscal_labels"][0],
                        "evidence": {"snapshot_id": o["snapshot_id"], "quote": o["quote"]}})
    return verify_quotes(entries, _text, ds)


def verify_comparability(config: dict, text_for=_text) -> list[str]:
    """Every comparability quote must appear verbatim in its snapshotted filing."""
    problems = []
    for ticker, c in (config.get("comparability") or {}).items():
        for q in c.get("quotes", []):
            if " ".join(q["quote"].split()) not in " ".join(text_for(q["snapshot_id"]).split()):
                problems.append(f"comparability {ticker}: quote not found verbatim in snapshot {q['snapshot_id']}")
    return problems
