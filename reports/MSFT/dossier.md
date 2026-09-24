# MICROSOFT CORPORATION (MSFT) — fundamentals dossier

Fiscal years FY2022–FY2026 (fiscal year ends 06-30) · run `06da42da70c4` · code `41bc18bd` (uncommitted changes) · created 2026-09-24T06:25:37+00:00

**Data vintage: current (latest restated filings).** Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 132 derived, 51 missing, 158 reported
- Reconciliation to filed statements: 118 matched, 22 matched-in-notes, 3 matched-in-text, 15 matched-negated, 42 not-checked
- Review queue: 0 blocking, 0 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $198.3bn in FY2022 to $331.8bn in FY2026, a compound annual rate of 13.7% over 4 years.
Operating margin expanded from 42.1% to 46.8% (+473 bp).

| Metric | Unit | FY2022 (Jun 30, 2022) | FY2023 (Jun 30, 2023) | FY2024 (Jun 30, 2024) | FY2025 (Jun 30, 2025) | FY2026 (Jun 30, 2026) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Revenue | USD | $198.3bn | $211.9bn | $245.1bn | $281.7bn | $331.8bn | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax · 'Revenue' |
| Revenue growth | % | n/a | +6.9% | +15.7% | +14.9% | +17.8% | `revenue / prior revenue - 1` |
| Gross margin | % | 68.4% | 68.9% | 69.8% | 68.8% | 67.9% | `gross_profit / revenue` |
| Operating margin | % | 42.1% | 41.8% | 44.6% | 45.6% | 46.8% | `operating_income / revenue` |
| Net margin | % | 36.7% | 34.1% | 36.0% | 36.1% | 40.3% | `net_income / revenue` |
| R&D / revenue | % | 12.4% | 12.8% | 12.0% | 11.5% | 10.7% | `rnd / revenue` |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2022->FY2023: diluted EPS +0.3%; net income -0.5%, diluted shares -0.9% — net income fell; EPS rose only because the share count fell. It was bought with $22.2bn of repurchases while SBC was $9.6bn.
- FY2023->FY2024: diluted EPS +21.9%; net income +21.8%, diluted shares -0.0% — share-count reduction explains 0.2% of EPS growth (log basis). It was bought with $17.3bn of repurchases while SBC was $10.7bn.
- FY2024->FY2025: diluted EPS +15.6%; net income +15.5%, diluted shares -0.1% — share-count reduction explains 0.4% of EPS growth (log basis). It was bought with $18.4bn of repurchases while SBC was $12.0bn.
- FY2025->FY2026: diluted EPS +31.6%; net income +31.3%, diluted shares -0.2% — share-count reduction explains 0.6% of EPS growth (log basis). It was bought with $22.3bn of repurchases while SBC was $12.4bn.

| Metric | Unit | FY2022 (Jun 30, 2022) | FY2023 (Jun 30, 2023) | FY2024 (Jun 30, 2024) | FY2025 (Jun 30, 2025) | FY2026 (Jun 30, 2026) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Net income | USD | $72.7bn | $72.4bn | $88.1bn | $101.8bn | $133.7bn | us-gaap:NetIncomeLoss · 'Net income' |
| Diluted shares (wtd. avg.) | shares | 7,540m | 7,472m | 7,469m | 7,465m | 7,453m | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding · 'Diluted' |
| Diluted EPS | USD/share | $9.65 | $9.68 | $11.80 | $13.64 | $17.95 | us-gaap:EarningsPerShareDiluted · 'Diluted' |
| EPS growth | % | n/a | +0.3% | +21.9% | +15.6% | +31.6% | `eps_diluted / prior eps_diluted - 1` |
| Diluted share change | % | n/a | -0.9% | -0.0% | -0.1% | -0.2% | `shares_diluted / prior shares_diluted - 1` |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +83.9% from FY2022 to FY2026; cash FCF changed +2.8% ($65.1bn to $67.0bn).
Capex went from $23.9bn to $115.9bn (4.9x), reaching 34.9% of revenue and 3.38x depreciation in FY2026.

| Metric | Unit | FY2022 (Jun 30, 2022) | FY2023 (Jun 30, 2023) | FY2024 (Jun 30, 2024) | FY2025 (Jun 30, 2025) | FY2026 (Jun 30, 2026) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Operating cash flow | USD | $89.0bn | $87.6bn | $118.5bn | $136.2bn | $182.9bn | us-gaap:NetCashProvidedByUsedInOperatingActivities · 'Net cash from operations' |
| CFO / net income | x | 1.22x | 1.21x | 1.35x | 1.34x | 1.37x | `cfo / net_income` |
| Capex (cash) | USD | $23.9bn | $28.1bn | $44.5bn | $64.6bn | $115.9bn | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment · 'Additions to property and equipment' |
| Cash FCF (CFO - capex) | USD | $65.1bn | $59.5bn | $74.1bn | $71.6bn | $67.0bn | `cfo - capex (cash FCF; not unlevered FCFF)` |
| FCF margin | % | 32.9% | 28.1% | 30.2% | 25.4% | 20.2% | `fcf / revenue` |
| FCF after SBC | USD | $57.6bn | $49.9bn | $63.3bn | $59.6bn | $54.6bn | `cfo - capex - sbc` |

## 4. What investment does growth require?

