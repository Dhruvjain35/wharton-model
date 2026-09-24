# Alphabet Inc. (GOOGL) — fundamentals dossier

Fiscal years FY2021–FY2025 (fiscal year ends 12-31) · run `a93e98d0a905` · code `286ad5a3` (uncommitted changes) · created 2026-09-24T06:42:27+00:00

**Data vintage: current (latest restated filings).** Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 134 derived, 29 missing, 178 reported
- Reconciliation to filed statements: 2 from-notes, 116 matched, 45 matched-in-notes, 12 matched-negated, 22 not-checked, 3 text-candidate
- Review queue: 0 blocking, 5 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $257.6bn in FY2021 to $402.8bn in FY2025, a compound annual rate of 11.8% over 4 years.
Operating margin expanded from 30.6% to 32.0% (+148 bp).

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Revenue | USD | $257.6bn | $282.8bn | $307.4bn | $350.0bn | $402.8bn | us-gaap:Revenues · 'Revenues' |
| Revenue growth | % | n/a | +9.8% | +8.7% | +13.9% | +15.1% | `revenue / prior revenue - 1` |
| Gross margin | % | 56.9% | 55.4% | 56.6% | 58.2% | 59.7% | `gross_profit_calc / revenue` |
| Operating margin | % | 30.6% | 26.5% | 27.4% | 32.1% | 32.0% | `operating_income / revenue` |
| Net margin | % | 29.5% | 21.2% | 24.0% | 28.6% | 32.8% | `net_income / revenue` |
| R&D / revenue | % | 12.3% | 14.0% | 14.8% | 14.1% | 15.2% | `rnd / revenue` |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2021->FY2022: bridge blocked (missing shares_diluted@FY2021).
- FY2022->FY2023: diluted EPS +27.2%; net income +23.0%, diluted shares -3.3% — share-count reduction explains 14.0% of EPS growth (log basis). It was bought with $61.5bn of repurchases while SBC was $22.5bn.
- FY2023->FY2024: diluted EPS +38.6%; net income +35.7%, diluted shares -2.2% — share-count reduction explains 6.7% of EPS growth (log basis). It was bought with $62.2bn of repurchases while SBC was $22.8bn.
- FY2024->FY2025: diluted EPS +34.5%; net income +32.0%, diluted shares -1.7% — share-count reduction explains 5.9% of EPS growth (log basis). It was bought with $45.7bn of repurchases while SBC was $25.0bn.
- If the PROPOSED net-income entries for FY2024 and FY2025 were approved (GOOGL-FY2024-EQGAIN, GOOGL-FY2025-EQGAIN), diluted EPS would be $9.25 instead of $10.81, and EPS growth +18.6% instead of +34.5%. None are approved yet; this is a preview for the team's review.

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Net income | USD | $76.0bn | $60.0bn | $73.8bn | $100.1bn | $132.2bn | us-gaap:NetIncomeLoss · 'Net income' |
| Diluted shares (wtd. avg.) | shares | — | 13,159m | 12,722m | 12,447m | 12,230m | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding · 'Number of shares used in per share computation (in shares)' |
| Diluted EPS | USD/share | $5.61 | $4.56 | $5.80 | $8.04 | $10.81 | us-gaap:EarningsPerShareDiluted · 'Diluted net income per share (in dollars per share)' |
| EPS growth | % | n/a | -18.7% | +27.2% | +38.6% | +34.5% | `eps_diluted / prior eps_diluted - 1` |
| Diluted share change | % | n/a | n/a | -3.3% | -2.2% | -1.7% | `shares_diluted / prior shares_diluted - 1` |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +73.8% from FY2021 to FY2025; cash FCF changed +9.3% ($67.0bn to $73.3bn).
Capex went from $24.6bn to $91.4bn (3.7x), reaching 22.7% of revenue and 4.33x depreciation in FY2025.

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Operating cash flow | USD | $91.7bn | $91.5bn | $101.7bn | $125.3bn | $164.7bn | us-gaap:NetCashProvidedByUsedInOperatingActivities · 'Net cash provided by operating activities' |
| CFO / net income | x | 1.21x | 1.53x | 1.38x | 1.25x | 1.25x | `cfo / net_income` |
| Capex (cash) | USD | $24.6bn | $31.5bn | $32.3bn | $52.5bn | $91.4bn | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment · 'Purchases of property and equipment' |
| Cash FCF (CFO - capex) | USD | $67.0bn | $60.0bn | $69.5bn | $72.8bn | $73.3bn | `cfo - capex (cash FCF; not unlevered FCFF)` |
| FCF margin | % | 26.0% | 21.2% | 22.6% | 20.8% | 18.2% | `fcf / revenue` |
| FCF after SBC | USD | $51.6bn | $40.6bn | $47.0bn | $50.0bn | $48.3bn | `cfo - capex - sbc` |

