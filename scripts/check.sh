#!/usr/bin/env bash
# Every gate, in order. Exit non-zero if any fails. Needs SEC_USER_AGENT only if a snapshot is missing.
set -euo pipefail
cd "$(dirname "$0")/.."
FRE=.venv/bin/fre
echo "== tests";            .venv/bin/python -m pytest -q
echo "== ledger quotes";    $FRE verify-ledger GOOGL
echo "== dossier";          $FRE dossier GOOGL --peers MSFT META --strict
run=$(ls -td out/GOOGL/*/ | grep -v valuation | head -1)
echo "== reproducibility";  $FRE verify-run "${run}run.json"
echo "== valuation";        $FRE value GOOGL
echo "== review screen";    $FRE screen GOOGL
echo "all gates passed"
