"""Market inputs with the same provenance discipline as filings.

Prices come from Nasdaq's historical quote endpoint and the risk-free rate from FRED.
Both are snapshotted with URL and retrieval time; the URL pins the date range, so a
snapshot never silently changes. A price is always stored with its own date, which
is recorded separately from the financial-statement date (PRD section 8).
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import date, datetime

from .. import snapshot

BROWSER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/126.0 Safari/537.36", "Accept": "application/json"}


@dataclass(frozen=True)
class Quote:
    symbol: str
    date: date
    close: float
    source_url: str
    snapshot_id: str


def closes(symbol: str, start: date, end: date) -> list[Quote]:
    url = (f"https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=stocks"
           f"&fromdate={start}&todate={end}&limit=400")
    sid = snapshot.fetch(url, headers=BROWSER)
    rows = (json.loads(snapshot.load_bytes(sid))["data"] or {}).get("tradesTable", {}).get("rows") or []
    out = [Quote(symbol=symbol, date=datetime.strptime(r["date"], "%m/%d/%Y").date(),
                 close=float(r["close"].replace("$", "").replace(",", "")), source_url=url, snapshot_id=sid)
           for r in rows]
    return sorted(out, key=lambda q: q.date)


def close_on_or_before(symbol: str, on: date, lookback_days: int = 10) -> Quote:
    from datetime import timedelta

    qs = [q for q in closes(symbol, on - timedelta(days=lookback_days), on) if q.date <= on]
    if not qs:
        raise LookupError(f"no {symbol} close within {lookback_days} days before {on}")
    return qs[-1]


@dataclass(frozen=True)
class Rate:
    series: str
    date: date
    value: float  # decimal, 0.0496 for 4.96%
    source_url: str
    snapshot_id: str


def fred_on_or_before(series: str, on: date, lookback_days: int = 10) -> Rate:
    from datetime import timedelta

    start = on - timedelta(days=lookback_days)
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}&coed={on}"
    sid = snapshot.fetch(url, headers={"User-Agent": "curl/8.7.1"})  # FRED drops unrecognized agents
    rows = list(csv.reader(io.StringIO(snapshot.load_bytes(sid).decode())))[1:]
    vals = [(date.fromisoformat(d), float(v)) for d, v in rows if v not in ("", ".")]
    vals = [x for x in vals if x[0] <= on]
    if not vals:
        raise LookupError(f"no {series} observation within {lookback_days} days before {on}")
    d, v = vals[-1]
    return Rate(series=series, date=d, value=v / 100, source_url=url, snapshot_id=sid)
