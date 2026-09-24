"""Immutable raw-source snapshots.

Every download is stored gzipped under data/snapshots/<id>.gz where <id> is the
first 16 hex chars of the sha256 of the raw bytes. The manifest records the URL and
retrieval time. A model run lists the snapshot ids it read, so identical inputs
provably produce identical outputs.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
MANIFEST = SNAPSHOT_DIR / "manifest.json"

SEC_BASE = "https://data.sec.gov"


def _user_agent() -> str:
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise RuntimeError(
            "SEC requires a contact User-Agent. Set SEC_USER_AGENT, e.g. "
            "'team-name research you@example.com'. It is kept out of source on purpose."
        )
    return ua


def _load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {}


def store(raw: bytes, url: str, retrieved_at: str | None = None) -> str:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    sid = hashlib.sha256(raw).hexdigest()[:16]
    path = SNAPSHOT_DIR / f"{sid}.gz"
    if not path.exists():
        # mtime=0 keeps the gzip bytes themselves deterministic
        path.write_bytes(gzip.compress(raw, mtime=0))
    manifest = _load_manifest()
    manifest.setdefault(sid, {"url": url, "retrieved_at": retrieved_at or _now(), "bytes": len(raw)})
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return sid


def load_bytes(sid: str) -> bytes:
    raw = gzip.decompress((SNAPSHOT_DIR / f"{sid}.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest()[:16] != sid:
        raise ValueError(f"snapshot {sid} does not match its hash; it was modified")
    return raw


def load(sid: str) -> dict:
    return json.loads(load_bytes(sid))


def info(sid: str) -> dict:
    return _load_manifest()[sid]


def fetch(url: str) -> str:
    """Download once; a URL already in the manifest is served from its snapshot."""
    import requests

    for sid, meta in _load_manifest().items():
        if meta["url"] == url and (SNAPSHOT_DIR / f"{sid}.gz").exists() and not url.startswith(SEC_BASE):
            return sid  # filing archives are immutable; only the live company APIs are re-downloaded

    resp = requests.get(url, headers={"User-Agent": _user_agent()}, timeout=60)
    resp.raise_for_status()
    time.sleep(0.15)  # stay well under SEC's 10 requests/second fair-access limit
    return store(resp.content, url)


def fetch_company(cik: str) -> dict[str, str]:
    cik10 = cik.zfill(10)
    return {
        "companyfacts": fetch(f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik10}.json"),
        "submissions": fetch(f"{SEC_BASE}/submissions/CIK{cik10}.json"),
    }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
