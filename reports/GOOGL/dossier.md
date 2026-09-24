# Alphabet Inc. (GOOGL) — fundamentals dossier

Fiscal years FY2021–FY2025 (fiscal year ends 12-31) · run `6de304a168fb` · code `c8d27307` (uncommitted changes) · created 2026-09-24T05:52:19+00:00

Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 120 derived, 23 missing, 178 reported
- Reconciliation to filed statements: 11 from-notes, 115 matched, 40 matched-in-notes, 12 matched-negated, 17 not-checked
- Review queue: 0 blocking, 5 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $257.6bn in FY2021 to $402.8bn in FY2025, a 11.8% compound annual rate over 4 years.
Operating margin expanded from 30.6% to 32.0% (+148 bp).

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Revenue | $257.6bn | $282.8bn | $307.4bn | $350.0bn | $402.8bn |
| Revenue growth | — | +9.8% | +8.7% | +13.9% | +15.1% |
| Gross margin | 56.9% | 55.4% | 56.6% | 58.2% | 59.7% |
| Operating margin | 30.6% | 26.5% | 27.4% | 32.1% | 32.0% |
| Net margin | 29.5% | 21.2% | 24.0% | 28.6% | 32.8% |
| R&D / revenue | 12.3% | 14.0% | 14.8% | 14.1% | 15.2% |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2021->FY2022: bridge blocked (missing shares_diluted@FY2021).
- FY2022->FY2023: diluted EPS +27.2%; net income +23.0%, diluted shares -3.3% — share-count reduction explains 14.0% of EPS growth (log basis). It was bought with $61.5bn of repurchases while SBC was $22.5bn.
- FY2023->FY2024: diluted EPS +38.6%; net income +35.7%, diluted shares -2.2% — share-count reduction explains 6.7% of EPS growth (log basis). It was bought with $62.2bn of repurchases while SBC was $22.8bn.
- FY2024->FY2025: diluted EPS +34.5%; net income +32.0%, diluted shares -1.7% — share-count reduction explains 5.9% of EPS growth (log basis). It was bought with $45.7bn of repurchases while SBC was $25.0bn.
- If every PROPOSED ledger entry for FY2025 were approved (GOOGL-FY2025-EQGAIN, GOOGL-FY2025-LEGAL), diluted EPS would be $9.25 instead of $10.81, and EPS growth +18.6% instead of +34.5%. None are approved yet; this is a preview for the team's review.

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Net income | $76.0bn | $60.0bn | $73.8bn | $100.1bn | $132.2bn |
| Diluted shares (wtd. avg.) | — | 13,159m | 12,722m | 12,447m | 12,230m |
| Diluted EPS | $5.61 | $4.56 | $5.80 | $8.04 | $10.81 |
| EPS growth | — | -18.7% | +27.2% | +38.6% | +34.5% |
| Diluted share change | — | — | -3.3% | -2.2% | -1.7% |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +73.8% from FY2021 to FY2025; cash FCF changed +9.3% ($67.0bn to $73.3bn).
Capex went from $24.6bn to $91.4bn (3.7x), reaching 22.7% of revenue and 4.33x depreciation in FY2025.

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Operating cash flow | $91.7bn | $91.5bn | $101.7bn | $125.3bn | $164.7bn |
| CFO / net income | 1.21x | 1.53x | 1.38x | 1.25x | 1.25x |
| Capex (cash) | $24.6bn | $31.5bn | $32.3bn | $52.5bn | $91.4bn |
| Cash FCF (CFO - capex) | $67.0bn | $60.0bn | $69.5bn | $72.8bn | $73.3bn |
| FCF margin | 26.0% | 21.2% | 22.6% | 20.8% | 18.2% |
| FCF after SBC | $51.6bn | $40.6bn | $47.0bn | $50.0bn | $48.3bn |

## 4. What investment does growth require?

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Capex / revenue | 9.6% | 11.1% | 10.5% | 15.0% | 22.7% |
| Depreciation (cash flow) | $10.3bn | $13.5bn | $11.9bn | $15.3bn | $21.1bn |
| Capex / depreciation | 2.40x | 2.34x | 2.70x | 3.43x | 4.33x |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Stock-based compensation | $15.4bn | $19.4bn | $22.5bn | $22.8bn | $25.0bn |
| SBC / revenue | 6.0% | 6.8% | 7.3% | 6.5% | 6.2% |
| Non-operating income / pretax | 13.2% | -4.9% | 1.7% | 6.2% | 18.8% |
| Effective tax rate | 16.2% | 15.9% | 13.9% | 16.4% | 16.8% |
| Buybacks | $50.3bn | $59.3bn | $61.5bn | $62.2bn | $45.7bn |
| Dividends | $0 | $0 | $0 | $7.4bn | $10.0bn |
| Buybacks + dividends / FCF | 75.0% | 98.8% | 88.5% | 95.6% | 76.1% |
| Debt incl. finance leases | $14.9bn | $15.0bn | $14.5bn | $15.9bn | $51.0bn |
| Cash + marketable securities | $139.6bn | $113.8bn | $110.9bn | $95.7bn | $126.8bn |
| Net debt (negative = net cash) | -$124.7bn | -$98.8bn | -$96.4bn | -$79.8bn | -$75.8bn |
| Operating leases (excluded from debt) | $13.6bn | $15.0bn | $15.3bn | $14.6bn | $16.0bn |

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
- **GOOGL-FY2025-WAYMO-SBC** (FY2025): A 2.1bn Waymo employee compensation charge sits in R&D. Kept as an expense: SBC is an economic cost (PRD A2, B3). Listed so nobody removes it as "one-time".

