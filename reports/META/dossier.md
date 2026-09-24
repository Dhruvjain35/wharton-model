# Meta Platforms, Inc. (META) — fundamentals dossier

Fiscal years FY2021–FY2025 (fiscal year ends 12-31) · run `b2450ca37bbd` · code `c8d27307` (uncommitted changes) · created 2026-09-24T05:52:21+00:00

Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 127 derived, 48 missing, 146 reported
- Reconciliation to filed statements: 2 from-notes, 115 matched, 15 matched-in-notes, 14 matched-negated, 49 not-checked
- Review queue: 2 blocking, 11 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $117.9bn in FY2021 to $201.0bn in FY2025, a 14.3% compound annual rate over 4 years.
Operating margin expanded from 39.6% to 41.4% (+179 bp).

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Revenue | $117.9bn | $116.6bn | $134.9bn | $164.5bn | $201.0bn |
| Revenue growth | — | -1.1% | +15.7% | +21.9% | +22.2% |
| Gross margin | 80.8% | 78.3% | 80.8% | 81.7% | 82.0% |
| Operating margin | 39.6% | 24.8% | 34.7% | 42.2% | 41.4% |
| Net margin | 33.4% | 19.9% | 29.0% | 37.9% | 30.1% |
| R&D / revenue | 20.9% | 30.3% | 28.5% | 26.7% | 28.5% |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2021->FY2022: diluted EPS -37.6%; net income -41.1%, diluted shares -5.5%. It was bought with $28.0bn of repurchases while SBC was $12.0bn.
- FY2022->FY2023: diluted EPS +73.1%; net income +68.5%, diluted shares -2.7% — share-count reduction explains 5.0% of EPS growth (log basis). It was bought with $19.8bn of repurchases while SBC was $14.0bn.
- FY2023->FY2024: diluted EPS +60.5%; net income +59.5%, diluted shares -0.6% — share-count reduction explains 1.2% of EPS growth (log basis). It was bought with $30.1bn of repurchases while SBC was $16.7bn.
- FY2024->FY2025: diluted EPS -1.6%; net income -3.1%, diluted shares -1.5%. It was bought with $26.2bn of repurchases while SBC was $20.4bn.

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Net income | $39.4bn | $23.2bn | $39.1bn | $62.4bn | $60.5bn |
| Diluted shares (wtd. avg.) | 2,859m | 2,702m | 2,629m | 2,614m | 2,574m |
| Diluted EPS | $13.77 | $8.59 | $14.87 | $23.86 | $23.49 |
| EPS growth | — | -37.6% | +73.1% | +60.5% | -1.6% |
| Diluted share change | — | -5.5% | -2.7% | -0.6% | -1.5% |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +53.6% from FY2021 to FY2025; cash FCF changed +18.2% ($39.0bn to $46.1bn).
Capex went from $18.7bn to $69.7bn (3.7x), reaching 34.7% of revenue and 3.74x depreciation in FY2025.

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Operating cash flow | $57.7bn | $50.5bn | $71.1bn | $91.3bn | $115.8bn |
| CFO / net income | 1.47x | 2.18x | 1.82x | 1.46x | 1.92x |
| Capex (cash) | $18.7bn | $31.2bn | $27.0bn | $37.3bn | $69.7bn |
| Cash FCF (CFO - capex) | $39.0bn | $19.3bn | $44.1bn | $54.1bn | $46.1bn |
| FCF margin | 33.1% | 16.5% | 32.7% | 32.9% | 22.9% |
| FCF after SBC | $29.8bn | $7.3bn | $30.0bn | $37.4bn | $25.7bn |

## 4. What investment does growth require?

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Capex / revenue | 15.8% | 26.7% | 20.0% | 22.6% | 34.7% |
| Depreciation (cash flow) | $8.0bn | $8.7bn | $11.2bn | $15.5bn | $18.6bn |
| Capex / depreciation | 2.35x | 3.59x | 2.42x | 2.40x | 3.74x |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| Stock-based compensation | $9.2bn | $12.0bn | $14.0bn | $16.7bn | $20.4bn |
| SBC / revenue | 7.8% | 10.3% | 10.4% | 10.1% | 10.2% |
| Non-operating income / pretax | 1.1% | -0.4% | 1.4% | 1.8% | 3.1% |
| Effective tax rate | 16.7% | 19.5% | 17.6% | 11.8% | 29.6% |
| Buybacks | $44.5bn | $28.0bn | $19.8bn | $30.1bn | $26.2bn |
| Dividends | $0 | $0 | $0 | $5.1bn | $5.3bn |
| Buybacks + dividends / FCF | 114.2% | 144.9% | 44.9% | 65.1% | 68.5% |
| Debt incl. finance leases | — | $10.6bn | $19.1bn | $29.5bn | $59.9bn |
| Cash + marketable securities | $48.0bn | $40.7bn | $65.4bn | $77.8bn | $81.6bn |
| Net debt (negative = net cash) | — | -$30.1bn | -$46.3bn | -$48.3bn | -$21.7bn |
| Operating leases (excluded from debt) | $13.9bn | $16.7bn | $18.8bn | $20.2bn | $25.2bn |

Debt policy: notes at carrying value + finance leases + commercial paper, every year. Operating leases are shown but excluded. SBC stays an expense: FCF after SBC is shown beside cash FCF.

### Accounting review ledger

| ID | Year | Metric | Original | Adjustment | Result | Status |
|---|---|---|---:|---:|---:|---|


## Review queue

- **block** `attestation-failed` Long-term debt, current portion FY2021: cannot attest zero, no filed statement covering this period was found to check against
- **block** `attestation-failed` Commercial paper FY2021: cannot attest zero, no filed statement covering this period was found to check against
- **warn** `restated` Purchases of property and equipment FY2021: 0001326801-22-000018 reported 1.8567e+10, latest filing reports 1.869e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2022: 0001326801-23-000013 reported 3.1431e+10, latest filing reports 3.1186e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2022: 0001326801-24-000012 reported 3.1431e+10, latest filing reports 3.1186e+10; confirm the reason in the later filing
- **warn** `restated` Purchases of property and equipment FY2023: 0001326801-24-000012 reported 2.7266e+10, latest filing reports 2.7045e+10; confirm the reason in the later filing
- **warn** `missing` Long-term debt, current portion FY2021: not found under any mapped tag
- **warn** `missing` Commercial paper FY2021: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2021: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2022: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2023: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2024: not found under any mapped tag
- **warn** `missing` Common shares outstanding (all classes) FY2025: not found under any mapped tag

## Definitions

| Metric | Formula |
|---|---|
| gross_profit_calc | `revenue - cost_of_revenue` |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` |
| fcf_after_sbc | `cfo - capex - sbc` |
| liquid_investments | `cash + st_investments` |
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
| total_debt | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` |
| net_debt | `total_debt - liquid_investments` |
| revenue_growth | `revenue / prior revenue - 1` |
| operating_income_growth | `operating_income / prior operating_income - 1` |
| net_income_growth | `net_income / prior net_income - 1` |
| fcf_growth | `fcf / prior fcf - 1` |
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` |
| eps_growth | `eps_diluted / prior eps_diluted - 1` |
| revenue_cagr | `(revenue FY2025 / revenue FY2021)^(1/4) - 1` |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividends, PaymentsOfDividendsCommonStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting, — missing or suppressed (see facts.csv notes for the reason).
