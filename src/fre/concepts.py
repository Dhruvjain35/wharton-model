"""Metric catalog: which XBRL tags may supply each reported metric, in priority order.

A tag listed second is only used for a period where the first has no 10-K observation.
Whenever a metric's history mixes tags, the normalizer compares the tags on every
period where both exist and raises a review item if they ever disagree. Tag
equivalence is therefore checked against the company's own data, not assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MetricSpec:
    id: str
    label: str
    kind: Literal["duration", "instant"]
    unit: str
    tags: tuple[str, ...]
    share_basis: bool = False  # per-share or share-count values move with stock splits
    note: str = ""
    optional: bool = False  # an alternative presentation; missing is expected for some companies


_SPECS = [
    # income statement
    MetricSpec("revenue", "Revenue", "duration", "USD",
               ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet")),
    MetricSpec("cost_of_revenue", "Cost of revenue", "duration", "USD",
               ("CostOfRevenue", "CostOfGoodsAndServicesSold")),
    MetricSpec("gross_profit", "Gross profit (as reported)", "duration", "USD", ("GrossProfit",),
               note="Only when the company reports it. Revenue minus cost of revenue is kept as a separate derived metric.", optional=True),
    MetricSpec("rnd", "Research and development", "duration", "USD", ("ResearchAndDevelopmentExpense",)),
    MetricSpec("operating_income", "Operating income", "duration", "USD", ("OperatingIncomeLoss",)),
    MetricSpec("nonoperating_income", "Other income (expense), net", "duration", "USD",
               ("NonoperatingIncomeExpense", "OtherNonoperatingIncomeExpense")),
    MetricSpec("equity_securities_gain", "Gains (losses) on equity securities", "duration", "USD",
               ("EquitySecuritiesFvNiGainLoss",),
               note="Nonoperating mark-to-market gains that flow through net income.", optional=True),
    MetricSpec("pretax_income", "Income before income taxes", "duration", "USD",
               ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments")),
    MetricSpec("income_tax", "Provision for income taxes", "duration", "USD", ("IncomeTaxExpenseBenefit",)),
    MetricSpec("net_income", "Net income (attributable to parent)", "duration", "USD", ("NetIncomeLoss",),
               note="The face-statement net income line."),
    MetricSpec("net_income_to_common", "Net income available to common (EPS numerator)", "duration", "USD",
               ("NetIncomeLossAvailableToCommonStockholdersBasic",),
               note="Differs from net income when preferred dividends or participating securities exist.", optional=True),
    MetricSpec("eps_basic", "Basic EPS", "duration", "USD/shares", ("EarningsPerShareBasic",), share_basis=True),
    MetricSpec("eps_diluted", "Diluted EPS", "duration", "USD/shares", ("EarningsPerShareDiluted",), share_basis=True),
    MetricSpec("shares_basic", "Weighted-average basic shares", "duration", "shares",
               ("WeightedAverageNumberOfSharesOutstandingBasic",), share_basis=True),
    MetricSpec("shares_diluted", "Weighted-average diluted shares", "duration", "shares",
               ("WeightedAverageNumberOfDilutedSharesOutstanding",), share_basis=True),
    # cash flow
    MetricSpec("cfo", "Net cash from operating activities", "duration", "USD",
               ("NetCashProvidedByUsedInOperatingActivities",)),
    MetricSpec("capex", "Purchases of property and equipment", "duration", "USD",
               ("PaymentsToAcquirePropertyPlantAndEquipment",)),
    MetricSpec("dna", "Depreciation and amortization (cash flow)", "duration", "USD",
               ("DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet",
                "DepreciationAndAmortization", "Depreciation"),
               note="If only the Depreciation tag exists, intangible amortization is excluded."),
    MetricSpec("sbc", "Stock-based compensation", "duration", "USD",
               ("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense")),
    MetricSpec("buybacks", "Repurchases of common stock", "duration", "USD",
               ("PaymentsForRepurchaseOfCommonStock",)),
    MetricSpec("dividends", "Dividends paid", "duration", "USD",
               ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock")),
    MetricSpec("cash_taxes", "Income taxes paid, net", "duration", "USD", ("IncomeTaxesPaidNet",)),
    # balance sheet
    MetricSpec("cash", "Cash and cash equivalents", "instant", "USD", ("CashAndCashEquivalentsAtCarryingValue",)),
    MetricSpec("st_investments", "Marketable securities (current)", "instant", "USD",
               ("MarketableSecuritiesCurrent", "ShortTermInvestments", "AvailableForSaleSecuritiesDebtSecuritiesCurrent")),
    MetricSpec("debt_lt_noncurrent", "Long-term debt, noncurrent", "instant", "USD", ("LongTermDebtNoncurrent",), optional=True),
    MetricSpec("debt_lt_current", "Long-term debt, current portion", "instant", "USD", ("LongTermDebtCurrent",)),
    MetricSpec("debt_and_finance_lease_noncurrent", "Long-term debt incl. finance leases, noncurrent", "instant", "USD",
               ("LongTermDebtAndCapitalLeaseObligations",),
               note="Alphabet's balance-sheet debt line through the FY2023 10-K; it includes finance leases. "
                    "The generic LongTermDebt tag is excluded: its meaning changed between Alphabet filings.", optional=True),
    MetricSpec("commercial_paper", "Commercial paper", "instant", "USD", ("CommercialPaper",)),
    MetricSpec("operating_lease_liability", "Operating lease liabilities", "instant", "USD", ("OperatingLeaseLiability",)),
    MetricSpec("finance_lease_liability", "Finance lease liabilities", "instant", "USD", ("FinanceLeaseLiability",)),
    MetricSpec("finance_lease_liability_current", "Finance lease liabilities, current", "instant", "USD",
               ("FinanceLeaseLiabilityCurrent",), optional=True),
    MetricSpec("accounts_receivable", "Accounts receivable, net", "instant", "USD", ("AccountsReceivableNetCurrent",)),
    MetricSpec("other_lt_investments", "Other long-term investments", "instant", "USD", ("OtherLongTermInvestments",),
               note="Alphabet presents this line as non-marketable securities.", optional=True),
    MetricSpec("preferred_equity", "Preferred stock (carrying value)", "instant", "USD",
               ("ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue", "PreferredStockValue"), optional=True),
    MetricSpec("shares_outstanding", "Common shares outstanding (all classes)", "instant", "shares",
               ("CommonStockSharesOutstanding",), share_basis=True),
    MetricSpec("unvested_rsus", "Unvested restricted stock units", "instant", "shares",
               ("ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber",),
               share_basis=True, optional=True),
    MetricSpec("assets", "Total assets", "instant", "USD", ("Assets",)),
    MetricSpec("liabilities", "Total liabilities", "instant", "USD", ("Liabilities",)),
    MetricSpec("equity", "Total stockholders' equity", "instant", "USD", ("StockholdersEquity",)),
]

METRICS: dict[str, MetricSpec] = {s.id: s for s in _SPECS}
