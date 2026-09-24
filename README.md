# Fundamentals Research Engine

A company research model where every number can be traced to the line of the SEC filing it came from, every calculation is deterministic Python, and every judgment is written down with a range, an owner and a reason.

Built for the Wharton Global High School Investment Competition from the team PRD (`Wharton_Fundamentals_Model_PRD.md`). Alphabet is the pilot; Microsoft and Meta are the peers.

**Latest outputs:** [`reports/GOOGL/dossier.md`](reports/GOOGL/dossier.md) · [`reports/GOOGL/valuation.md`](reports/GOOGL/valuation.md) · [`reports/GOOGL/review.html`](reports/GOOGL/review.html) (download and open; it works offline)

## Quick start

```bash
uv sync                                              # Python 3.12, pinned dependencies
export SEC_USER_AGENT="team-name research you@example.com"   # SEC requires a contact; only needed to download
scripts/check.sh                                     # every gate: tests, ledger quotes, dossier, reproducibility, valuation, review screen
```

| Command | What it does |
|---|---|
| `fre dossier GOOGL --peers MSFT META --price-date 2026-09-23` | Fundamentals dossier (`dossier.md`, `tables/*.csv`, `run.json`) with peers and dated market multiples |
| `fre dossier GOOGL --as-of 2024-03-01` | Point-in-time run: only filings made on or before that date (no later restatements) |
| `fre dossier GOOGL --no-adjustments` | Every ledger adjustment switched off |
| `fre verify-run out/GOOGL/<run>/run.json` | Rebuilds the run from its pinned inputs and proves the output digest is identical |
| `fre value GOOGL` | Runs `reviews/GOOGL/valuation.yaml`: DCF, scenarios, reverse DCF, grids, multiples cross-check |
| `fre verify-value out/GOOGL/valuation/valuation.json` | Same reproducibility proof for the valuation |
| `fre readiness GOOGL` | Lists the human work left before the model supports a submission (exits 1 until done) |
| `fre screen GOOGL` | Writes `review.html`: charts plus click-through provenance for every figure |
| `fre verify-ledger GOOGL` | Checks every ledger and peer-comparability quote against the filing text |
| `fre review GOOGL` | Prints the open review queue |
| `fre refresh GOOGL` | Downloads fresh SEC data and pins it (the only command that changes inputs) |

Adding a company: add it to `config/companies.yaml` (CIK, and any stock split with the filing that proves it), run `fre refresh TICKER`, then `fre dossier TICKER`.

## How "no hallucinations" is enforced

Nothing here relies on being careful. Each rule is code, and each has tests written to fail when the rule is removed (the suite is mutation-checked: deleting a guard turns it red).

1. **Every number is a Fact** with its filing accession, XBRL tag, period, snapshot id and status: `reported`, `derived`, `analyst-adjusted`, `missing` or `conflicting`. **Missing is never zero.** A ratio with a missing or meaningless input is suppressed with its reason.
2. **Immutable inputs.** Every download (SEC Company Facts, filed statements, filing text, prices, Treasury yields) is stored content-addressed in `data/snapshots/`. A run lists the snapshots it read; `fre verify-run` rebuilds it and compares a digest of every output number.
3. **Reconciliation gate.** Each reported fact, annual and quarterly, is checked in tiers: (1) the line of the filed financial statement it came from, at the statement's own precision; (2) the filing's note tables and parenthetical pages; (3) the printed figure next to the metric's own keyword in the filing text, with the snippet kept. A mismatch **withholds** the fact (both values visible) so it cannot feed any calculation; anything still unverified is listed by `fre readiness`.
4. **Filing vintages are explicit.** The latest filing's restated value is used; older values stay visible with the reason (stock split, rounding, or "unexplained" for a teammate to check). Alphabet's 2022 20-for-1 split is applied only where a filing predates it, and the split itself is cited to the 10-K.
5. **Quotes are verified.** Any number taken from filing prose (a legal charge, a coupon rate, preferred stock terms) carries a verbatim quote that must appear in the snapshotted filing text and must contain that number.
6. **Humans own judgment.** Accounting adjustments and forecast assumptions are proposed by the AI and applied only after a named teammate approves them. The engine refuses an approval by the author or by an AI.
7. **Independently audited.** Two separate reviews of this repo: one checked every PRD clause, one recomputed every figure from the raw SEC data with its own code (no arithmetic errors found; its findings on wording and latent bugs were fixed with regression tests).
8. **Zero is proven, not assumed.** A component the company does not have (for example no commercial paper) becomes 0 only when the engine confirms that no XBRL fact, statement line or note table shows it.

## What is in the model

