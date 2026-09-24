"""Run a reviewed valuation file (reviews/<TICKER>/valuation.yaml) end to end.

What is sourced, and from where:
  - base-year revenue, operating NWC lines        the base year's 10-K (reconciled facts / statement rows)
  - balance sheet at the valuation date           the latest 10-Q (facts, reconciled to its statement)
  - share count                                   the latest 10-Q (CommonStockSharesOutstanding) + unvested RSUs
  - risk-free rate                                FRED DGS10, snapshotted
  - prices                                        Nasdaq closes, snapshotted, with their own dates
  - cost of debt, preferred terms                 verbatim 10-Q quotes, verified against the snapshot
What is judgment (every item carries value, range, rationale, owner, date, status):
  - growth, margins, tax, capex, D&A, terminal economics, beta, ERP
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

import yaml

from .. import snapshot
from ..filing_text import plain_text
from ..pipeline import ROOT, lock
from ..quarterly import instant
from ..statements import primary_statements
from .dcf import Bridge, DCFInputs, DCFResult, Explicit, ValuationError, value
from .market import close_on_or_before, fred_on_or_before
from .reverse import SolveResult, grid2d, reverse, solve
from .wacc import Wacc, WaccInputs, compute

REQUIRED = ("value", "low", "high", "units", "rationale", "owner", "as_of", "status")
PER_YEAR = ("growth", "operating_margin", "capex_pct", "dna_pct")


class ConfigError(ValueError):
    pass


# ----------------------------------------------------------------------------- config checks


def validate(cfg: dict) -> list[str]:
    problems = []
    n = cfg["forecast_years"]
    for name, a in cfg["assumptions"].items():
        for k in REQUIRED:
            if k not in a or a[k] in (None, ""):
                problems.append(f"{name}: missing '{k}'")
        if any(k not in a for k in ("value", "low", "high")):
            continue
        v, lo, hi = a["value"], a["low"], a["high"]
        flat = [x for y in (v, lo, hi) for x in (y if isinstance(y, list) else [y])]
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in flat):
            problems.append(f"{name}: value/low/high must be numbers (YAML reads 1e9 as text; write 1.0e+9)")
            continue
        if name in PER_YEAR:
            if not all(isinstance(x, list) and len(x) == n for x in (v, lo, hi)):
                problems.append(f"{name}: needs {n} yearly values for value, low and high")
                continue
            if any(not (l <= x <= h) for x, l, h in zip(v, lo, hi)):
                problems.append(f"{name}: a value lies outside its own range")
        elif not (lo <= v <= hi):
            problems.append(f"{name}: value {v} outside its range [{lo}, {hi}]")
        if a.get("status") == "approved":
            from ..ledger import _is_ai
            r = a.get("reviewer")
            if not r or r == a.get("owner") or _is_ai(r):
                problems.append(f"{name}: approval needs a human reviewer other than the owner")
    for sname, sc in (cfg.get("scenarios") or {}).items():
        for k in ("rationale", "owner", "as_of", "status"):
            if not sc.get(k):
                problems.append(f"scenario {sname}: missing '{k}'")
        for k, v in sc.items():
            if k in SCENARIO_META:
                continue
            base = cfg["assumptions"].get(k)
            if base is None:
                problems.append(f"scenario {sname}: overrides unknown assumption '{k}'")
                continue
            vals, los, his = (v, base["low"], base["high"]) if isinstance(v, list) else ([v], [base["low"]], [base["high"]])
            if any(not (lo <= x <= hi) for x, lo, hi in zip(vals, los, his)):
                problems.append(f"scenario {sname}: {k} leaves the assumption's own range; widen the range with a reason")
    return problems


SCENARIO_META = ("rationale", "owner", "as_of", "status", "reviewer")


def verify_quotes(cfg: dict) -> list[str]:
    """Each sourced input quotes its filing; the quote must be verbatim and contain the stated figure."""
    problems = []
    for name, s in (cfg.get("sourced") or {}).items():
        text = " ".join(plain_text(snapshot.load_bytes(s["snapshot_id"])).split())
        quote = " ".join(s["quote"].split())
        if quote not in text:
            problems.append(f"{name}: quote not found verbatim in snapshot {s['snapshot_id']}")
        elif s["figure"] not in quote:
            problems.append(f"{name}: figure '{s['figure']}' is not in its quote")
    return problems


def figure_value(figure: str) -> float:
    """The number a quoted figure states: '4.80 %' -> 0.048, '385 million' -> 385e6, '$ 50 ...' -> 50."""
    import re

    m = re.search(r"(-?\d[\d,]*(?:\.\d+)?)\s*(%|percent|billion|million|thousand)?", figure)
    if not m:
        raise ConfigError(f"no number in figure {figure!r}")
    v = float(m.group(1).replace(",", ""))
    scale = {"%": 0.01, "percent": 0.01, "billion": 1e9, "million": 1e6, "thousand": 1e3}.get(m.group(2) or "", 1.0)
    return v * scale


def check_sourced_values(cfg: dict) -> list[str]:
    """The number the model uses must be the number printed in its quote."""
    import re

    problems = []
    for name, s in (cfg.get("sourced") or {}).items():
        try:
            stated = figure_value(s["figure"])
        except ConfigError as e:
            problems.append(f"{name}: {e}")
            continue
        if abs(float(s["value"]) - stated) > 1e-9 * max(1.0, abs(stated)):
            problems.append(f"{name}: value {s['value']} does not equal its quoted figure {s['figure']!r} ({stated:g})")
    split = (cfg.get("sourced") or {}).get("class_split")
    classes = cfg.get("class_shares") or {}
    if classes:
        quote = " ".join(split["quote"].split()) if split else ""
        total = 0.0
        for cname, c in classes.items():
            letter = cname.split("_")[-1].upper()
            m = re.search(rf"Class {letter} ([\d,]+)", quote)
            shares = float(c["shares"])
            total += shares
            if not m or abs(float(m.group(1).replace(",", "")) * 1e6 - shares) > 0.5e6:
                problems.append(f"{cname}: {shares:g} shares not stated as Class {letter} in the class_split quote")
        if split and abs(total - float(split["value"]) * 1e6) > 1.5e6:
            problems.append(f"class shares sum to {total:g}, but the quote states {split['value']} million")
    return problems


def _a(cfg: dict, name: str, which: str = "value"):
    return cfg["assumptions"][name][which]


# ----------------------------------------------------------------------------- sourced inputs


@dataclass
class Sourced:
    label: str
    value: float
    source: str


def operating_nwc(cfg: dict, cik: int, accession: str, on: date, extra: dict[str, float]) -> Sourced:
    spec = cfg["operating_nwc"]
    sheet = next(st for st in primary_statements(cik, accession) if st.column_index(None, on) is not None
                 and "BALANCE" in st.title.upper())
    col = sheet.column_index(None, on)
    total, parts = 0.0, []
    for sign, tags in ((1, spec["add"]), (-1, spec["subtract"])):
        for tag in tags:
            rows = sheet.rows_for(tag)
            if not rows:
                raise ConfigError(f"operating NWC line {tag} not on the {on} balance sheet")
            v = sheet.scaled(rows[0], col, "USD")
            total += sign * v
            parts.append(f"{'+' if sign > 0 else '-'} {rows[0].label} {v / 1e6:,.0f}m")
    for name in spec.get("add_back_financing", []):
        total += extra[name]
        parts.append(f"+ {name} {extra[name] / 1e6:,.0f}m (financing item inside a subtracted line)")
    return Sourced("operating NWC", total, f"{sheet.url}: " + " ".join(parts))


@dataclass
class ValuationRun:
    ticker: str
    cfg: dict
    problems: list[str]
    valuation_date: date
    stub: float
    base_revenue: Sourced
    nwc: Sourced
    bridge_items: dict[str, Sourced]
    shares: dict[str, Sourced]
    prices: dict[str, dict]
    market_cap: dict[str, float]
    wacc: Wacc
    base: DCFResult
    scenarios: dict[str, DCFResult]
    reverse: dict[str, dict[str, SolveResult]]
    grids: dict[str, dict]
    nonoperating_sensitivity: list[dict]
    breakevens: dict[str, SolveResult] = field(default_factory=dict)
    preferred_sensitivity: list[dict] = field(default_factory=list)
    multiples: dict = field(default_factory=dict)  # ticker -> Multiples at the latest price date
    snapshots_read: list[str] = field(default_factory=list)
    fundamentals: object = None  # engine.Run for the same ticker
    companyfacts: dict = field(default_factory=dict, repr=False)


def _load(ticker: str) -> dict:
    return yaml.safe_load((ROOT / "reviews" / ticker / "valuation.yaml").read_text())


def build_inputs(cfg: dict, base_revenue: float, nwc: float, bridge: Bridge, wacc: float, stub: float,
                 overrides: dict | None = None, risk_free: float | None = None) -> DCFInputs:
    a = {k: v["value"] for k, v in cfg["assumptions"].items()} | (overrides or {})
    return DCFInputs(
        base_revenue=base_revenue, growth=a["growth"], operating_margin=a["operating_margin"], tax_rate=a["tax_rate"],
        reinvestment=Explicit(capex_pct=a["capex_pct"], dna_pct=a["dna_pct"], nwc_pct=nwc / base_revenue, base_nwc=nwc),
        wacc=wacc, terminal_growth=a["terminal_growth"], terminal_margin=a["terminal_margin"],
        terminal_roic=a["terminal_roic"], bridge=bridge, stub=stub, risk_free=risk_free)


def run(ticker: str) -> ValuationRun:
    cfg = _load(ticker)
    problems = validate(cfg) + verify_quotes(cfg) + check_sourced_values(cfg)
    ids = lock()[ticker]
    cf = snapshot.load(ids["companyfacts"])
    cik = int(cf["cik"])
    vdate = date.fromisoformat(str(cfg["valuation_date"]))
    by = cfg["base_year"]

    from ..engine import build as build_fundamentals  # annual facts, reconciled
    fund = build_fundamentals(ticker, check_notes=False)
    ds = fund.reported
    rev = ds.fact("revenue", by)
    base_revenue = Sourced("base revenue", rev.value, f"{rev.sources[0].url} ({rev.sources[0].locator})")
    fy_end = rev.period_end
    stub = (date(fy_end.year + 1, fy_end.month, fy_end.day) - vdate).days / 365.0
    if not 0 < stub <= 1:
        raise ConfigError(f"valuation date {vdate} must fall inside the first forecast year")

    fin_extra = {}
    for m in cfg["operating_nwc"].get("add_back_financing", []):
        if ds.value(m, by) is None:  # missing is not zero
            raise ConfigError(f"operating NWC add-back {m}@{by} is missing; attest it or remove it from the list")
        fin_extra[m] = ds.value(m, by)
    nwc = operating_nwc(cfg, cik, ds.annual_filings[by], fy_end, fin_extra)

    latest = fund.latest
    if latest is None or fund.latest_labels.get("bs") != f"AT{vdate}":
        raise ConfigError(f"valuation date {vdate} must be the latest 10-Q balance sheet date "
                          f"({fund.latest_labels.get('bs', 'none')})")
    recon = {r.fact: r.outcome for r in fund.latest_reconciliation}

    def bal(metric: str) -> Sourced:
        key = f"{metric}@AT{vdate}"
        f = latest.facts.get(key)
        if f is None or f.value is None:
            raise ConfigError(f"{metric} at {vdate} is missing or withheld by reconciliation")
        return Sourced(metric, f.value, f"{f.sources[0].accession} {f.sources[0].locator} at {vdate} "
                                        f"[reconciliation: {recon.get(key, 'n/a')}]")

    items = {m: bal(m) for m in ("cash", "st_investments", "other_lt_investments", "debt_lt_noncurrent",
                                 "debt_lt_current", "finance_lease_liability", "commercial_paper")}
    liq = cfg["sourced"]["preferred_liquidation_per_depositary_share"]
    n_dep = cfg["sourced"]["preferred_depositary_shares"]
    items["preferred_claim"] = Sourced("mandatory convertible preferred at liquidation preference",
                                       float(liq["value"]) * float(n_dep["value"]),
                                       f"{n_dep['quote']} / {liq['quote']}")
    operating_cash = float(_a(cfg, "operating_cash"))
    excess_cash = items["cash"].value + items["st_investments"].value - operating_cash
    debt = sum(items[k].value for k in ("debt_lt_noncurrent", "debt_lt_current", "finance_lease_liability",
                                        "commercial_paper"))
    shares = {"outstanding": bal("shares_outstanding"), "unvested_rsus": bal("unvested_rsus")}
    diluted = shares["outstanding"].value + shares["unvested_rsus"].value
    bridge = Bridge(excess_cash=excess_cash, nonoperating_assets=items["other_lt_investments"].value,
                    debt=debt, other_senior_claims=items["preferred_claim"].value, diluted_shares=diluted)

    # market data: prices at the valuation date and today, each with its own date
    prices = {}
    for label, on in (("valuation_date", vdate), ("latest", date.fromisoformat(str(cfg["price_date"])))):
        prices[label] = {sym: close_on_or_before(sym, on) for sym in cfg["listed_classes"]}
    classes = cfg["class_shares"]  # class -> shares at the valuation date, from the 10-Q (quoted)
    mcap = {}
    for label, q in prices.items():
        mcap[label] = sum(float(c["shares"]) * q[c["priced_as"]].close for c in classes.values())

    rf = fred_on_or_before("DGS10", vdate)
    pref_market = sum(float(n_dep["value"]) / 2 * prices["valuation_date"][s].close for s in cfg["preferred_listings"])
    w = compute(WaccInputs(
        risk_free=rf.value, equity_risk_premium=_a(cfg, "equity_risk_premium"), beta=_a(cfg, "beta"),
        pretax_cost_of_debt=float(cfg["sourced"]["pretax_cost_of_debt"]["value"]), tax_rate=_a(cfg, "tax_rate"),
        equity_value=mcap["valuation_date"], debt_value=debt, preferred_value=pref_market,
        cost_of_preferred=float(cfg["sourced"]["preferred_dividend_rate"]["value"]) * float(liq["value"])
        / (pref_market / float(n_dep["value"]))))
    prices["risk_free"] = rf

    base_in = build_inputs(cfg, base_revenue.value, nwc.value, bridge, w.wacc, stub, risk_free=rf.value)
    base = value(base_in)
    scenarios = {"base": base}
    for name, sc in (cfg.get("scenarios") or {}).items():
        over = {k: v for k, v in sc.items() if k != "rationale"}
        over = {k: v for k, v in over.items() if k not in SCENARIO_META}
        scenarios[name] = value(build_inputs(cfg, base_revenue.value, nwc.value, bridge, w.wacc, stub, over, rf.value))

    # reverse DCF at each price: one unknown at a time, everything else held fixed
    rev_out = {}
    per_share_price = {label: q[cfg["headline_class"]].close for label, q in prices.items() if label != "risk_free"}
    for label, px in per_share_price.items():
        rev_out[label] = {var: reverse(base_in, var, px, *cfg["reverse_bounds"][var])
                          for var in ("growth", "margin", "wacc", "terminal_growth")}

    growths = [x / 100 for x in range(4, 27, 2)]
    margins = [x / 100 for x in range(24, 43, 2)]
    waccs = [x / 1000 for x in range(75, 121, 5)]
    tgs = [x / 1000 for x in range(15, 41, 5)]
    grids = {
        "growth_x_margin": {"x": "growth (all forecast years)", "y": "operating margin (forecast and terminal)",
                            "xs": growths, "ys": margins, "values": grid2d(base_in, "growth", growths, "margin", margins)},
        "wacc_x_terminal_growth": {"x": "WACC", "y": "terminal growth", "xs": waccs, "ys": tgs,
                                   "values": grid2d(base_in, "wacc", waccs, "terminal_growth", tgs)},
    }

    # nonoperating assets carry the disputed mark-to-market gains: value with them haircut
    nonop = []
    for cut in (0.0, 0.25, 0.5, 1.0):
        b2 = replace(bridge, nonoperating_assets=bridge.nonoperating_assets * (1 - cut))
        nonop.append({"haircut": cut, "value_per_share": value(replace(base_in, bridge=b2)).value_per_share})

    # break-even: the capex path multiplier at which value equals the latest price
    px = per_share_price["latest"]
    def capex_scale(k):
        ex = base_in.reinvestment
        return value(replace(base_in, reinvestment=replace(ex, capex_pct=[c * k for c in ex.capex_pct]))).value_per_share - px
    breakevens = {"capex_multiplier_at_latest_price": solve(capex_scale, 0.2, 3.0)}

    # the preferred claim: liquidation preference (base) vs market value of the depositary shares
    pref_sens = [{"basis": "liquidation preference", "claim": bridge.other_senior_claims,
                  "value_per_share": base.value_per_share},
                 {"basis": f"market value at {vdate}", "claim": pref_market,
                  "value_per_share": value(replace(base_in, bridge=replace(bridge, other_senior_claims=pref_market))).value_per_share}]

    # relative valuation cross-check (clearly labelled; never averaged with the DCF)
    from ..engine import build as build_run
    from ..pipeline import companies as company_cfg
    from .multiples import for_run
    latest_px = date.fromisoformat(str(cfg["price_date"]))
    mults = {}
    for t, c in company_cfg().items():
        r = fund if t == ticker else build_run(t)
        mults[t] = for_run(t, r, latest_px, c["price_symbols"])

    read = set(ids.values()) | {s["snapshot_id"] for s in cfg["sourced"].values()} | {rf.snapshot_id}
    read |= {q.snapshot_id for k, v in prices.items() if k != "risk_free" for q in v.values()}

    return ValuationRun(ticker=ticker, cfg=cfg, problems=problems, valuation_date=vdate, stub=stub,
                        base_revenue=base_revenue, nwc=nwc, bridge_items=items, shares=shares, prices=prices,
                        market_cap=mcap, wacc=w, base=base, scenarios=scenarios, reverse=rev_out, grids=grids,
                        nonoperating_sensitivity=nonop, breakevens=breakevens, fundamentals=fund, companyfacts=cf,
                        preferred_sensitivity=pref_sens, multiples=mults, snapshots_read=sorted(read))
