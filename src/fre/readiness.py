"""What still stands between this run and a submission the team can defend (PRD sections 11 and 14).

Phase A is done when every figure is traceable; Phase B is done when the team can defend the
assumptions. The engine cannot do the defending, so this lists the human work that remains.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def check(*, adjustments: list[dict], assumptions: dict, scenarios: dict, thesis: dict, open_warnings: int,
          unverified: int, comparability: dict) -> list[dict]:
    out = []

    def item(ok: bool, text: str) -> None:
        out.append({"status": "OK" if ok else "TODO", "item": text})

    pending = [a["id"] for a in adjustments if a["status"] == "proposed"]
    item(not pending, f"Approve or reject each accounting adjustment ({len(pending)} still proposed)")
    unsourced = [k for k, a in assumptions.items() if "TEAM INPUT REQUIRED" in str(a.get("rationale", ""))]
    item(not unsourced, "Replace placeholder inputs with cited figures: " + (", ".join(unsourced) or "none"))
    unapproved = [k for k, a in assumptions.items() if a.get("status") != "approved"]
    item(not unapproved, f"Approve every valuation assumption ({len(unapproved)} not approved)")
    unapproved_sc = [k for k, s in scenarios.items() if s.get("status") != "approved"]
    item(not unapproved_sc, f"Approve every scenario ({len(unapproved_sc)} not approved)")
    for field_, what in (("claim", "Write the thesis claim"), ("direction", "State the thesis direction"),
                         ("owner", "Name the thesis owner")):
        item(bool(thesis.get(field_)), what)
    item(bool(thesis.get("counterevidence")), "List counterevidence to the thesis")
    item(bool(thesis.get("invalidation")), "List observable invalidation conditions")
    item(bool(thesis.get("decision_history")), "Record at least one dated decision, ideally where evidence changed the view")
    item(open_warnings == 0, f"Resolve open review warnings ({open_warnings})")
    item(unverified == 0, f"Check unverified facts by hand ({unverified} not matched to a filed statement, table or text)")
    for t, c in comparability.items():
        item("Team to confirm" not in c.get("note", ""), f"Confirm the {t} comparability note")
    return out


def for_ticker(root: Path, ticker: str, run) -> list[dict]:
    from .pipeline import config

    rev = root / "reviews" / ticker
    adj = yaml.safe_load((rev / "adjustments.yaml").read_text()) if (rev / "adjustments.yaml").exists() else {}
    val = yaml.safe_load((rev / "valuation.yaml").read_text()) if (rev / "valuation.yaml").exists() else {}
    thesis = yaml.safe_load((rev / "thesis.yaml").read_text()) if (rev / "thesis.yaml").exists() else {}
    unverified = sum(r.outcome == "from-notes" for r in run.reconciliation + run.latest_reconciliation)
    warnings = sum(i.severity == "warn" for i in run.reported.review)
    return check(adjustments=adj.get("adjustments") or [], assumptions=val.get("assumptions") or {},
                 scenarios=val.get("scenarios") or {}, thesis=thesis or {}, open_warnings=warnings,
                 unverified=unverified, comparability=config().get("comparability") or {})
