"""One call from ticker to a complete, reproducible research run."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import attest, ledger
from .eps_bridge import bridge
from .fundamentals import compute
from .normalize import Dataset
from .pipeline import ROOT, companies, load
from .reconcile import ReconRecord, reconcile
from .statements import note_details, primary_statements
from .verify import verify_ledger

ENGINE_VERSION = "0.1.0"


@dataclass
class Run:
    ticker: str
    reported: Dataset
    adjusted: Dataset  # approved adjustments only
    what_if: Dataset  # every proposed adjustment applied: a preview, never the default
    reconciliation: list[ReconRecord]
    adjustments: list
    observations: list[dict]
    ledger_problems: list[str]
    eps_bridge: list[dict]
    eps_bridge_what_if: list[dict]
    config: dict
    latest: Dataset | None = None  # YTD / prior YTD / TTM / balance sheet after the last 10-K
    latest_labels: dict = field(default_factory=dict)
    latest_reconciliation: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat())

    @property
    def blocking(self) -> list:
        extra = self.latest.review if self.latest is not None else []
        return [i for i in self.reported.review + extra if i.severity == "block"]


def default_years(ticker: str, n: int = 5) -> list[int]:
    """The last n fiscal years for which the pinned data holds a 10-K."""
    from . import snapshot
    from .pipeline import lock

    from .normalize import annual_accessions

    ids = lock()[ticker]
    fye = snapshot.load(ids["submissions"])["fiscalYearEnd"]
    return sorted(annual_accessions(snapshot.load(ids["companyfacts"]), fye))[-n:]


def build(ticker: str, years: list[int] | None = None, *, check_notes: bool = True,
          snapshot_ids: dict[str, str] | None = None) -> Run:
    years = years or default_years(ticker)
    ds = load(ticker, years, snapshot_ids)
    attest.apply_zero_attestations(ds, attest.load_rules(ticker))
    recon = reconcile(ds, fetch=primary_statements, fetch_notes=note_details if check_notes else None)
    compute(ds)
    adjustments, observations = ledger.load(ds, ticker)
    problems = verify_ledger(ds, ticker)
    adjusted = compute(ledger.apply(ds, adjustments))
    what_if = compute(ledger.apply(ds, adjustments, statuses=("approved", "proposed")))
    from . import snapshot
    from .latest import build_latest
    latest, latest_recon, latest_labels = build_latest(
        ds, snapshot.load(ds.snapshot_ids["companyfacts"]), snapshot.load(ds.snapshot_ids["submissions"]),
        primary_statements, note_details if check_notes else None)
    return Run(latest=latest, latest_labels=latest_labels, latest_reconciliation=latest_recon,
               ticker=ticker, reported=ds, adjusted=adjusted, what_if=what_if, reconciliation=recon,
               adjustments=adjustments, observations=observations, ledger_problems=problems,
               eps_bridge=bridge(ds), eps_bridge_what_if=bridge(what_if),
               config={"ticker": ticker, "fiscal_years": years, "check_notes": check_notes,
                       "company_config": companies()[ticker], "engine_version": ENGINE_VERSION})


def code_version() -> dict:
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", "src", "config", "reviews"))}


def outputs_digest(payload: dict) -> str:
    """Hash of every number the run produced. Same inputs + same code => same digest."""
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
