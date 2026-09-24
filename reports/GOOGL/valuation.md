# GOOGL valuation — FCFF DCF (PRD phase B)

**Every judgment input below is PROPOSED and unapproved.** The output shows what those inputs imply; it is not a price target or a recommendation. The reverse DCF and grids show how much the answer moves.

Valuation date 2026-06-30 (latest 10-Q balance sheet) · first forecast year counts 50.4% of its cash flow · prices dated separately below.

## Evidence the assumptions lean on (computed from reconciled facts)

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 | YTD prior | YTD 2026-06-30 | TTM |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Revenue | $257.6bn | $282.8bn | $307.4bn | $350.0bn | $402.8bn | $186.7bn | $229.7bn | $445.9bn |
| Operating income | $78.7bn | $74.8bn | $84.3bn | $112.4bn | $129.0bn | $61.9bn | $80.5bn | $147.6bn |
| Net income | $76.0bn | $60.0bn | $73.8bn | $100.1bn | $132.2bn | $62.7bn | $174.8bn | $244.2bn |
| Gains on equity securities | $12.4bn | -$3.5bn | $392m | $3.7bn | $24.1bn | $11.0bn | $135.9bn | $149.0bn |
| Operating cash flow | $91.7bn | $91.5bn | $101.7bn | $125.3bn | $164.7bn | $63.9bn | $84.9bn | $185.7bn |
| Capex | $24.6bn | $31.5bn | $32.3bn | $52.5bn | $91.4bn | $39.6bn | $80.6bn | $132.4bn |
| Depreciation | $10.3bn | $13.5bn | $11.9bn | $15.3bn | $21.1bn | $9.5bn | $13.6bn | $25.2bn |
| SBC | $15.4bn | $19.4bn | $22.5bn | $22.8bn | $25.0bn | $11.5bn | $14.7bn | $28.1bn |
| Buybacks | $50.3bn | $59.3bn | $61.5bn | $62.2bn | $45.7bn | $28.3bn | $0 | $17.4bn |

- YTD revenue growth +23.1%; operating margin YTD 35.0%, TTM 33.1%.
- Capex intensity YTD 35.1%, TTM 29.7%; depreciation intensity YTD 5.9%.
- Cash FCF (CFO − capex) YTD $4.3bn vs $24.3bn a year earlier.
- Gains on equity securities are 77.8% of YTD net income.

## Assumptions

| Assumption | Value | Range | Units | Status | Owner |
|---|---|---|---|---|---|
| growth | 20.0%, 15.0%, 12.0%, 10.0%, 8.0% | 14.0%, 9.0%, 6.0%, 5.0%, 4.0% … 24.0%, 20.0%, 17.0%, 14.0%, 11.0% | revenue growth, FY2026-FY2030 | proposed | Claude (AI-proposed) |
| operating_margin | 33.0%, 32.0%, 32.0%, 32.0%, 32.0% | 30.0%, 27.0%, 26.0%, 26.0%, 26.0% … 36.0%, 36.0%, 36.0%, 36.0%, 36.0% | GAAP operating margin (SBC expensed), FY2026-FY2030 | proposed | Claude (AI-proposed) |
| tax_rate | 17.00% | 14.00% … 21.00% | operating cash tax rate on EBIT | proposed | Claude (AI-proposed) |
| capex_pct | 33.0%, 30.0%, 25.0%, 20.0%, 17.0% | 28.0%, 22.0%, 17.0%, 14.0%, 12.0% … 38.0%, 36.0%, 33.0%, 28.0%, 24.0% | cash capex / revenue, FY2026-FY2030 | proposed | Claude (AI-proposed) |
| dna_pct | 6.5%, 9.0%, 11.0%, 12.0%, 12.5% | 6.0%, 7.5%, 8.5%, 9.5%, 10.0% … 7.5%, 11.0%, 13.0%, 14.0%, 15.0% | depreciation / revenue, FY2026-FY2030 | proposed | Claude (AI-proposed) |
| terminal_growth | 3.00% | 2.00% … 4.00% | perpetual nominal growth from FY2031 | proposed | Claude (AI-proposed) |
| terminal_margin | 32.00% | 26.00% … 36.00% | operating margin in the terminal year | proposed | Claude (AI-proposed) |
| terminal_roic | 20.00% | 12.00% … 35.00% | return on new invested capital in perpetuity | proposed | Claude (AI-proposed) |
| equity_risk_premium | 4.50% | 4.00% … 5.50% | US equity risk premium | proposed | Claude (AI-proposed) |
| beta | 1.05 | 0.90 … 1.30 | equity beta | proposed | Claude (AI-proposed) |
| operating_cash | $0 | $0 … $20.0bn | USD of cash treated as operationally necessary (not excess) | proposed | Claude (AI-proposed) |

