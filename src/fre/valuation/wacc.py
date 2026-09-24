"""Weighted average cost of capital from explicitly supplied components (PRD B4).

Every input arrives from the reviewed valuation file with its own source or
rationale. This module only does the arithmetic; it never estimates beta, the
equity risk premium, or anything else.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class WaccInputs:
    risk_free: float
    equity_risk_premium: float
    beta: float
    pretax_cost_of_debt: float
    tax_rate: float
    equity_value: float  # market value of all common classes
    debt_value: float
    preferred_value: float = 0.0
    cost_of_preferred: float | None = None


@dataclass(frozen=True)
class Wacc:
    inputs: WaccInputs
    cost_of_equity: float
    after_tax_cost_of_debt: float
    weights: dict
    wacc: float

    def to_dict(self) -> dict:
        return asdict(self)


def compute(i: WaccInputs) -> Wacc:
    if i.preferred_value and i.cost_of_preferred is None:
        raise ValueError("preferred capital needs its own cost (cost_of_preferred)")
    ke = i.risk_free + i.beta * i.equity_risk_premium
    kd = i.pretax_cost_of_debt * (1 - i.tax_rate)
    total = i.equity_value + i.debt_value + i.preferred_value
    w = {"equity": i.equity_value / total, "debt": i.debt_value / total, "preferred": i.preferred_value / total}
    wacc = w["equity"] * ke + w["debt"] * kd + w["preferred"] * (i.cost_of_preferred or 0.0)
    return Wacc(inputs=i, cost_of_equity=ke, after_tax_cost_of_debt=kd, weights=w, wacc=wacc)
