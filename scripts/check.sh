#!/usr/bin/env bash
# Every gate, in order. Exit non-zero if any fails.
# Works offline from data/snapshots; SEC_USER_AGENT is needed only if a snapshot is missing.
set -euo pipefail
cd "$(dirname "$0")/.."
FRE=.venv/bin/fre
PRICE_DATE=2026-09-23
echo "== tests";                 .venv/bin/python -m pytest -q
echo "== quotes (ledger, comparability)"; $FRE verify-ledger GOOGL
echo "== dossier";               $FRE dossier GOOGL --peers MSFT META --price-date "$PRICE_DATE" --strict
run=$(ls -td out/GOOGL/*/ | grep -v valuation | head -1)
echo "== dossier reproducibility"; $FRE verify-run "${run}run.json"
echo "== valuation";             $FRE value GOOGL
echo "== valuation reproducibility"; $FRE verify-value out/GOOGL/valuation/valuation.json
echo "== review screen";         $FRE screen GOOGL
echo "all gates passed  (run \`fre readiness GOOGL\` for the human work left before submission)"