## Sourced inputs

- Risk-free: FRED DGS10 4.44% on 2026-06-30 (https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2026-06-20&coed=2026-06-30, snapshot `970b700eefd5ace6`)
- class_split: 12,230 (Class A 5,868 , Class B 835 , Class C 5,527 ) — "12,230 (Class A 5,868 , Class B 835 , Class C 5,527 ) shares issued and outstanding" (snapshot `1b4e671893d74a58`)
- pretax_cost_of_debt: 4.80 % — "$ 20.0 billion US dollar-denominated notes with a weighted-average coupon rate of 4.80 %" (snapshot `1b4e671893d74a58`)
- preferred_dividend_rate: 6.25 % — "Dividends are cumulative at an annual rate of 6.25 % on the liquidation preference of $ 1,000 per share" (snapshot `1b4e671893d74a58`)
- preferred_depositary_shares: 385 million — "issued an aggregate amount of 385 million Series A and Series B depositary shares" (snapshot `1b4e671893d74a58`)
- preferred_liquidation_per_depositary_share: $ 50 per depositary share — "liquidation preference of $ 1,000 per share ($ 50 per depositary share)" (snapshot `1b4e671893d74a58`)

## Discount rate

Cost of equity 9.17% = 4.44% + 1.05 × 4.50%; after-tax cost of debt 3.98%; preferred 6.18% (dividend on liquidation preference / market price). Market weights at 2026-06-30: equity 97.3%, debt 2.3%, preferred 0.4%. **WACC 9.03%.**

## Equity bridge (all at the valuation date)

| Item | Amount | Source |
|---|---:|---|
| Operating EV (base) | $2,240.4bn | model |
| + Cash and marketable securities (less operating cash $0) | $242.5bn | 0001652044-26-000071 us-gaap:CashAndCashEquivalentsAtCarryingValue at 2026-06-30; 0001652044-26-000071 us-gaap:MarketableSecuritiesCurrent at 2026-06-30 |
| + Non-marketable securities (carrying value) | $131.5bn | 0001652044-26-000071 us-gaap:OtherLongTermInvestments at 2026-06-30 |
| − Debt incl. finance leases | $102.8bn | notes, current portion, finance leases, commercial paper |
| − Mandatory convertible preferred (liquidation preference) | $19.2bn | 10-Q quotes |
| = Equity value | $2,492.3bn | |
| ÷ Diluted shares | 12,524m | 12,230m outstanding + 294m unvested RSUs |

SBC stays inside operating margin and is not added back; existing RSUs are counted as shares; no separate future-dilution charge (PRD B3). Operating leases stay operating (lease cost inside margin, liability not in debt).

## Results

| Scenario | Operating EV | Equity value | Per share | Terminal share of EV |
|---|---:|---:|---:|---:|
| base | $2,240.4bn | $2,492.3bn | $199.00 | 86% |
| adverse | $1,411.6bn | $1,663.6bn | $132.83 | 92% |
| favorable | $3,070.7bn | $3,322.6bn | $265.30 | 83% |

| Price | Date | Market cap (all classes) |
|---|---|---:|
| GOOGL $357.37 | 2026-06-30 | $4,348.3bn |
| GOOGL $337.83 | 2026-09-23 | $4,115.9bn |

- **base**: proposed assumptions
- **adverse**: Joint stress (PRD B5): growth normalizes faster while capex intensity stays higher for longer, and the new capital earns less. The pieces move together; they are not independent shocks.
- **favorable**: Growth holds up, the capex wave normalizes quickly, and margins expand as revenue from the new capacity arrives. Assumes the investment earns high returns.

Flags: 83% of operating EV is terminal value: the result mostly reflects terminal assumptions; 86% of operating EV is terminal value: the result mostly reflects terminal assumptions; 92% of operating EV is terminal value: the result mostly reflects terminal assumptions

## Reverse DCF — assumptions consistent with price under this model

One unknown at a time; every other assumption held at its base value. Bracketed Brent root finding over the bounds shown. "none" means no value inside the bounds reproduces the price.

