"""Deterministic derived metrics and ratios (PRD A2).

Every output is a Fact with status DERIVED, its formula, and the keys of the facts it
used, so any ratio can be traced back to filing lines. When an input is missing, or
a denominator makes the ratio meaningless, the output is MISSING with the reason.
"""

from __future__ import annotations

from typing import Callable

from .models import Fact, FactStatus, ReviewItem
from .normalize import Dataset

GROSS_PROFIT_TOLERANCE = 0.5e6


def _put(ds: Dataset, metric: str, label: str, unit: str, value: float | None, formula: str,
         inputs: list[str], notes: list[str] | None = None) -> None:
    anchor = next((ds.facts[k] for k in inputs if k in ds.facts), None)
    ds.add(Fact(company=ds.company.cik, metric=metric, value=value, unit=unit,
                period_start=anchor.period_start if anchor else None,
                period_end=anchor.period_end if anchor else ds.facts[next(iter(ds.facts))].period_end,
                fiscal_label=label, status=FactStatus.DERIVED if value is not None else FactStatus.MISSING,
                formula=formula, inputs=inputs, notes=notes or []))


def _derive(ds: Dataset, metric: str, label: str, unit: str, formula: str, names: list[str],
            fn: Callable[..., float | None | tuple[float | None, str]], input_labels: list[str] | None = None) -> None:
    """Evaluate fn over the named facts; fn may return (None, reason) to suppress."""
    labels = input_labels or [label] * len(names)
    keys = [f"{n}@{lab}" for n, lab in zip(names, labels)]
    missing = [k for k in keys if ds.facts.get(k) is None or ds.facts[k].value is None]
    if missing:
        _put(ds, metric, label, unit, None, formula, keys, [f"Blocked: input {k} is missing or unresolved" for k in missing])
        return
    out = fn(*[ds.facts[k].value for k in keys])
    if isinstance(out, tuple):
        value, reason = out
        _put(ds, metric, label, unit, value, formula, keys, [reason] if reason else [])
    else:
        _put(ds, metric, label, unit, out, formula, keys)


def _ratio_positive_denominator(what: str):
    def fn(num, den):
        if den <= 0:
            return None, f"Suppressed: {what} is not positive ({den:,.0f})"
        return num / den
    return fn


def _prior(ds: Dataset, label: str) -> str | None:
    year = int(label[2:])
    return f"FY{year - 1}" if year - 1 in ds.fiscal_years else None


def _has(ds: Dataset, metric: str, label: str) -> bool:
    f = ds.facts.get(f"{metric}@{label}")
    return f is not None and f.value is not None


def _total_debt(ds: Dataset, label: str) -> None:
    """One lease policy for every year: all notes + all finance leases + commercial paper."""
    if _has(ds, "debt_lt_noncurrent", label):
        names = ["debt_lt_noncurrent", "debt_lt_current", "finance_lease_liability", "commercial_paper"]
    elif _has(ds, "debt_and_finance_lease_noncurrent", label):
        # older presentation: the noncurrent line already includes noncurrent finance leases
        names = ["debt_and_finance_lease_noncurrent", "debt_lt_current", "finance_lease_liability_current",
                 "commercial_paper"]
    else:
        names = ["debt_lt_noncurrent", "debt_lt_current", "finance_lease_liability", "commercial_paper"]
    _derive(ds, "total_debt", label, "USD", " + ".join(names), names, lambda *v: sum(v))
    f = ds.facts[f"total_debt@{label}"]
    if f.value is not None:
        ds.add(f.model_copy(update={"notes": f.notes + [
            "Policy: notes (carrying value) + finance leases + commercial paper; operating leases excluded and shown separately"]}))


