"""Load a supported company from immutable snapshots and build its reviewed dataset."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml

from . import snapshot
from .normalize import CorporateAction, Dataset, normalize

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "companies.yaml"
LOCK = ROOT / "data" / "snapshots" / "lock.json"


def companies() -> dict:
    return yaml.safe_load(CONFIG.read_text())


def actions_for(ticker: str) -> list[CorporateAction]:
    out = []
    for a in companies()[ticker].get("corporate_actions") or []:
        eff = a["effective"] if isinstance(a["effective"], date) else date.fromisoformat(a["effective"])
        out.append(CorporateAction(kind=a["kind"], ratio=float(a["ratio"]), effective=eff, source=a["source"].strip()))
    return out


def lock() -> dict:
    return json.loads(LOCK.read_text()) if LOCK.exists() else {}


def refresh(ticker: str) -> dict[str, str]:
    """Download fresh SEC data and pin it. Only this function touches the network."""
    ids = snapshot.fetch_company(companies()[ticker]["cik"])
    pins = lock()
    pins[ticker] = ids
    LOCK.write_text(json.dumps(pins, indent=2, sort_keys=True))
    return ids


def load(ticker: str, fiscal_years: list[int]) -> Dataset:
    ids = lock()[ticker]
    cf, subs = snapshot.load(ids["companyfacts"]), snapshot.load(ids["submissions"])
    return normalize(cf, subs, snapshot_ids=ids, retrieved_at=snapshot.info(ids["companyfacts"])["retrieved_at"],
                     actions=actions_for(ticker), fiscal_years=fiscal_years)
