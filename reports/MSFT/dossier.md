# MICROSOFT CORPORATION (MSFT) — fundamentals dossier

Fiscal years FY2022–FY2026 (fiscal year ends 06-30) · run `14b718e3bced` · code `c8d27307` (uncommitted changes) · created 2026-09-24T05:52:20+00:00

Every figure below comes from SEC filings through pinned snapshots and deterministic Python. `fre verify-run` recomputes this run and proves the digest.

## Data quality

- Facts: 122 derived, 41 missing, 158 reported
- Reconciliation to filed statements: 5 from-notes, 118 matched, 20 matched-in-notes, 15 matched-negated, 37 not-checked
- Review queue: 0 blocking, 0 warnings
- Ledger quotes verified against filing text: all

## 1. Is the business growing, and is profitability improving?

Revenue went from $198.3bn in FY2022 to $331.8bn in FY2026, a 13.7% compound annual rate over 4 years.
Operating margin expanded from 42.1% to 46.8% (+473 bp).

| Metric | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---:|---:|---:|---:|---:|
| Revenue | $198.3bn | $211.9bn | $245.1bn | $281.7bn | $331.8bn |
| Revenue growth | — | +6.9% | +15.7% | +14.9% | +17.8% |
| Gross margin | 68.4% | 68.9% | 69.8% | 68.8% | 67.9% |
| Operating margin | 42.1% | 41.8% | 44.6% | 45.6% | 46.8% |
| Net margin | 36.7% | 34.1% | 36.0% | 36.1% | 40.3% |
| R&D / revenue | 12.4% | 12.8% | 12.0% | 11.5% | 10.7% |

## 2. Are EPS gains coming from the business, the share count, or unusual items?

- FY2022->FY2023: diluted EPS +0.3%; net income -0.5%, diluted shares -0.9% — share-count reduction explains 291.9% of EPS growth (log basis). It was bought with $22.2bn of repurchases while SBC was $9.6bn.
- FY2023->FY2024: diluted EPS +21.9%; net income +21.8%, diluted shares -0.0% — share-count reduction explains 0.2% of EPS growth (log basis). It was bought with $17.3bn of repurchases while SBC was $10.7bn.
- FY2024->FY2025: diluted EPS +15.6%; net income +15.5%, diluted shares -0.1% — share-count reduction explains 0.4% of EPS growth (log basis). It was bought with $18.4bn of repurchases while SBC was $12.0bn.
- FY2025->FY2026: diluted EPS +31.6%; net income +31.3%, diluted shares -0.2% — share-count reduction explains 0.6% of EPS growth (log basis). It was bought with $22.3bn of repurchases while SBC was $12.4bn.

| Metric | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---:|---:|---:|---:|---:|
| Net income | $72.7bn | $72.4bn | $88.1bn | $101.8bn | $133.7bn |
| Diluted shares (wtd. avg.) | 7,540m | 7,472m | 7,469m | 7,465m | 7,453m |
| Diluted EPS | $9.65 | $9.68 | $11.80 | $13.64 | $17.95 |
| EPS growth | — | +0.3% | +21.9% | +15.6% | +31.6% |
| Diluted share change | — | -0.9% | -0.0% | -0.1% | -0.2% |

EPS bridge identity: EPS factor ≈ net-income factor / diluted-share factor (approximation: the numerator and share basis are not reconciled share class by share class).

## 3. How much accounting profit becomes cash?

Net income changed +83.9% from FY2022 to FY2026; cash FCF changed +2.8% ($65.1bn to $67.0bn).
Capex went from $23.9bn to $115.9bn (4.9x), reaching 34.9% of revenue and 3.38x depreciation in FY2026.

| Metric | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---:|---:|---:|---:|---:|
| Operating cash flow | $89.0bn | $87.6bn | $118.5bn | $136.2bn | $182.9bn |
| CFO / net income | 1.22x | 1.21x | 1.35x | 1.34x | 1.37x |
| Capex (cash) | $23.9bn | $28.1bn | $44.5bn | $64.6bn | $115.9bn |
| Cash FCF (CFO - capex) | $65.1bn | $59.5bn | $74.1bn | $71.6bn | $67.0bn |
| FCF margin | 32.9% | 28.1% | 30.2% | 25.4% | 20.2% |
| FCF after SBC | $57.6bn | $49.9bn | $63.3bn | $59.6bn | $54.6bn |

## 4. What investment does growth require?

| Metric | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---:|---:|---:|---:|---:|
| Capex / revenue | 12.0% | 13.3% | 18.1% | 22.9% | 34.9% |
| Depreciation (cash flow) | $12.6bn | $11.0bn | $15.2bn | $22.0bn | $34.3bn |
| Capex / depreciation | 1.90x | 2.56x | 2.93x | 2.93x | 3.38x |

## 5. Could debt, stock compensation, or accounting choices mislead?