| Metric | Unit | FY2022 (Jun 30, 2022) | FY2023 (Jun 30, 2023) | FY2024 (Jun 30, 2024) | FY2025 (Jun 30, 2025) | FY2026 (Jun 30, 2026) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Capex / revenue | % | 12.0% | 13.3% | 18.1% | 22.9% | 34.9% | `capex / revenue` |
| Depreciation (as tagged; see definitions) | USD | $12.6bn | $11.0bn | $15.2bn | $22.0bn | $34.3bn | us-gaap:Depreciation · 'Depreciation expense' |
| Capex / depreciation | x | 1.90x | 2.56x | 2.93x | 2.93x | 3.38x | `capex / dna` |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | Unit | FY2022 (Jun 30, 2022) | FY2023 (Jun 30, 2023) | FY2024 (Jun 30, 2024) | FY2025 (Jun 30, 2025) | FY2026 (Jun 30, 2026) | Definition / source |
|---|---|---:|---:|---:|---:|---:|---|
| Stock-based compensation | USD | $7.5bn | $9.6bn | $10.7bn | $12.0bn | $12.4bn | us-gaap:ShareBasedCompensation · 'Stock-based compensation expense' |
| SBC / revenue | % | 3.8% | 4.5% | 4.4% | 4.3% | 3.7% | `sbc / revenue` |
| Non-operating income / pretax | % | 0.4% | 0.9% | -1.5% | -4.0% | 6.4% | `nonoperating_income / pretax_income` |
| Effective tax rate | % | 13.1% | 19.0% | 18.2% | 17.6% | 19.4% | `income_tax / pretax_income` |
| ROIC (proposed definition) | % | n/a | n/a | n/a | n/a | n/a | `nopat / ((invested_capital + prior invested_capital) / 2)` |
| Buybacks | USD | $32.7bn | $22.2bn | $17.3bn | $18.4bn | $22.3bn | us-gaap:PaymentsForRepurchaseOfCommonStock · 'Common stock repurchased' |
| Dividends | USD | $18.1bn | $19.8bn | $21.8bn | $24.1bn | $26.4bn | us-gaap:PaymentsOfDividendsCommonStock · 'Common stock cash dividends paid' |
| Buybacks + dividends / FCF | % | 78.0% | 70.7% | 52.7% | 59.4% | 72.7% | `shareholder_payout / fcf` |
| Debt incl. finance leases | USD | $64.7bn | $64.3bn | $78.8bn | $89.3bn | $106.9bn | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` |
| Cash + marketable securities | USD | $104.8bn | $111.3bn | $75.5bn | $94.6bn | $76.8bn | `cash + st_investments` |
| Net debt (negative = net cash) | USD | -$40.1bn | -$47.0bn | $3.2bn | -$5.2bn | $30.0bn | `total_debt - liquid_investments` |
| Operating leases (excluded from debt) | USD | $13.7bn | $15.1bn | $19.1bn | $22.9bn | $21.9bn | us-gaap:OperatingLeaseLiability · 'Total operating lease liabilities' |

Debt policy: notes at carrying value + finance leases + commercial paper, every year. Operating leases are shown but excluded. SBC stays an expense: FCF after SBC is shown beside cash FCF.

### Accounting review ledger

| ID | Year | Metric | Original | Adjustment | Result | Status |
|---|---|---|---:|---:|---:|---|


## Latest reported period

No 10-Q had been filed after the last 10-K in this run's data (as of its vintage).

## Review queue

- Nothing open.

## Definitions

| Metric | Formula | Years |
|---|---|---|
| capex_intensity | `capex / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| capex_to_depreciation | `capex / dna` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| cash_conversion | `cfo / net_income` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` | FY2023, FY2024, FY2025, FY2026 |
| effective_tax_rate | `income_tax / pretax_income` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| eps_growth | `eps_diluted / prior eps_diluted - 1` | FY2023, FY2024, FY2025, FY2026 |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| fcf_after_sbc | `cfo - capex - sbc` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| fcf_growth | `fcf / prior fcf - 1` | FY2023, FY2024, FY2025, FY2026 |
| fcf_margin | `fcf / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| gross_margin | `gross_profit / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| gross_profit_calc | `revenue - cost_of_revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| liquid_investments | `cash + st_investments` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| net_debt | `total_debt - liquid_investments` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| net_income_growth | `net_income / prior net_income - 1` | FY2023, FY2024, FY2025, FY2026 |
| net_margin | `net_income / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| nonoperating_share_of_pretax | `nonoperating_income / pretax_income` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| nopat | `operating_income * (1 - effective_tax_rate)` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| operating_income_growth | `operating_income / prior operating_income - 1` | FY2023, FY2024, FY2025, FY2026 |
| operating_margin | `operating_income / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| payout_to_fcf | `shareholder_payout / fcf` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| revenue_cagr | `(revenue FY2026 / revenue FY2022)^(1/4) - 1` | FY2026 |
| revenue_growth | `revenue / prior revenue - 1` | FY2023, FY2024, FY2025, FY2026 |
| rnd_intensity | `rnd / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| sbc_intensity | `sbc / revenue` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| shareholder_payout | `buybacks + dividends` | FY2022, FY2023, FY2024, FY2025, FY2026 |
| total_debt | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` | FY2022, FY2023, FY2024, FY2025, FY2026 |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividendsCommonStock, PaymentsOfOrdinaryDividends, PaymentsOfDividends; preferred_dividends = DividendsPreferredStockCash, PaymentsOfDividendsPreferredStockAndPreferenceStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting (withheld), — missing (not reported), n/a suppressed (formula exists but an input or denominator does not allow it; the reason is in tables/facts.csv and review.html).
