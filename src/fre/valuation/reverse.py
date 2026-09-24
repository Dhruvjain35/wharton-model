"""Reverse DCF: which single assumption makes modeled value equal the market price?

Method: evaluate the model on a grid across documented bounds, bracket every sign
change, then refine each bracket with Brent's method. Zero brackets means no
solution in bounds; several means several solutions; both are reported as such.
The answer is "assumptions consistent with price under this model", not a market
forecast: every other input is held fixed and listed.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, replace

from scipy.optimize import brentq

from .dcf import DCFInputs, ValuationError, value

LABEL = "assumptions consistent with price under this model"

# variable -> (default bounds, how to set it)
VARIABLES = {
    "growth": ((-0.20, 0.60), lambda b, x: replace(b, growth=[x] * len(b.growth))),
    "margin": ((-0.10, 0.80), lambda b, x: replace(b, operating_margin=[x] * len(b.growth), terminal_margin=x)),
    "wacc": ((0.03, 0.25), lambda b, x: replace(b, wacc=x, terminal_wacc=None)),
    "terminal_growth": ((-0.05, 0.08), lambda b, x: replace(b, terminal_growth=x)),
    "sales_to_capital": ((0.1, 10.0), lambda b, x: replace(b, reinvestment=type(b.reinvestment)(x))),
}


@dataclass
class SolveResult:
    status: str  # unique | multiple | none
    roots: list[float]
    monotonic: bool
    lo: float
    hi: float
    grid: int
    xtol: float
    invalid_points: int = 0
    label: str = LABEL
    variable: str = ""
    price: float | None = None
    held_fixed: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def solve(f, lo: float, hi: float, grid: int = 241, xtol: float = 1e-10) -> SolveResult:
    xs = [lo + (hi - lo) * i / (grid - 1) for i in range(grid)]
    ys: list[float | None] = []
    for x in xs:
        try:
            y = f(x)
            ys.append(y if math.isfinite(y) else None)
        except ValuationError:
            ys.append(None)
    roots: list[float] = []
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 == 0:
            roots.append(x0)
        elif y0 * y1 < 0:
            roots.append(brentq(f, x0, x1, xtol=xtol))
    if pts and pts[-1][1] == 0:
        roots.append(pts[-1][0])
    diffs = [b[1] - a[1] for a, b in zip(pts, pts[1:])]
    monotonic = all(d >= 0 for d in diffs) or all(d <= 0 for d in diffs)
    status = "none" if not roots else "unique" if len(roots) == 1 else "multiple"
    return SolveResult(status=status, roots=roots, monotonic=monotonic, lo=lo, hi=hi, grid=grid, xtol=xtol,
                       invalid_points=sum(y is None for y in ys))


def reverse(base: DCFInputs, variable: str, price: float, lo: float | None = None, hi: float | None = None,
            grid: int = 241) -> SolveResult:
    (dlo, dhi), setter = VARIABLES[variable]
    lo, hi = (dlo if lo is None else lo), (dhi if hi is None else hi)
    r = solve(lambda x: value(setter(base, x)).value_per_share - price, lo, hi, grid)
    r.variable, r.price = variable, price
    fixed = {"growth": base.growth, "operating_margin": base.operating_margin, "terminal_margin": base.terminal_margin,
             "wacc": base.wacc, "terminal_growth": base.terminal_growth, "terminal_roic": base.terminal_roic,
             "tax_rate": base.tax_rate, "reinvestment": asdict(base.reinvestment)}
    drop = {"growth": ["growth"], "margin": ["operating_margin", "terminal_margin"], "wacc": ["wacc"],
            "terminal_growth": ["terminal_growth"], "sales_to_capital": ["reinvestment"]}[variable]
    r.held_fixed = {k: v for k, v in fixed.items() if k not in drop}
    return r


def grid2d(base: DCFInputs, var_x: str, xs: list[float], var_y: str, ys: list[float]) -> list[list[float | None]]:
    """Value per share over a two-assumption grid; None where the combination is invalid."""
    sx, sy = VARIABLES[var_x][1], VARIABLES[var_y][1]
    out = []
    for y in ys:
        row = []
        for x in xs:
            try:
                row.append(value(sx(sy(base, y), x)).value_per_share)
            except ValuationError:
                row.append(None)
        out.append(row)
    return out
