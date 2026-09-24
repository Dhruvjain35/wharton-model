# Meta Platforms, Inc. (META) — fundamentals dossier

Fiscal years FY2021–FY2025 (fiscal year ends 12-31) · run `bfb51272b085` · code `41bc18bd` (uncommitted changes) · created 2026-09-24T06:25:40+00:00

**Data vintage: current (latest restated filings).** Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 141 derived, 54 missing, 146 reported
- Reconciliation to filed statements: 117 matched, 15 matched-in-notes, 14 matched-negated, 54 not-checked
- Review queue: 0 blocking, 9 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $117.9bn in FY2021 to $201.0bn in FY2025, a compound annual rate of 14.3% over 4 years.
Operating margin expanded from 39.6% to 41.4% (+179 bp).

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Revenue | USD | $117.9bn | $116.6bn | $134.9bn | $164.5bn | $201.0bn | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax · 'Revenue' |
| Revenue growth | % | n/a | -1.1% | +15.7% | +21.9% | +22.2% | `revenue / prior revenue - 1` |
| Gross margin | % | 80.8% | 78.3% | 80.8% | 81.7% | 82.0% | `gross_profit_calc / revenue` |
| Operating margin | % | 39.6% | 24.8% | 34.7% | 42.2% | 41.4% | `operating_income / revenue` |
| Net margin | % | 33.4% | 19.9% | 29.0% | 37.9% | 30.1% | `net_income / revenue` |
| R&D / revenue | % | 20.9% | 30.3% | 28.5% | 26.7% | 28.5% | `rnd / revenue` |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2021->FY2022: diluted EPS -37.6%; net income -41.1%, diluted shares -5.5%. It was bought with $28.0bn of repurchases while SBC was $12.0bn.
- FY2022->FY2023: diluted EPS +73.1%; net income +68.5%, diluted shares -2.7% — share-count reduction explains 5.0% of EPS growth (log basis). It was bought with $19.8bn of repurchases while SBC was $14.0bn.
- FY2023->FY2024: diluted EPS +60.5%; net income +59.5%, diluted shares -0.6% — share-count reduction explains 1.2% of EPS growth (log basis). It was bought with $30.1bn of repurchases while SBC was $16.7bn.
- FY2024->FY2025: diluted EPS -1.6%; net income -3.1%, diluted shares -1.5%. It was bought with $26.2bn of repurchases while SBC was $20.4bn.

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Net income | USD | $39.4bn | $23.2bn | $39.1bn | $62.4bn | $60.5bn | us-gaap:NetIncomeLoss · 'Net income' |
| Diluted shares (wtd. avg.) | shares | 2,859m | 2,702m | 2,629m | 2,614m | 2,574m | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding · 'Diluted (in shares)' |
| Diluted EPS | USD/share | $13.77 | $8.59 | $14.87 | $23.86 | $23.49 | us-gaap:EarningsPerShareDiluted · 'Diluted (in dollars per share)' |
| EPS growth | % | n/a | -37.6% | +73.1% | +60.5% | -1.6% | `eps_diluted / prior eps_diluted - 1` |
| Diluted share change | % | n/a | -5.5% | -2.7% | -0.6% | -1.5% | `shares_diluted / prior shares_diluted - 1` |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +53.6% from FY2021 to FY2025; cash FCF changed +18.2% ($39.0bn to $46.1bn).
Capex went from $18.7bn to $69.7bn (3.7x), reaching 34.7% of revenue and 3.74x depreciation in FY2025.

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Operating cash flow | USD | $57.7bn | $50.5bn | $71.1bn | $91.3bn | $115.8bn | us-gaap:NetCashProvidedByUsedInOperatingActivities · 'Net cash provided by operating activities' |
| CFO / net income | x | 1.47x | 2.18x | 1.82x | 1.46x | 1.92x | `cfo / net_income` |
| Capex (cash) | USD | $18.7bn | $31.2bn | $27.0bn | $37.3bn | $69.7bn | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment · 'Purchases of property and equipment' |
| Cash FCF (CFO - capex) | USD | $39.0bn | $19.3bn | $44.1bn | $54.1bn | $46.1bn | `cfo - capex (cash FCF; not unlevered FCFF)` |
| FCF margin | % | 33.1% | 16.5% | 32.7% | 32.9% | 22.9% | `fcf / revenue` |
| FCF after SBC | USD | $29.8bn | $7.3bn | $30.0bn | $37.4bn | $25.7bn | `cfo - capex - sbc` |

