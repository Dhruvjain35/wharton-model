"""Read the financial statements exactly as SEC renders them from a filing (R pages).

This is the independent path the reconciliation gate uses. Company Facts gives
values by tag; the R pages show which tag sits on which line of the actual
statement, with the company's own label and presentation scale. A normalized fact
is trusted only when it matches the line on the statement it claims to come from.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import date, datetime

from . import snapshot

ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
PRIMARY = ("BALANCE SHEETS", "STATEMENTS OF INCOME", "STATEMENTS OF OPERATIONS", "INCOME STATEMENTS",
           "STATEMENTS OF CASH FLOWS", "CASH FLOWS STATEMENTS", "STOCKHOLDERS' EQUITY", "STOCKHOLDERS’ EQUITY",
           "SHAREHOLDERS' EQUITY", "SHAREHOLDERS’ EQUITY")


@dataclass(frozen=True)
class Column:
    months: int | None  # None for balance-sheet instants
    end: date


@dataclass(frozen=True)
class Row:
    label: str
    tag: str  # "us-gaap:Revenues"
    unit: str
    values: list[float | None]


@dataclass
class Statement:
    title: str
    columns: list[Column]
    rows: list[Row] = field(default_factory=list)
    url: str = ""
    snapshot_id: str = ""

    def rows_for(self, tag: str) -> list[Row]:
        return [r for r in self.rows if r.tag == tag]

    def column_index(self, months: int | None, end: date) -> int | None:
        for i, c in enumerate(self.columns):
            if c.end == end and c.months == months:
                return i
        return None


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _cells(tr: str) -> list[tuple[str, int]]:
    out = []
    for m in re.finditer(r"<t([hd])([^>]*)>(.*?)</t\1>", tr, re.S):
        span = re.search(r'colspan="(\d+)"', m.group(2))
        out.append((_text(m.group(3)), int(span.group(1)) if span else 1))
    return out


def _date(s: str) -> date | None:
    s = s.replace(".", "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def _scale(title: str, what: str) -> float:
    m = re.search(rf"{re.escape(what)} in (Thousands|Millions|Billions)", title)
    return {"Thousands": 1e3, "Millions": 1e6, "Billions": 1e9}[m.group(1)] if m else 1.0


def _number(s: str) -> float | None:
    s = re.sub(r"\[\d+\]", "", s).replace("$", "").replace(",", "").strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").strip()
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def parse_r_page(raw: bytes) -> Statement:
    t = raw.decode("utf-8", errors="replace")
    trs = re.findall(r"<tr[^>]*>.*?</tr>", t, re.S)
    head = _cells(trs[0])
    title = head[0][0]
    usd_scale, share_scale = _scale(title, "$"), _scale(title, "shares")

    # Header: either dates directly, or duration groups ("12 Months Ended") over a date row.
    groups = head[1:]
    columns: list[Column] = []
    if groups and all(_date(g) for g, _ in groups):
        columns = [Column(None, _date(g)) for g, _ in groups]
        body = trs[1:]
    else:
        dates = [_date(c) for c, _ in _cells(trs[1])]
        spans = []
        for g, span in groups:
            m = re.match(r"(\d+) Months Ended", g)
            spans += [int(m.group(1)) if m else None] * span
        columns = [Column(months, d) for months, d in zip(spans, dates) if d]
        body = trs[2:]

    st = Statement(title=title, columns=columns)
    for tr in body:
        if 'class="r' not in tr[:40]:
            continue
        tag = re.search(r"defref_([a-z0-9-]+)_(\w+)", tr)
        cells = _cells(tr)
        if not tag or len(cells) < 2:
            continue
        label = cells[0][0]
        if "per share" in label or "$ / shares" in label:
            unit, scale = "USD/shares", 1.0
        elif "(in shares)" in label:
            unit, scale = "shares", share_scale
        else:
            unit, scale = "USD", usd_scale
        vals = [_number(c) for c, _ in cells[1:1 + len(columns)]]
        vals = [None if v is None else v * scale for v in vals]
        if any(v is not None for v in vals):
            st.rows.append(Row(label=label, tag=f"{tag.group(1)}:{tag.group(2)}", unit=unit, values=vals))
    return st


def primary_statements(cik: int, accession: str) -> list[Statement]:
    """Fetch (or reuse snapshots of) the balance sheet, income statement and cash flow."""
    folder = f"{ARCHIVES}/{cik}/{accession.replace('-', '')}"
    summary = snapshot.load_bytes(snapshot.fetch(f"{folder}/FilingSummary.xml")).decode("utf-8", "replace")
    out = []
    for rep in re.findall(r"<Report instance=.*?</Report>", summary, re.S):
        name = re.search(r"<ShortName>(.*?)</ShortName>", rep, re.S)
        fname = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", rep, re.S)
        cat = re.search(r"<MenuCategory>(.*?)</MenuCategory>", rep, re.S)
        if not (name and fname and cat) or cat.group(1) != "Statements":
            continue
        short = html.unescape(name.group(1)).upper()
        if "PARENTHETICAL" in short or not any(k in short for k in PRIMARY):
            continue
        url = f"{folder}/{fname.group(1)}"
        sid = snapshot.fetch(url)
        st = parse_r_page(snapshot.load_bytes(sid))
        st.url, st.snapshot_id = url, sid
        out.append(st)
    return out