**Phase A: fundamentals** (PRD section 4)
- Five annual periods plus the latest year-to-date and trailing twelve months (TTM = fiscal year + YTD − prior YTD; quarters are never summed; balance-sheet values are never summed)
- The PRD's A2 metric dictionary: growth, margins, EPS, share change, cash conversion, cash FCF, capex and SBC intensity, net debt, and more, each with its formula and inputs
- EPS bridge: EPS growth split exactly (on a log basis) into earnings, share count and a reported residual; buybacks shown next to their cash cost and SBC
- Accounting review ledger (`reviews/GOOGL/adjustments.yaml`) with an adjusted view that can be switched off, plus a preview of "if every proposal were approved"
- Latest period after the last 10-K: YTD vs prior YTD, the latest standalone quarter, TTM, and the balance sheet, all reconciled to the 10-Q
- ROIC with a proposed, labelled definition (PRD A2 optional)
- Peers: five-year history for each company with period ends, comparability notes written from each 10-K with verified quotes, and market multiples (P/E, EV/EBIT, FCF yield) that count every share class at its own listed price. There is no composite score.

**Phase B: valuation** (PRD section 5)
- FCFF DCF implementing the B2 calculation contract; hand-calculated test fixture; levered cash flow kept separate from FCFF; no tax refunds on losses; partial first year handled
- Equity bridge at the latest 10-Q balance sheet: cash and marketable securities, non-marketable securities, debt including finance leases, the 2026 mandatory convertible preferred, and diluted shares including unvested RSUs
- WACC calculated from sourced parts; equity risk premium and beta are **team inputs** (PRD B4 forbids estimating them automatically)
- Controls: terminal growth vs the risk-free rate, growth and reinvestment jumps into perpetuity, implied EBITDA-margin expansion, terminal value share of EV, the exit multiple the perpetuity implies
- Base, adverse, favorable and flat-EBITDA-margin scenarios; reverse DCF (bracketed root finding that reports "no solution" or "multiple solutions" rather than forcing one); growth × margin and WACC × terminal-growth grids; a capex break-even; a haircut on the holdings that carry the disputed gains

## Policies (change them deliberately, in one place)

| Topic | Policy | Where |
|---|---|---|
| Debt | Notes at carrying value + finance leases + commercial paper, every year; operating leases shown but excluded | `fundamentals._total_debt` |
| SBC | An expense: never added back to FCFF; FCF after SBC shown beside cash FCF; existing RSUs counted as shares | `valuation/dcf.py`, `valuation/run.py` |
| Gross profit | As reported if the company reports it; otherwise "revenue − cost of revenue as presented", labelled | `fundamentals.compute` |
| Share classes | Market cap uses every class; unlisted Class B valued at the Class A price (convertible 1:1) | `reviews/GOOGL/valuation.yaml` |
| Discounting | End of period from the valuation date; only the remaining part of the first forecast year is counted | `valuation/dcf.py` |

## Team to-do before submission

- [ ] Approve or reject each entry in `reviews/GOOGL/adjustments.yaml` (set `status` and your name in `reviewer`)
- [ ] Replace the placeholder **equity risk premium** and **beta** in `reviews/GOOGL/valuation.yaml` with cited figures, and approve or change every assumption
- [ ] Confirm the drafted MSFT comparability note (marked "Team to confirm")
- [ ] Resolve the open review warnings (`fre review GOOGL`), including the FY2023 finance-lease reclassification
- [ ] Fill `reviews/GOOGL/thesis.yaml` (claim, counterevidence, invalidation) once the client case is released
- [ ] Confirm this season's AI-use rules for the competition (PRD section 11)

## Known limits

- The FY2021 weighted-average share count is reported only by share class, so the FY2021→FY2022 EPS bridge is blocked, not estimated.
- Depreciation in the forecast is a proposed share of revenue; a PP&E roll-forward tied to the capex path is the next model step.
- The reverse DCF moves one assumption at a time; the grids show pairs. Sensitivity ranges are not confidence intervals, and no scenario has a probability attached.
- Company Facts omits segment data; segment valuation (PRD B level 4) is not built.
- Meta's quarterly filings do not tag lease liabilities, so its EV (and EV/EBIT) at the latest 10-Q is withheld rather than mixed with a December figure.
- Capex / depreciation is not like-for-like across peers (different XBRL tags; the peer notes name each one).
- This model supports research. It does not produce a recommendation, and it does not claim to reproduce any fund's process.

## Layout

```
src/fre/            engine (normalize, reconcile, fundamentals, eps_bridge, ledger, quarterly, dossier, screen, cli)
src/fre/valuation/  dcf, reverse, wacc, market data, run, report
config/             supported companies and cited corporate actions
reviews/<TICKER>/   human-owned inputs: adjustments, attestations, valuation assumptions, thesis
data/snapshots/     immutable source snapshots + manifest + lock (pinned ids per company)
reports/            the latest generated outputs, committed for reading without running anything
tests/              160+ failure-mode tests, each written to fail when its guard is removed; hand-calculated DCF fixture
```
