"""Snapshot store: content-addressed, tamper-evident, and never caches a rejected response."""

import gzip

import pytest

from fre import snapshot


@pytest.fixture
def store_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(snapshot, "SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr(snapshot, "MANIFEST", tmp_path / "manifest.json")
    return tmp_path


def test_store_is_content_addressed_and_round_trips(store_dir):
    sid = snapshot.store(b'{"a": 1}', "u")
    assert snapshot.load(sid) == {"a": 1}
    assert snapshot.store(b'{"a": 1}', "u") == sid


def test_tampered_snapshot_is_detected(store_dir):
    sid = snapshot.store(b'{"a": 1}', "u")
    (store_dir / f"{sid}.gz").write_bytes(gzip.compress(b'{"a": 2}'))
    with pytest.raises(ValueError, match="modified"):
        snapshot.load(sid)


def test_rejected_response_is_not_stored(store_dir, monkeypatch):
    class Resp:
        content = b'{"data": {"totalRecords": 0}}'
        def raise_for_status(self):
            pass
    import requests
    monkeypatch.setattr(requests, "get", lambda *a, **k: Resp())
    monkeypatch.setattr(snapshot.time, "sleep", lambda s: None)
    with pytest.raises(LookupError):
        snapshot.fetch("https://example.test/prices", headers={"User-Agent": "t"}, accept=lambda raw: False)
    assert not list(store_dir.glob("*.gz"))