## 6. How does it compare with comparable businesses?

| Metric | GOOGL FY2025 (FYE 12-31) | MSFT FY2026 (FYE 06-30) | META FY2025 (FYE 12-31) |
|---|---:|---:|---:|
| Revenue | $402.8bn | $331.8bn | $201.0bn |
| Revenue CAGR (window) | 11.8% | 13.7% | 14.3% |
| Operating margin | 32.0% | 46.8% | 41.4% |
| Net margin | 32.8% | 40.3% | 30.1% |
| FCF margin | 18.2% | 20.2% | 22.9% |
| Capex / revenue | 22.7% | 34.9% | 34.7% |
| Capex / depreciation | 4.33x | 3.38x | 3.74x |
| SBC / revenue | 6.2% | 3.7% | 10.2% |
| CFO / net income | 1.25x | 1.37x | 1.92x |
| Diluted share change | -1.7% | -0.2% | -1.5% |
| Non-operating / pretax | 18.8% | 6.4% | 3.1% |
| Net debt | -$75.8bn | $30.0bn | -$21.7bn |

- MSFT's fiscal year ends 06-30: its FY2026 ended 2026-06-30, not on GOOGL's 12-31 calendar. Latest-year columns are not the same twelve months.
- GOOGL does not report gross profit; gross margin uses revenue minus cost of revenue as presented.
- MSFT reports gross profit
- META does not report gross profit; gross margin uses revenue minus cost of revenue as presented.
- Business-mix comparability (segments, customers, capital intensity drivers) is a team judgment: write it from Item 1 of each 10-K before relying on this table.

## Review queue

- **warn** `missing` Weighted-average basic shares FY2021: not found under any mapped tag
- **warn** `missing` Weighted-average diluted shares FY2021: not found under any mapped tag
- **warn** `restated` Long-term debt incl. finance leases, noncurrent FY2023: 0001652044-24-000022 reported 1.3253e+10, latest filing reports 1.187e+10; confirm the reason in the later filing
- **warn** `restated` Finance lease liabilities FY2023: 0001652044-24-000022 reported 1.746e+09, latest filing reports 1.666e+09; confirm the reason in the later filing
- **warn** `restated` Finance lease liabilities, current FY2023: 0001652044-24-000022 reported 3.63e+08, latest filing reports 2.83e+08; confirm the reason in the later filing

## Definitions

| Metric | Formula |
|---|---|
| gross_profit_calc | `revenue - cost_of_revenue` |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` |
| fcf_after_sbc | `cfo - capex - sbc` |
| liquid_investments | `cash + st_investments` |
| total_debt | `debt_and_finance_lease_noncurrent + debt_lt_current + finance_lease_liability_current + commercial_paper` |
| net_debt | `total_debt - liquid_investments` |
| shareholder_payout | `buybacks + dividends` |
| gross_margin | `gross_profit_calc / revenue` |
| operating_margin | `operating_income / revenue` |
| net_margin | `net_income / revenue` |
| fcf_margin | `fcf / revenue` |
| capex_intensity | `capex / revenue` |
| sbc_intensity | `sbc / revenue` |
| rnd_intensity | `rnd / revenue` |
| cash_conversion | `cfo / net_income` |
| effective_tax_rate | `income_tax / pretax_income` |
| capex_to_depreciation | `capex / dna` |
| payout_to_fcf | `shareholder_payout / fcf` |
| nonoperating_share_of_pretax | `nonoperating_income / pretax_income` |
| revenue_growth | `revenue / prior revenue - 1` |
| operating_income_growth | `operating_income / prior operating_income - 1` |
| net_income_growth | `net_income / prior net_income - 1` |
| fcf_growth | `fcf / prior fcf - 1` |
| eps_growth | `eps_diluted / prior eps_diluted - 1` |
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` |
| revenue_cagr | `(revenue FY2025 / revenue FY2021)^(1/4) - 1` |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividends, PaymentsOfDividendsCommonStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting, — missing or suppressed (see facts.csv notes for the reason).
