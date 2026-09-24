"""Consolidated FCFF DCF, exactly the calculation contract in PRD B2.

    Revenue_t          = Revenue_(t-1) * (1 + Growth_t)
    EBIT_t             = Revenue_t * OperatingMargin_t
    NOPAT_t            = EBIT_t - OperatingCashTaxes_t          (no refund on losses)
    NetReinvestment_t  = Capex_t - D&A_t + dNWC_t               (explicit method)
                       = max(dRevenue_t, 0) / SalesToCapital    (sales-to-capital method)
    FCFF_t             = NOPAT_t - NetReinvestment_t

    TerminalNOPAT      = Revenue_N * (1 + g) * TerminalMargin * (1 - TerminalTax)
    ReinvestmentRate   = g / TerminalROIC
    TerminalFCFF       = TerminalNOPAT * (1 - ReinvestmentRate)
    TerminalValue      = TerminalFCFF / (TerminalWACC - g)

    OperatingEV  = sum(FCFF_t * DF_t) + TerminalValue * DF_N
    EquityValue  = OperatingEV + ExcessCash + NonoperatingAssets - Debt - OtherSeniorClaims
    ValuePerShare = EquityValue / DilutedShares

Discounting is end of period. With stub < 1 (valuation date inside forecast year 1),
only the remaining fraction of year-1 FCFF is counted and every period shifts by
(1 - stub): the balance sheet at the valuation date already holds the cash earned
before it. SBC stays inside operating margin (an expense) and is never added back.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


class ValuationError(ValueError):
    pass


@dataclass(frozen=True)
class Explicit:
    capex_pct: list[float]  # of revenue, per forecast year
    dna_pct: list[float]
    nwc_pct: float  # operating NWC (excludes cash and financing debt) as a share of revenue
    base_nwc: float  # operating NWC at the end of the base year


@dataclass(frozen=True)
class SalesToCapital:
    ratio: float  # incremental revenue per unit of net reinvestment


@dataclass(frozen=True)
class Bridge:
    excess_cash: float
    nonoperating_assets: float
    debt: float
    other_senior_claims: float
    diluted_shares: float


@dataclass
class DCFInputs:
    base_revenue: float
    growth: list[float]
    operating_margin: list[float]
    tax_rate: float | list[float]
    reinvestment: Explicit | SalesToCapital
    wacc: float
    terminal_growth: float
    terminal_margin: float
    terminal_roic: float
    bridge: Bridge
    terminal_wacc: float | None = None
    terminal_tax_rate: float | None = None
    stub: float = 1.0
    risk_free: float | None = None  # for the terminal-growth plausibility flag
    interest_expense: list[float] | None = None  # memo only: levered FCF
    net_borrowing: list[float] | None = None  # memo only


@dataclass(frozen=True)
class Row:
    year: int
    revenue: float
    ebit: float
    taxes: float
    nopat: float
    capex: float | None
    dna: float | None
    delta_nwc: float | None
    net_reinvestment: float
    fcff: float
    fcff_counted: float
    discount_factor: float
    pv: float
    levered_fcf_memo: float | None


@dataclass
class DCFResult:
    inputs: DCFInputs
    rows: list[Row]
    terminal_nopat: float
    reinvestment_rate: float
    terminal_fcff: float
    terminal_value: float
    pv_terminal: float
    enterprise_value: float
    equity_value: float
    value_per_share: float
    terminal_share: float
    implied_exit_ev_ebit: float | None = None  # terminal value / year N+1 EBIT: the multiple the perpetuity implies
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["inputs"]["reinvestment"] = {"method": type(self.inputs.reinvestment).__name__,
                                       **asdict(self.inputs.reinvestment)}
        return d


def _per_year(x: float | list[float], n: int, name: str) -> list[float]:
    if isinstance(x, (int, float)):
        return [float(x)] * n
    if len(x) != n:
        raise ValuationError(f"{name} has {len(x)} values for {n} forecast years")
    return [float(v) for v in x]


def value(inp: DCFInputs) -> DCFResult:
    n = len(inp.growth)
    if n == 0:
        raise ValuationError("need at least one forecast year")
    if isinstance(inp.reinvestment, (list, tuple)):
        raise ValuationError("choose exactly one reinvestment method, not both (PRD B1)")
    margins = _per_year(inp.operating_margin, n, "operating_margin")
    taxes = _per_year(inp.tax_rate, n, "tax_rate")
    t_wacc = inp.wacc if inp.terminal_wacc is None else inp.terminal_wacc
    t_tax = taxes[-1] if inp.terminal_tax_rate is None else inp.terminal_tax_rate
    g = inp.terminal_growth
    if g >= t_wacc:
        raise ValuationError(f"terminal growth {g:.2%} must be below terminal WACC {t_wacc:.2%}")
    if inp.terminal_roic <= 0 or inp.terminal_roic <= g:
        raise ValuationError(f"terminal ROIC {inp.terminal_roic:.2%} must exceed terminal growth {g:.2%}: "
                             "growth is not free")
    if inp.bridge.diluted_shares <= 0:
        raise ValuationError("diluted share base must be positive")
    if not 0 < inp.stub <= 1:
        raise ValuationError("stub must be in (0, 1]")
    ex = inp.reinvestment if isinstance(inp.reinvestment, Explicit) else None
    if ex:
        _per_year(ex.capex_pct, n, "capex_pct")
        _per_year(ex.dna_pct, n, "dna_pct")
    elif inp.reinvestment.ratio <= 0:
        raise ValuationError("sales-to-capital ratio must be positive")
    interest = _per_year(inp.interest_expense, n, "interest_expense") if inp.interest_expense else None
    borrowing = _per_year(inp.net_borrowing, n, "net_borrowing") if inp.net_borrowing else None

    flags: list[str] = []
    rows: list[Row] = []
    prev_rev, prev_nwc = inp.base_revenue, (ex.base_nwc if ex else None)
    for i in range(n):
        rev = prev_rev * (1 + inp.growth[i])
        ebit = rev * margins[i]
        tax = max(ebit, 0.0) * taxes[i]
        if ebit < 0:
            flags.append(f"Year {i + 1}: operating loss taxed at zero; loss carryforwards are not modeled")
        nopat = ebit - tax
        if ex:
            capex, dna = rev * ex.capex_pct[i], rev * ex.dna_pct[i]
            nwc = rev * ex.nwc_pct
            d_nwc = nwc - prev_nwc
            reinv = capex - dna + d_nwc
            prev_nwc = nwc
        else:
            capex = dna = d_nwc = None
            d_rev = rev - prev_rev
            if d_rev < 0:
                flags.append(f"Year {i + 1}: revenue falls; no invested capital is assumed to be released")
            reinv = max(d_rev, 0.0) / inp.reinvestment.ratio
        fcff = nopat - reinv
        share = inp.stub if i == 0 else 1.0
        t = inp.stub + i
        df = 1 / (1 + inp.wacc) ** t
        memo = None
        if interest is not None or borrowing is not None:
            memo = fcff - (interest[i] if interest else 0) * (1 - taxes[i]) + (borrowing[i] if borrowing else 0)
        rows.append(Row(year=i + 1, revenue=rev, ebit=ebit, taxes=tax, nopat=nopat, capex=capex, dna=dna,
                        delta_nwc=d_nwc, net_reinvestment=reinv, fcff=fcff, fcff_counted=fcff * share,
                        discount_factor=df, pv=fcff * share * df, levered_fcf_memo=memo))
        prev_rev = rev

    t_rev = prev_rev * (1 + g)
    t_ebit = t_rev * inp.terminal_margin
    t_nopat = t_ebit - max(t_ebit, 0.0) * t_tax  # no tax refund on a terminal loss either
    rr = g / inp.terminal_roic
    t_fcff = t_nopat * (1 - rr)
    tv = t_fcff / (t_wacc - g)
    pv_tv = tv * rows[-1].discount_factor
    ev = sum(r.pv for r in rows) + pv_tv
    b = inp.bridge
    equity = ev + b.excess_cash + b.nonoperating_assets - b.debt - b.other_senior_claims
    tv_share = pv_tv / ev if ev > 0 else float("nan")

    if inp.risk_free is not None and g > inp.risk_free:
        flags.append(f"Terminal growth {g:.2%} exceeds the risk-free rate {inp.risk_free:.2%}: the company would outgrow "
                     "the economy forever")
    if inp.growth[-1] - g > 0.03:
        flags.append(f"Revenue growth drops from {inp.growth[-1]:.1%} in year {n} to {g:.1%} in perpetuity: consider "
                     "more explicit years so the business reaches maturity first")
    if ex:
        ebitda = [m + d for m, d in zip(margins, ex.dna_pct)]
        if ebitda[-1] - ebitda[0] > 0.03:
            flags.append(f"Implied EBITDA margin rises from {ebitda[0]:.1%} to {ebitda[-1]:.1%} because depreciation "
                         "grows while operating margin is held: is that expansion intended?")
        last_rr = rows[-1].net_reinvestment / rows[-1].nopat if rows[-1].nopat > 0 else None
        if last_rr is not None and abs(last_rr - rr) > 0.20:
            flags.append(f"Reinvestment rate jumps from {last_rr:.0%} in year {n} to {rr:.0%} in the terminal period")
    if g > 0.04:
        flags.append(f"Terminal growth {g:.1%} exceeds 4%, a conservative ceiling for long-run nominal growth: justify it")
    if abs(inp.terminal_margin - margins[-1]) > 0.05:
        flags.append(f"Terminal margin {inp.terminal_margin:.1%} jumps from year-{n} margin {margins[-1]:.1%}")
    if inp.terminal_roic > 0.30:
        flags.append(f"Terminal ROIC {inp.terminal_roic:.0%} assumes excess returns forever: justify the moat")
    if ev > 0 and tv_share > 0.75:
        flags.append(f"{tv_share:.0%} of operating EV is terminal value: the result mostly reflects terminal assumptions")
    return DCFResult(inputs=inp, rows=rows, terminal_nopat=t_nopat, reinvestment_rate=rr, terminal_fcff=t_fcff,
                     terminal_value=tv, pv_terminal=pv_tv, enterprise_value=ev, equity_value=equity,
                     value_per_share=equity / b.diluted_shares, terminal_share=tv_share,
                     implied_exit_ev_ebit=tv / t_ebit if t_ebit > 0 else None, flags=flags)
