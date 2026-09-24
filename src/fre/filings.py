"""Filing-level metadata: EDGAR acceptance timestamps, read from each filing's index page (snapshotted)."""

from __future__ import annotations

import re

from . import snapshot
from .normalize import Dataset

ARCHIVES = "https://www.sec.gov/Archives/edgar/data"


def accepted_at(cik: int, accession: str) -> str | None:
    url = f"{ARCHIVES}/{cik}/{accession.replace('-', '')}/{accession}-index.htm"
    raw = snapshot.load_bytes(snapshot.fetch(url)).decode("utf-8", "replace")
    m = re.search(r'infoHead">Accepted</div>\s*<div class="info">([^<]+)</div>', raw)
    return m.group(1).strip() if m else None


def enrich(ds: Dataset, fetch=accepted_at) -> Dataset:
    """Stamp every source with its acceptance time and every fact with its currency."""
    cik = int(ds.company.cik)
    cache: dict[str, str | None] = {}
    for key, f in list(ds.facts.items()):
        srcs = []
        for s in f.sources:
            if s.accession and s.accession not in cache:
                cache[s.accession] = fetch(cik, s.accession)
            srcs.append(s.model_copy(update={"accepted": cache.get(s.accession)}))
        ds.facts[key] = f.model_copy(update={"sources": srcs, "currency": "USD" if "USD" in f.unit else None})
    return ds
