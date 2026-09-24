"""fre: fundamentals research engine command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import ROOT


def _cmd_refresh(a):
    from .pipeline import refresh
    print(json.dumps(refresh(a.ticker), indent=2))


def _cmd_dossier(a):
    from . import compare, dossier
    from .engine import build

    run = build(a.ticker, a.years, check_notes=not a.no_notes)
    peers = [build(p, None, check_notes=not a.no_notes) for p in a.peers]
    out = dossier.write(run, Path(a.out), compare.markdown(run, peers))
    for p in peers:
        dossier.write(p, Path(a.out))
    print(f"wrote {out}")
    print(f"blocking review items: {len(run.blocking)}; ledger problems: {len(run.ledger_problems)}")
    return 1 if (a.strict and (run.blocking or run.ledger_problems)) else 0


def _cmd_verify_run(a):
    from .dossier import payload
    from .engine import build

    saved = json.loads(Path(a.run_json).read_text())
    cfg = saved["run"]["config"]
    run = build(cfg["ticker"], cfg["fiscal_years"], check_notes=cfg["check_notes"],
                snapshot_ids=saved["inputs"]["snapshot_ids"])
    again = payload(run)["outputs_digest"]
    ok = again == saved["outputs_digest"]
    print(f"saved   {saved['outputs_digest']}\nrebuilt {again}\n{'IDENTICAL' if ok else 'DIFFERENT'}")
    return 0 if ok else 1


def _cmd_verify_ledger(a):
    from .engine import default_years
    from .pipeline import load
    from .verify import verify_ledger

    problems = verify_ledger(load(a.ticker, default_years(a.ticker)), a.ticker)
    print("\n".join(problems) or "all ledger quotes verified against filing text")
    return 1 if problems else 0


def _cmd_review(a):
    from .engine import build

    run = build(a.ticker, a.years, check_notes=not a.no_notes)
    for i in sorted(run.reported.review, key=lambda i: ("block", "warn", "info").index(i.severity)):
        if a.all or i.severity != "info":
            print(f"{i.severity:5s} {i.kind:20s} {i.message}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="fre", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("refresh", help="download fresh SEC data and pin it (needs SEC_USER_AGENT)")
    s.add_argument("ticker")
    s.set_defaults(fn=_cmd_refresh)

    s = sub.add_parser("dossier", help="build a run and export dossier.md, tables/*.csv, run.json")
    s.add_argument("ticker")
    s.add_argument("--peers", nargs="*", default=[])
    s.add_argument("--years", nargs="*", type=int)
    s.add_argument("--out", default=str(ROOT / "out"))
    s.add_argument("--no-notes", action="store_true", help="skip note-table verification (faster, offline-only if cached)")
    s.add_argument("--strict", action="store_true", help="exit 1 when blocking review items remain")
    s.set_defaults(fn=_cmd_dossier)

    s = sub.add_parser("verify-run", help="rebuild a saved run from its pinned inputs and compare digests")
    s.add_argument("run_json")
    s.set_defaults(fn=_cmd_verify_run)

    s = sub.add_parser("verify-ledger", help="check every ledger quote against the filing text")
    s.add_argument("ticker")
    s.set_defaults(fn=_cmd_verify_ledger)

    s = sub.add_parser("review", help="print the review queue")
    s.add_argument("ticker")
    s.add_argument("--years", nargs="*", type=int)
    s.add_argument("--all", action="store_true")
    s.add_argument("--no-notes", action="store_true")
    s.set_defaults(fn=_cmd_review)

    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