| Price | Solve for | Result | Bounds | Monotonic |
|---|---|---|---|---|
| $357.37 (2026-06-30) | growth | 28.61% (unique) | -10.0% … 60.0% | yes |
| $357.37 (2026-06-30) | margin | 57.18% (unique) | 0.0% … 80.0% | yes |
| $357.37 (2026-06-30) | wacc | 6.35% (unique) | 4.0% … 20.0% | yes |
| $357.37 (2026-06-30) | terminal_growth | no solution in bounds (none) | -3.0% … 4.5% | yes |
| $337.83 (2026-09-23) | growth | 27.06% (unique) | -10.0% … 60.0% | yes |
| $337.83 (2026-09-23) | margin | 54.07% (unique) | 0.0% … 80.0% | yes |
| $337.83 (2026-09-23) | wacc | 6.55% (unique) | 4.0% … 20.0% | yes |
| $337.83 (2026-09-23) | terminal_growth | no solution in bounds (none) | -3.0% … 4.5% | yes |

Capex break-even at $337.83: no capex multiplier in [0.2x, 3.0x] reproduces the price with growth and margins held fixed; the gap is about growth, margins or the discount rate, not capex alone.

## Sensitivity

**operating margin (forecast and terminal) (rows) × growth (all forecast years) (columns), value per share**

| | 4.0% | 6.0% | 8.0% | 10.0% | 12.0% | 14.0% | 16.0% | 18.0% | 20.0% | 22.0% | 24.0% | 26.0% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 24.0% | 105 | 113 | 122 | 132 | 143 | 154 | 167 | 180 | 194 | 209 | 225 | 242 |
| 26.0% | 113 | 123 | 133 | 143 | 155 | 167 | 181 | 195 | 210 | 227 | 244 | 263 |
| 28.0% | 122 | 132 | 143 | 154 | 167 | 180 | 195 | 210 | 227 | 245 | 263 | 283 |
| 30.0% | 130 | 141 | 153 | 166 | 179 | 194 | 209 | 226 | 243 | 262 | 283 | 304 |
| 32.0% | 139 | 151 | 163 | 177 | 191 | 207 | 223 | 241 | 260 | 280 | 302 | 325 |
| 34.0% | 147 | 160 | 173 | 188 | 203 | 220 | 237 | 256 | 276 | 298 | 321 | 346 |
| 36.0% | 156 | 169 | 183 | 199 | 215 | 233 | 251 | 271 | 293 | 316 | 340 | 366 |
| 38.0% | 165 | 179 | 194 | 210 | 227 | 246 | 265 | 287 | 309 | 334 | 360 | 387 |
| 40.0% | 173 | 188 | 204 | 221 | 239 | 259 | 280 | 302 | 326 | 352 | 379 | 408 |
| 42.0% | 182 | 197 | 214 | 232 | 251 | 272 | 294 | 317 | 342 | 369 | 398 | 429 |

**terminal growth (rows) × WACC (columns), value per share**

| | 7.5% | 8.0% | 8.5% | 9.0% | 9.5% | 10.0% | 10.5% | 11.0% | 11.5% | 12.0% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5% | 223 | 206 | 191 | 178 | 167 | 157 | 148 | 140 | 133 | 127 |
| 2.0% | 235 | 215 | 199 | 184 | 172 | 161 | 152 | 143 | 136 | 129 |
| 2.5% | 249 | 226 | 208 | 192 | 178 | 166 | 156 | 147 | 139 | 132 |
| 3.0% | 266 | 240 | 218 | 200 | 185 | 172 | 160 | 151 | 142 | 134 |
| 3.5% | 288 | 256 | 231 | 210 | 193 | 178 | 166 | 155 | 146 | 137 |
| 4.0% | 315 | 276 | 246 | 222 | 202 | 186 | 172 | 160 | 150 | 141 |

Sensitivity ranges are not statistical confidence intervals, and no probabilities are attached to scenarios.

Non-marketable securities carry the disputed mark-to-market gains (see the accounting ledger). Value per share with those holdings haircut: 0% → $199.00, 25% → $196.38, 50% → $193.76, 100% → $188.51.

## Open inputs before this can be relied on

- Equity risk premium and beta are placeholders without a source (TEAM INPUT REQUIRED).
- Depreciation is a proposed % of revenue; a PP&E roll-forward tied to the capex path is the next model step.
- Cost of debt uses the 2026 USD coupon, not a current market yield.
- All forecast assumptions await a teammate's approval.