| Metric | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---:|---:|---:|---:|---:|
| Stock-based compensation | $7.5bn | $9.6bn | $10.7bn | $12.0bn | $12.4bn |
| SBC / revenue | 3.8% | 4.5% | 4.4% | 4.3% | 3.7% |
| Non-operating income / pretax | 0.4% | 0.9% | -1.5% | -4.0% | 6.4% |
| Effective tax rate | 13.1% | 19.0% | 18.2% | 17.6% | 19.4% |
| Buybacks | $32.7bn | $22.2bn | $17.3bn | $18.4bn | $22.3bn |
| Dividends | $18.1bn | $19.8bn | $21.8bn | $24.1bn | $26.4bn |
| Buybacks + dividends / FCF | 78.0% | 70.7% | 52.7% | 59.4% | 72.7% |
| Debt incl. finance leases | $64.7bn | $64.3bn | $78.8bn | $89.3bn | $106.9bn |
| Cash + marketable securities | $104.8bn | $111.3bn | $75.5bn | $94.6bn | $76.8bn |
| Net debt (negative = net cash) | -$40.1bn | -$47.0bn | $3.2bn | -$5.2bn | $30.0bn |
| Operating leases (excluded from debt) | $13.7bn | $15.1bn | $19.1bn | $22.9bn | $21.9bn |

Debt policy: notes at carrying value + finance leases + commercial paper, every year. Operating leases are shown but excluded. SBC stays an expense: FCF after SBC is shown beside cash FCF.

### Accounting review ledger

| ID | Year | Metric | Original | Adjustment | Result | Status |
|---|---|---|---:|---:|---:|---|


## Review queue

- Nothing open.

## Definitions

| Metric | Formula |
|---|---|
| gross_profit_calc | `revenue - cost_of_revenue` |
| fcf | `cfo - capex (cash FCF; not unlevered FCFF)` |
| fcf_after_sbc | `cfo - capex - sbc` |
| liquid_investments | `cash + st_investments` |
| total_debt | `debt_lt_noncurrent + debt_lt_current + finance_lease_liability + commercial_paper` |
| net_debt | `total_debt - liquid_investments` |
| shareholder_payout | `buybacks + dividends` |
| gross_margin | `gross_profit / revenue` |
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
| diluted_share_change | `shares_diluted / prior shares_diluted - 1` |
| eps_growth | `eps_diluted / prior eps_diluted - 1` |
| revenue_cagr | `(revenue FY2026 / revenue FY2022)^(1/4) - 1` |

Reported metrics map to XBRL tags: revenue = Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet; cost_of_revenue = CostOfRevenue, CostOfGoodsAndServicesSold; gross_profit = GrossProfit; rnd = ResearchAndDevelopmentExpense; operating_income = OperatingIncomeLoss; nonoperating_income = NonoperatingIncomeExpense, OtherNonoperatingIncomeExpense; equity_securities_gain = EquitySecuritiesFvNiGainLoss; pretax_income = IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments; income_tax = IncomeTaxExpenseBenefit; net_income = NetIncomeLoss; net_income_to_common = NetIncomeLossAvailableToCommonStockholdersBasic; eps_basic = EarningsPerShareBasic; eps_diluted = EarningsPerShareDiluted; shares_basic = WeightedAverageNumberOfSharesOutstandingBasic; shares_diluted = WeightedAverageNumberOfDilutedSharesOutstanding; cfo = NetCashProvidedByUsedInOperatingActivities; capex = PaymentsToAcquirePropertyPlantAndEquipment; dna = DepreciationDepletionAndAmortization, DepreciationAmortizationAndAccretionNet, DepreciationAndAmortization, Depreciation; sbc = ShareBasedCompensation, AllocatedShareBasedCompensationExpense; buybacks = PaymentsForRepurchaseOfCommonStock; dividends = PaymentsOfDividends, PaymentsOfDividendsCommonStock; cash_taxes = IncomeTaxesPaidNet; cash = CashAndCashEquivalentsAtCarryingValue; st_investments = MarketableSecuritiesCurrent, ShortTermInvestments, AvailableForSaleSecuritiesDebtSecuritiesCurrent; debt_lt_noncurrent = LongTermDebtNoncurrent; debt_lt_current = LongTermDebtCurrent; debt_and_finance_lease_noncurrent = LongTermDebtAndCapitalLeaseObligations; commercial_paper = CommercialPaper; operating_lease_liability = OperatingLeaseLiability; finance_lease_liability = FinanceLeaseLiability; finance_lease_liability_current = FinanceLeaseLiabilityCurrent; accounts_receivable = AccountsReceivableNetCurrent; other_lt_investments = OtherLongTermInvestments; preferred_equity = ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue, PreferredStockValue; shares_outstanding = CommonStockSharesOutstanding; unvested_rsus = ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber; assets = Assets; liabilities = Liabilities; equity = StockholdersEquity

Legend: † analyst-adjusted, ‼ conflicting, — missing or suppressed (see facts.csv notes for the reason).