## 4. What investment does growth require?

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Capex / revenue | % | 9.6% | 11.1% | 10.5% | 15.0% | 22.7% | `capex / revenue` |
| Depreciation (as tagged; see definitions) | USD | $10.3bn | $13.5bn | $11.9bn | $15.3bn | $21.1bn | us-gaap:Depreciation · 'Depreciation of property and equipment' |
| Capex / depreciation | x | 2.40x | 2.34x | 2.70x | 3.43x | 4.33x | `capex / dna` |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Stock-based compensation | USD | $15.4bn | $19.4bn | $22.5bn | $22.8bn | $25.0bn | us-gaap:ShareBasedCompensation · 'Stock-based compensation expense' |
| SBC / revenue | % | 6.0% | 6.8% | 7.3% | 6.5% | 6.2% | `sbc / revenue` |
| Non-operating income / pretax | % | 13.2% | -4.9% | 1.7% | 6.2% | 18.8% | `nonoperating_income / pretax_income` |
| Effective tax rate | % | 16.2% | 15.9% | 13.9% | 16.4% | 16.8% | `income_tax / pretax_income` |
| ROIC (proposed definition) | % | n/a | 56.1% | 51.3% | 51.7% | 44.9% | `nopat / ((invested_capital + prior invested_capital) / 2)` |
| Buybacks | USD | $50.3bn | $59.3bn | $61.5bn | $62.2bn | $45.7bn | us-gaap:PaymentsForRepurchaseOfCommonStock · 'Repurchases of stock' |
| Dividends | USD | $0 | $0 | $0 | $7.4bn | $10.0bn | us-gaap:PaymentsOfDividends · 'Dividend payments' |
| Buybacks + dividends / FCF | % | 75.0% | 98.8% | 88.5% | 95.6% | 76.1% | `shareholder_payout / fcf` |
| Debt incl. finance leases | USD | $14.9bn | $15.0bn | $14.5bn | $15.9bn | $51.0bn | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` |
| Cash + marketable securities | USD | $139.6bn | $113.8bn | $110.9bn | $95.7bn | $126.8bn | `cash + st_investments` |
| Net debt (negative = net cash) | USD | -$124.7bn | -$98.8bn | -$96.4bn | -$79.8bn | -$75.8bn | `total_debt - liquid_investments` |
| Operating leases (excluded from debt) | USD | $13.6bn | $15.0bn | $15.3bn | $14.6bn | $16.0bn | us-gaap:OperatingLeaseLiability · 'Total operating lease liabilities' |

Debt policy: notes at carrying value + finance leases + commercial paper, every year. Operating leases are shown but excluded. SBC stays an expense: FCF after SBC is shown beside cash FCF.

### Accounting review ledger

| ID | Year | Metric | Original | Adjustment | Result | Status |
|---|---|---|---:|---:|---:|---|
| GOOGL-FY2021-EQGAIN | FY2021 | net_income | $76.0bn | -$9.8bn | $66.3bn | proposed |
| GOOGL-FY2022-EQGAIN | FY2022 | net_income | $60.0bn | $2.7bn | $62.7bn | proposed |
| GOOGL-FY2023-EQGAIN | FY2023 | net_income | $73.8bn | -$310m | $73.5bn | proposed |
| GOOGL-FY2024-EQGAIN | FY2024 | net_income | $100.1bn | -$2.9bn | $97.2bn | proposed |
| GOOGL-FY2025-EQGAIN | FY2025 | net_income | $132.2bn | -$19.0bn | $113.1bn | proposed |
| GOOGL-FY2023-USEFUL-LIFE | FY2023 | operating_income | $84.3bn | -$3.9bn | $80.4bn | proposed |
| GOOGL-FY2023-USEFUL-LIFE-NI | FY2023 | net_income | $73.8bn | -$3.0bn | $70.8bn | proposed |
| GOOGL-FY2023-RESTRUCTURING | FY2023 | operating_income | $84.3bn | $4.2bn | $88.5bn | proposed |
| GOOGL-FY2024-RESTRUCTURING | FY2024 | operating_income | $112.4bn | $1.8bn | $114.2bn | proposed |
| GOOGL-FY2025-LEGAL | FY2025 | operating_income | $129.0bn | $4.9bn | $133.9bn | proposed |

- **GOOGL-FY2022-MANDIANT** (FY2022, FY2023): Mandiant was acquired on 2022-09-12 and reported in Google Cloud from that date. FY2022-FY2023 growth includes acquired revenue; the amount is not separately disclosed here.
- **GOOGL-FY2025-TAX-LAW-CFO** (FY2025): The July 4, 2025 US tax law allows immediate R&D expensing and accelerated depreciation; the cash benefit is inside FY2025 operating cash flow. FY2025 CFO, cash FCF and cash conversion are flattered by an amount the filing does not quantify in this passage. Cash taxes paid fell from 27.4bn (FY2024) to 21.5bn (FY2025).
- **GOOGL-FY2023-TAX-RULES** (FY2023): FY2023's effective tax rate (13.9%, against 15.9% in FY2022 and 16.4% in FY2024) includes a cumulative one-time adjustment for prior periods from two IRS rule changes, mainly on foreign tax credits. The filing does not quantify it, so no numeric adjustment is proposed; FY2023 net income and EPS growth are flattered by an unknown amount.
- **GOOGL-FY2025-WAYMO-SBC** (FY2025): A 2.1bn Waymo employee compensation charge sits in R&D. Kept as an expense: SBC is an economic cost (PRD A2, B3). Listed so nobody removes it as "one-time".

## Latest reported period (10-Q through 2026-06-30)

Year-to-date values reconciled to the 10-Q statements (1 from-notes, 28 matched, 5 matched-in-notes, 5 matched-negated, 7 not-checked, 5 text-candidate). TTM = last fiscal year + YTD - prior-year YTD, built only from reconciled inputs.

| Metric | YTD prior year | YTD current | Change | Latest quarter | TTM |
|---|---:|---:|---:|---:|---:|
| Revenue | $186.7bn | $229.7bn | +23.1% | $119.8bn | $445.9bn |
| Operating income | $61.9bn | $80.5bn | +30.0% | $40.8bn | $147.6bn |
| Net income | $62.7bn | $174.8bn | +178.6% | $112.2bn | $244.2bn |
| Gains on equity securities | $11.0bn | $135.9bn | +1130.9% | $99.0bn | $149.0bn |
| Operating cash flow | $63.9bn | $84.9bn | +32.8% | $39.1bn* | $185.7bn |
| Capex | $39.6bn | $80.6bn | +103.3% | $44.9bn* | $132.4bn |
| Cash FCF (CFO - capex) | $24.3bn | $4.3bn | -82.4% | -$5.9bn* | $53.3bn |
| Depreciation | $9.5bn | $13.6bn | +43.2% | $7.1bn* | $25.2bn |
| SBC | $11.5bn | $14.7bn | +27.7% | $8.0bn* | $28.1bn |
| Buybacks | $28.3bn | $0 | -100.0% | $0* | $17.4bn |
| Dividends to common | $5.0bn | $5.2bn | +5.1% | — | $10.3bn |

\* latest quarter derived as YTD minus the prior YTD (cash flow statements report year-to-date only).

Balance sheet at 2026-06-30:

| Item | Amount |
|---|---:|
| Cash | $55.9bn |
| Marketable securities | $186.6bn |
| Other long-term investments | $131.5bn |
| Long-term debt | $98.2bn |
| Current portion of debt | $2.0bn |
| Finance leases | $2.6bn |
| Preferred stock (carrying) | $18.0bn |
| Total equity | $640.5bn |
| Common shares outstanding | 12,230m |

## 6. How does it compare with comparable businesses?

Latest fiscal year of each company:

| Metric | GOOGL FY2025 (FYE 12-31) | MSFT FY2026 (FYE 06-30) | META FY2025 (FYE 12-31) |
|---|---:|---:|---:|
| Revenue | $402.8bn | $331.8bn | $201.0bn |
| Revenue CAGR (window) | 11.8% | 13.7% | 14.3% |
| Operating margin | 32.0% | 46.8% | 41.4% |
| Net margin | 32.8% | 40.3% | 30.1% |
| FCF margin | 18.2% | 20.2% | 22.9% |
| Capex / revenue | 22.7% | 34.9% | 34.7% |
| Capex / depreciation (definitions differ) | 4.33x | 3.38x | 3.74x |
| SBC / revenue | 6.2% | 3.7% | 10.2% |
| CFO / net income | 1.25x | 1.37x | 1.92x |
| Diluted share change | -1.7% | -0.2% | -1.5% |
| Non-operating / pretax | 18.8% | 6.4% | 3.1% |
| Net debt | -$75.8bn | $30.0bn | -$21.7bn |

Five-year history (period end in brackets):

**Revenue growth**

| Company (currency) | Y-4 | Y-3 | Y-2 | Y-1 | Y-0 |
|---|---:|---:|---:|---:|---:|
| GOOGL (USD) | — (Dec 2021) | +9.8% (Dec 2022) | +8.7% (Dec 2023) | +13.9% (Dec 2024) | +15.1% (Dec 2025) |
| MSFT (USD) | — (Jun 2022) | +6.9% (Jun 2023) | +15.7% (Jun 2024) | +14.9% (Jun 2025) | +17.8% (Jun 2026) |
| META (USD) | — (Dec 2021) | -1.1% (Dec 2022) | +15.7% (Dec 2023) | +21.9% (Dec 2024) | +22.2% (Dec 2025) |

**Operating margin**

| Company (currency) | Y-4 | Y-3 | Y-2 | Y-1 | Y-0 |
|---|---:|---:|---:|---:|---:|
| GOOGL (USD) | 30.6% (Dec 2021) | 26.5% (Dec 2022) | 27.4% (Dec 2023) | 32.1% (Dec 2024) | 32.0% (Dec 2025) |
| MSFT (USD) | 42.1% (Jun 2022) | 41.8% (Jun 2023) | 44.6% (Jun 2024) | 45.6% (Jun 2025) | 46.8% (Jun 2026) |
| META (USD) | 39.6% (Dec 2021) | 24.8% (Dec 2022) | 34.7% (Dec 2023) | 42.2% (Dec 2024) | 41.4% (Dec 2025) |

**FCF margin**

| Company (currency) | Y-4 | Y-3 | Y-2 | Y-1 | Y-0 |
|---|---:|---:|---:|---:|---:|
| GOOGL (USD) | 26.0% (Dec 2021) | 21.2% (Dec 2022) | 22.6% (Dec 2023) | 20.8% (Dec 2024) | 18.2% (Dec 2025) |
| MSFT (USD) | 32.9% (Jun 2022) | 28.1% (Jun 2023) | 30.2% (Jun 2024) | 25.4% (Jun 2025) | 20.2% (Jun 2026) |
| META (USD) | 33.1% (Dec 2021) | 16.5% (Dec 2022) | 32.7% (Dec 2023) | 32.9% (Dec 2024) | 22.9% (Dec 2025) |

**Capex / revenue**

| Company (currency) | Y-4 | Y-3 | Y-2 | Y-1 | Y-0 |
|---|---:|---:|---:|---:|---:|
| GOOGL (USD) | 9.6% (Dec 2021) | 11.1% (Dec 2022) | 10.5% (Dec 2023) | 15.0% (Dec 2024) | 22.7% (Dec 2025) |
| MSFT (USD) | 12.0% (Jun 2022) | 13.3% (Jun 2023) | 18.1% (Jun 2024) | 22.9% (Jun 2025) | 34.9% (Jun 2026) |
| META (USD) | 15.8% (Dec 2021) | 26.7% (Dec 2022) | 20.0% (Dec 2023) | 22.6% (Dec 2024) | 34.7% (Dec 2025) |

Comparability:

- **GOOGL**: Three segments: Google Services, Google Cloud and Other Bets. Services earns primarily advertising revenue across Search, YouTube and partner properties. Source (10-K, verified verbatim): “We report our segment results as Google Services, Google Cloud, and Other Bets.” “generates revenues primarily by delivering both performance and brand advertising that appears on Google Search & other properties, YouTube, and Google Network partners' properties”
- **MSFT**: Three segments: Productivity and Business Processes, Intelligent Cloud, and More Personal Computing. Team to confirm: it is a comparable for Google Cloud and enterprise software more than for advertising. Its fiscal year ends June 30. Source (10-K, verified verbatim): “Our Intelligent Cloud segment consists of our public, private, and hybrid server products and cloud services that power modern business and developers.” “Our Productivity and Business Processes segment consists of products and services in our portfolio of productivity, communication, and information services, spanning a variety of devices and platforms.”
- **META**: Two segments, Family of Apps and Reality Labs, and substantially all revenue from advertising: the closest business-model match to Google Services. It has no public cloud business, so it says nothing about Google Cloud economics. Source (10-K, verified verbatim): “We report our financial results for our two reportable segments: Family of Apps (FoA) and Reality Labs (RL).” “We generate substantially all of our revenue from advertising.”

- MSFT's fiscal year ends 06-30: its FY2026 ended 2026-06-30, not on GOOGL's 12-31 calendar. Latest-year columns are not the same twelve months.
- GOOGL does not report gross profit; gross margin uses revenue minus cost of revenue as presented.
- MSFT reports gross profit.
- META does not report gross profit; gross margin uses revenue minus cost of revenue as presented.
- Capex / depreciation is NOT like-for-like: GOOGL uses us-gaap:Depreciation (property and equipment only; excludes amortization); MSFT uses us-gaap:Depreciation (property and equipment only; excludes amortization); META uses us-gaap:DepreciationDepletionAndAmortization.
- The comparability notes above are drafted from each 10-K; the team should review them before relying on the comparison.

Market multiples (relative valuation; every share class counted):

| Company | Trailing window | Price date | Market cap | P/E (mkt cap / trailing NI) | P/E (price / FY diluted EPS) | EV/EBIT | FCF yield |
|---|---|---|---:|---:|---:|---:|---:|
| GOOGL | TTM to 2026-06-30 | 2026-09-23 | $4,115.9bn | 16.9x | 31.3x (FY2025) | 27.1x | 1.29% |
| MSFT | FY2026 | 2026-09-23 | $3,717.2bn | 27.8x | 27.9x (FY2026) | 24.1x | 1.80% |
| META | TTM to 2026-06-30 | 2026-09-23 | $1,895.6bn | 27.8x | 31.7x (FY2025) | — | 2.16% |
- GOOGL: 'Class A Common Stock' priced at its own trading symbol GOOGL (cover page); 'Class C Capital Stock' priced at its own trading symbol GOOG (cover page); 'Class B Common Stock' priced at GOOGL (no trading symbol on the cover page; config mapping); EV = market cap + debt incl. finance leases + preferred at carrying value - cash - marketable securities
- MSFT: 'Common stock' priced at MSFT (no trading symbol on the cover page; config mapping); EV = market cap + debt incl. finance leases + preferred at carrying value - cash - marketable securities
- META: 'Common Class A' priced at META (no trading symbol on the cover page; config mapping); 'Common Class B' priced at META (no trading symbol on the cover page; config mapping); debt component(s) not reported at 2026-06-30: finance_lease_liability; EV = market cap + debt incl. finance leases + preferred at carrying value - cash - marketable securities; EV not computed: debt not reported at the balance-sheet date; EV/EBIT: input missing

## 7. Thesis and what would change it (team-owned)

- Claim: **not written yet**
- Direction: **not set** · owner: **none**
- Counterevidence: **empty**
- Would change our view if: **empty**
- Decision history: **empty**
- Research questions: What revenue growth and operating margin combination is consistent with the price? (valuation grid, reverse DCF) / What if capex intensity stays elevated longer than the base case? (adverse scenario, capex break-even) / How much value depends on sustained excess returns? (terminal ROIC sensitivity) / Which assumption matters most? (compare the reverse-DCF moves for growth, margin and WACC)

## Review queue

- **warn** `missing` Weighted-average basic shares FY2021: not found under any mapped tag
- **warn** `missing` Weighted-average diluted shares FY2021: not found under any mapped tag
- **warn** `restated` Long-term debt incl. finance leases, noncurrent FY2023: 0001652044-24-000022 reported 1.3253e+10, latest filing reports 1.187e+10; confirm the reason in the later filing
- **warn** `restated` Finance lease liabilities FY2023: 0001652044-24-000022 reported 1.746e+09, latest filing reports 1.666e+09; confirm the reason in the later filing
- **warn** `restated` Finance lease liabilities, current FY2023: 0001652044-24-000022 reported 3.63e+08, latest filing reports 2.83e+08; confirm the reason in the later filing

## Definitions

| Metric | Formula | Years |
|---|---|---|
| capex_intensity | `capex / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| capex_to_depreciation | `capex / dna` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| cash_conversion | `cfo / net_income` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` | FY2023, FY2024, FY2025 |
| effective_tax_rate | `income_tax / pretax_income` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| eps_growth | `eps_diluted / prior eps_diluted - 1` | FY2022, FY2023, FY2024, FY2025 |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| fcf_after_sbc | `cfo - capex - sbc` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| fcf_growth | `fcf / prior fcf - 1` | FY2022, FY2023, FY2024, FY2025 |
| fcf_margin | `fcf / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| gross_margin | `gross_profit_calc / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| gross_profit_calc | `revenue - cost_of_revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| invested_capital | `equity + total_debt - cash - st_investments - other_lt_investments` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| liquid_investments | `cash + st_investments` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| net_debt | `total_debt - liquid_investments` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| net_income_growth | `net_income / prior net_income - 1` | FY2022, FY2023, FY2024, FY2025 |
| net_margin | `net_income / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| nonoperating_share_of_pretax | `nonoperating_income / pretax_income` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| nopat | `operating_income * (1 - effective_tax_rate)` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| operating_income_growth | `operating_income / prior operating_income - 1` | FY2022, FY2023, FY2024, FY2025 |
| operating_margin | `operating_income / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| payout_to_fcf | `shareholder_payout / fcf` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| revenue_cagr | `(revenue FY2025 / revenue FY2021)^(1/4) - 1` | FY2025 |
| revenue_growth | `revenue / prior revenue - 1` | FY2022, FY2023, FY2024, FY2025 |
| rnd_intensity | `rnd / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| roic | `nopat / ((invested_capital + prior invested_capital) / 2)` | FY2022, FY2023, FY2024, FY2025 |
| sbc_intensity | `sbc / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| shareholder_payout | `buybacks + dividends` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| total_debt | `debt_and_finance_lease_noncurrent + debt_lt_current + finance_lease_liability_current + commercial_paper` | FY2021, FY2022 |
| total_debt | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` | FY2023, FY2024, FY2025 |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividendsCommonStock, PaymentsOfOrdinaryDividends, PaymentsOfDividends; preferred_dividends = DividendsPreferredStockCash, PaymentsOfDividendsPreferredStockAndPreferenceStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting (withheld), — missing (not reported), n/a suppressed (formula exists but an input or denominator does not allow it; the reason is in tables/facts.csv and review.html).
