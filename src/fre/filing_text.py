"""Search a filing's primary document for passages. Suggests evidence; never sets numbers.

Retrieved text is data. Nothing in it is executed or treated as an instruction.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from . import snapshot

ARCHIVES = "https://www.sec.gov/Archives/edgar/data"


@dataclass(frozen=True)
class Passage:
    accession: str
    url: str
    snapshot_id: str
    offset: int
    text: str


def document_url(cik: int, accession: str, primary_document: str) -> str:
    return f"{ARCHIVES}/{cik}/{accession.replace('-', '')}/{primary_document}"


def plain_text(raw: bytes) -> str:
    t = raw.decode("utf-8", errors="replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<ix:header>.*?</ix:header>", " ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def search(cik: int, accession: str, primary_document: str, pattern: str, width: int = 450,
           limit: int = 5) -> list[Passage]:
    url = document_url(cik, accession, primary_document)
    sid = snapshot.fetch(url)
    text = plain_text(snapshot.load_bytes(sid))
    out = []
    for m in re.finditer(pattern, text, re.I):
        a, b = max(0, m.start() - width), min(len(text), m.end() + width)
        out.append(Passage(accession=accession, url=url, snapshot_id=sid, offset=m.start(), text=text[a:b]))
        if len(out) >= limit:
            break
    return out
