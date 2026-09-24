"""Readiness: what a human still has to do before the model supports a submission (PRD section 14)."""

from fre.readiness import check


def test_everything_proposed_and_an_empty_thesis_are_todos():
    items = check(adjustments=[{"id": "A", "status": "proposed"}],
                  assumptions={"beta": {"status": "proposed", "rationale": "TEAM INPUT REQUIRED."}},
                  scenarios={}, thesis={"claim": None, "invalidation": [], "decision_history": []},
                  open_warnings=3, unverified=2, comparability={"MSFT": {"note": "Team to confirm: x"}})
    todo = [i for i in items if i["status"] == "TODO"]
    text = " ".join(i["item"] for i in todo)
    for word in ("adjustment", "beta", "claim", "invalidation", "warnings", "unverified", "MSFT"):
        assert word in text


def test_all_done_is_ready():
    items = check(adjustments=[{"id": "A", "status": "approved"}],
                  assumptions={"beta": {"status": "approved", "rationale": "regression beta, source X"}},
                  scenarios={"adverse": {"status": "approved"}},
                  thesis={"claim": "c", "direction": "long", "owner": "Priya", "counterevidence": ["x"],
                          "invalidation": ["y"], "decision_history": [{"date": "2026-09-29", "change": "z"}]},
                  open_warnings=0, unverified=0, comparability={"MSFT": {"note": "reviewed"}})
    assert all(i["status"] == "OK" for i in items)