def compute(ds: Dataset) -> Dataset:
    for label in ds.labels:
        # ---- derived amounts
        _derive(ds, "gross_profit_calc", label, "USD", "revenue - cost_of_revenue",
                ["revenue", "cost_of_revenue"], lambda r, c: r - c)
        _derive(ds, "fcf", label, "USD", "cfo - capex (cash FCF; not unlevered FCFF)", ["cfo", "capex"], lambda a, b: a - b)
        _derive(ds, "fcf_after_sbc", label, "USD", "cfo - capex - sbc", ["cfo", "capex", "sbc"], lambda a, b, c: a - b - c)
        _derive(ds, "liquid_investments", label, "USD", "cash + st_investments", ["cash", "st_investments"], lambda a, b: a + b)
        _total_debt(ds, label)
        _derive(ds, "net_debt", label, "USD", "total_debt - liquid_investments",
                ["total_debt", "liquid_investments"], lambda d, c: d - c)
        _derive(ds, "shareholder_payout", label, "USD", "buybacks + dividends", ["buybacks", "dividends"], lambda a, b: a + b)

        # ---- margins and intensities
        if _has(ds, "gross_profit", label):
            gp_name, gp_note = "gross_profit", []
            if _has(ds, "cost_of_revenue", label):
                calc = ds.value("revenue", label) - ds.value("cost_of_revenue", label)
                if abs(calc - ds.value("gross_profit", label)) > GROSS_PROFIT_TOLERANCE:
                    ds.review.append(ReviewItem(severity="warn", metric="gross_profit", fiscal_label=label,
                                                kind="gross-profit-check",
                                                message=f"Reported gross profit differs from revenue - cost of revenue by "
                                                        f"{ds.value('gross_profit', label) - calc:,.0f}"))
        else:
            gp_name = "gross_profit_calc"
            gp_note = ["Company does not report gross profit; uses revenue - cost of revenue as presented"]
        _derive(ds, "gross_margin", label, "pure", f"{gp_name} / revenue", [gp_name, "revenue"],
                _ratio_positive_denominator("revenue"))
        if gp_note and ds.facts[f"gross_margin@{label}"].value is not None:
            f = ds.facts[f"gross_margin@{label}"]
            ds.add(f.model_copy(update={"notes": f.notes + gp_note}))

        for metric, num, what in [
            ("operating_margin", "operating_income", "operating income"),
            ("net_margin", "net_income", "net income"),
            ("fcf_margin", "fcf", "cash FCF"),
            ("capex_intensity", "capex", "capex"),
            ("sbc_intensity", "sbc", "SBC"),
            ("rnd_intensity", "rnd", "R&D"),
        ]:
            _derive(ds, metric, label, "pure", f"{num} / revenue", [num, "revenue"], _ratio_positive_denominator("revenue"))

        _derive(ds, "cash_conversion", label, "pure", "cfo / net_income", ["cfo", "net_income"],
                _ratio_positive_denominator("net income"))
        _derive(ds, "effective_tax_rate", label, "pure", "income_tax / pretax_income", ["income_tax", "pretax_income"],
                _ratio_positive_denominator("pretax income"))
        _derive(ds, "capex_to_depreciation", label, "pure", "capex / dna", ["capex", "dna"],
                _ratio_positive_denominator("depreciation"))
        _derive(ds, "payout_to_fcf", label, "pure", "shareholder_payout / fcf", ["shareholder_payout", "fcf"],
                _ratio_positive_denominator("cash FCF"))
        _derive(ds, "nonoperating_share_of_pretax", label, "pure", "nonoperating_income / pretax_income",
                ["nonoperating_income", "pretax_income"], _ratio_positive_denominator("pretax income"))

        # ---- growth against the prior fiscal year in the dataset
        prior = _prior(ds, label)
        for metric, base in [("revenue_growth", "revenue"), ("operating_income_growth", "operating_income"),
                             ("net_income_growth", "net_income"), ("fcf_growth", "fcf"),
                             ("diluted_share_change", "shares_diluted")]:
            if prior is None:
                _put(ds, metric, label, "pure", None, f"{base} / prior {base} - 1", [],
                     [f"Suppressed: FY{int(label[2:]) - 1} is not in the loaded window"])
                continue
            _derive(ds, metric, label, "pure", f"{base} / prior {base} - 1", [base, base],
                    lambda cur, prev, what=base: (None, f"Suppressed: prior {what} is not positive")
                    if prev <= 0 else cur / prev - 1, input_labels=[label, prior])
        if prior is None:
            _put(ds, "eps_growth", label, "pure", None, "eps_diluted / prior eps_diluted - 1", [],
                 [f"Suppressed: FY{int(label[2:]) - 1} is not in the loaded window"])
        else:
            _derive(ds, "eps_growth", label, "pure", "eps_diluted / prior eps_diluted - 1", ["eps_diluted", "eps_diluted"],
                    _eps_growth, input_labels=[label, prior])

    # ---- ROIC (PRD A2: optional until the capital and tax definitions are reviewed)
    for label in ds.labels:
        _derive(ds, "nopat", label, "USD", "operating_income * (1 - effective_tax_rate)",
                ["operating_income", "effective_tax_rate"], lambda e, t: e * (1 - t))
        _derive(ds, "invested_capital", label, "USD",
                "equity + total_debt - cash - st_investments - other_lt_investments",
                ["equity", "total_debt", "cash", "st_investments", "other_lt_investments"],
                lambda e, d, c, s, o: e + d - c - s - o)
    for label in ds.labels:
        prior = _prior(ds, label)
        if prior is None:
            _put(ds, "roic", label, "pure", None, "nopat / average invested_capital", [],
                 [f"Suppressed: FY{int(label[2:]) - 1} balance sheet is not in the loaded window"])
            continue
        _derive(ds, "roic", label, "pure", "nopat / ((invested_capital + prior invested_capital) / 2)",
                ["nopat", "invested_capital", "invested_capital"],
                lambda n, a, b: (None, "Suppressed: average invested capital is not positive") if a + b <= 0 else n / ((a + b) / 2),
                input_labels=[label, label, prior])
        f = ds.facts[f"roic@{label}"]
        ds.add(f.model_copy(update={"notes": f.notes + [
            "Proposed definition (PRD A2 optional): operating leases excluded from capital, non-marketable "
            "securities treated as non-operating; review before relying on it"]}))

    # ---- window statistics, stored on the final year
    first, last = ds.labels[0], ds.labels[-1]
    years = len(ds.labels) - 1
    if years >= 1:
        _derive(ds, "revenue_cagr", last, "pure", f"(revenue {last} / revenue {first})^(1/{years}) - 1",
                ["revenue", "revenue"],
                lambda end, start: (None, "Undefined: nonpositive endpoint") if start <= 0 or end <= 0
                else (end / start) ** (1 / years) - 1, input_labels=[last, first])
    return ds


def _eps_growth(cur: float, prev: float):
    if prev > 0 and cur > 0:
        return cur / prev - 1
    change = cur - prev
    kind = {(True, False): "profit-to-loss", (False, True): "loss-to-profit"}.get((prev > 0, cur > 0), "loss-to-loss")
    return None, f"Suppressed ratio: {kind}; absolute change {change:+.2f} per share"
