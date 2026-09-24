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


def _has_rows(raw: bytes) -> bool:
    try:
        return bool((json.loads(raw)["data"] or {}).get("tradesTable", {}).get("rows"))
    except (ValueError, KeyError, TypeError, AttributeError):
        return False


def closes(symbol: str, start: date, force: bool = False) -> list[Quote]:
    # Nasdaq ignores or empties `todate` for past windows; `fromdate` alone returns through today.
    url = f"https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=stocks&fromdate={start}&limit=400"
    sid = snapshot.fetch(url, headers=BROWSER, accept=_has_rows, force=force)
    rows = json.loads(snapshot.load_bytes(sid))["data"]["tradesTable"]["rows"]
    out = [Quote(symbol=symbol, date=datetime.strptime(r["date"], "%m/%d/%Y").date(),
                 close=float(r["close"].replace("$", "").replace(",", "")), source_url=url, snapshot_id=sid)
           for r in rows]
    return sorted(out, key=lambda q: q.date)


def close_on_or_before(symbol: str, on: date, lookback_days: int = 10) -> Quote:
    from datetime import timedelta

    start = on - timedelta(days=lookback_days)
    qs = closes(symbol, start)
    if qs and qs[-1].date < on:  # the stored snapshot predates the date asked for
        qs = closes(symbol, start, force=True)
    qs = [q for q in qs if q.date <= on]
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
    sid = snapshot.fetch(url, headers={"User-Agent": "curl/8.7.1"},  # FRED drops unrecognized agents
                         accept=lambda raw: raw.startswith(b"observation_date"))
    rows = list(csv.reader(io.StringIO(snapshot.load_bytes(sid).decode())))[1:]
    vals = [(date.fromisoformat(d), float(v)) for d, v in rows if v not in ("", ".")]
    vals = [x for x in vals if x[0] <= on]
    if not vals:
        raise LookupError(f"no {series} observation within {lookback_days} days before {on}")
    d, v = vals[-1]
    return Rate(series=series, date=d, value=v / 100, source_url=url, snapshot_id=sid)