## 4. What investment does growth require?

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Capex / revenue | % | 15.8% | 26.7% | 20.0% | 22.6% | 34.7% | `capex / revenue` |
| Depreciation (as tagged; see definitions) | USD | $8.0bn | $8.7bn | $11.2bn | $15.5bn | $18.6bn | us-gaap:DepreciationDepletionAndAmortization · 'Depreciation and amortization' |
| Capex / depreciation | x | 2.35x | 3.59x | 2.42x | 2.40x | 3.74x | `capex / dna` |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | Unit | FY2021 (Dec 31, 2021) | FY2022 (Dec 31, 2022) | FY2023 (Dec 31, 2023) | FY2024 (Dec 31, 2024) | FY2025 (Dec 31, 2025) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Stock-based compensation | USD | $9.2bn | $12.0bn | $14.0bn | $16.7bn | $20.4bn | us-gaap:ShareBasedCompensation · 'Share-based compensation' |
| SBC / revenue | % | 7.8% | 10.3% | 10.4% | 10.1% | 10.2% | `sbc / revenue` |
| Non-operating income / pretax | % | 1.1% | -0.4% | 1.4% | 1.8% | 3.1% | `nonoperating_income / pretax_income` |
| Effective tax rate | % | 16.7% | 19.5% | 17.6% | 11.8% | 29.6% | `income_tax / pretax_income` |
| ROIC (proposed definition) | % | n/a | n/a | n/a | n/a | n/a | `nopat / ((invested_capital + prior invested_capital) / 2)` |
| Buybacks | USD | $44.5bn | $28.0bn | $19.8bn | $30.1bn | $26.2bn | us-gaap:PaymentsForRepurchaseOfCommonStock · 'Repurchases of Class A common stock' |
| Dividends | USD | $0 | $0 | $0 | $5.1bn | $5.3bn | us-gaap:PaymentsOfDividends · 'Payments for dividends and dividend equivalents' |
| Buybacks + dividends / FCF | % | 114.2% | 144.9% | 44.9% | 65.1% | 68.5% | `shareholder_payout / fcf` |
| Debt incl. finance leases | USD | $581m | $10.6bn | $19.1bn | $29.5bn | $59.9bn | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` |
| Cash + marketable securities | USD | $48.0bn | $40.7bn | $65.4bn | $77.8bn | $81.6bn | `cash + st_investments` |
| Net debt (negative = net cash) | USD | -$47.4bn | -$30.1bn | -$46.3bn | -$48.3bn | -$21.7bn | `total_debt - liquid_investments` |
| Operating leases (excluded from debt) | USD | $13.9bn | $16.7bn | $18.8bn | $20.2bn | $25.2bn | us-gaap:OperatingLeaseLiability · 'Present value of lease liabilities' |

Debt policy: notes at carrying value + finance leases + commercial paper, every year. Operating leases are shown but excluded. SBC stays an expense: FCF after SBC is shown beside cash FCF.

### Accounting review ledger

| ID | Year | Metric | Original | Adjustment | Result | Status |
|---|---|---|---:|---:|---:|---|


## Latest reported period (10-Q through 2026-06-30)

Year-to-date values reconciled to the 10-Q statements (26 matched, 3 matched-in-notes, 5 matched-negated, 17 not-checked). TTM = last fiscal year + YTD - prior-year YTD, built only from reconciled inputs.

| Metric | YTD prior year | YTD current | Change | Latest quarter | TTM |
|---|---:|---:|---:|---:|---:|
| Revenue | $89.8bn | $117.1bn | +30.4% | $60.8bn | $228.2bn |
| Operating income | $38.0bn | $41.6bn | +9.6% | $18.8bn | $86.9bn |
| Net income | $35.0bn | $42.6bn | +21.8% | $15.8bn | $68.1bn |
| Gains on equity securities | — | — | — | — | — |
| Operating cash flow | $49.6bn | $64.1bn | +29.2% | $31.9bn* | $130.3bn |
| Capex | $29.5bn | $49.1bn | +66.6% | $30.1bn* | $89.3bn |
| Cash FCF (CFO - capex) | $20.1bn | $15.0bn | -25.5% | $1.7bn* | $41.0bn |
| Depreciation | $8.2bn | $12.4bn | +49.9% | $6.0bn | $22.7bn |
| SBC | $9.0bn | $13.7bn | +52.4% | $7.6bn | $25.1bn |
| Buybacks | $22.9bn | $0 | -100.0% | $0* | $3.3bn |
| Dividends to common | $2.7bn | $2.7bn | +1.6% | $1.4bn | $5.4bn |

\* latest quarter derived as YTD minus the prior YTD (cash flow statements report year-to-date only).

Balance sheet at 2026-06-30:

| Item | Amount |
|---|---:|
| Cash | $15.5bn |
| Marketable securities | $74.8bn |
| Other long-term investments | — |
| Long-term debt | $83.7bn |
| Current portion of debt | $0 |
| Finance leases | — |
| Preferred stock (carrying) | $0 |
| Total equity | $261.2bn |
| Common shares outstanding | — |

## Review queue

- **warn** `restated` Purchases of property and equipment FY2021: 0001326801-22-000018 reported 1.8567e+10, latest filing reports 1.869e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2022: 0001326801-23-000013 reported 3.1431e+10, latest filing reports 3.1186e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2022: 0001326801-24-000012 reported 3.1431e+10, latest filing reports 3.1186e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2023: 0001326801-24-000012 reported 2.7266e+10, latest filing reports 2.7045e+10; confirm the reason in the later filing
- **warn** `missing` Common shares outstanding (all classes) FY2021: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2022: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2023: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2024: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2025: not found under any mapped tag

## Definitions

| Metric | Formula | Years |
|---|---|---|
| capex_intensity | `capex / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| capex_to_depreciation | `capex / dna` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| cash_conversion | `cfo / net_income` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` | FY2022, FY2023, FY2024, FY2025 |
| effective_tax_rate | `income_tax / pretax_income` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| eps_growth | `eps_diluted / prior eps_diluted - 1` | FY2022, FY2023, FY2024, FY2025 |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| fcf_after_sbc | `cfo - capex - sbc` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| fcf_growth | `fcf / prior fcf - 1` | FY2022, FY2023, FY2024, FY2025 |
| fcf_margin | `fcf / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| gross_margin | `gross_profit_calc / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| gross_profit_calc | `revenue - cost_of_revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
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
| sbc_intensity | `sbc / revenue` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| shareholder_payout | `buybacks + dividends` | FY2021, FY2022, FY2023, FY2024, FY2025 |
| total_debt | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` | FY2021, FY2022, FY2023, FY2024, FY2025 |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividendsCommonStock, PaymentsOfOrdinaryDividends, PaymentsOfDividends; preferred_dividends = DividendsPreferredStockCash, PaymentsOfDividendsPreferredStockAndPreferenceStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting (withheld), — missing (not reported), n/a suppressed (formula exists but an input or denominator does not allow it; the reason is in tables/facts.csv and review.html).
