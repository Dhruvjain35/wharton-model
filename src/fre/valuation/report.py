"""Valuation report: assumptions first, then what they imply, then what would change the answer."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from ..dossier import money, pct, per_share
from ..quarterly import ttm, ytd
from .run import ValuationRun

EVIDENCE_FLOWS = [("revenue", "Revenue"), ("operating_income", "Operating income"), ("net_income", "Net income"),
                  ("equity_securities_gain", "Gains on equity securities"), ("cfo", "Operating cash flow"),
                  ("capex", "Capex"), ("dna", "Depreciation"), ("sbc", "SBC"), ("buybacks", "Buybacks")]


def evidence(run: ValuationRun, cf: dict, fund) -> dict:
    """History + latest YTD + TTM, all computed from reconciled facts."""
    ds = fund.reported
    end = run.valuation_date
    start = date(end.year, 1, 1)
    prior = (date(end.year - 1, 1, 1), date(end.year - 1, end.month, end.day))
    fye = ds.company.fiscal_year_end
    rows = {}
    for m, name in EVIDENCE_FLOWS:
        cur, pri, t = ytd(cf, m, start, end), ytd(cf, m, *prior), ttm(cf, m, end, fye)
        rows[m] = {"name": name, "history": {lab: ds.value(m, lab) for lab in ds.labels},
                   "ytd": cur.value, "ytd_prior": pri.value, "ttm": t.value}
    rev = rows["revenue"]
    ratios = {
        "revenue_growth_ytd": (rev["ytd"] / rev["ytd_prior"] - 1) if rev["ytd"] and rev["ytd_prior"] else None,
        "operating_margin_ytd": rows["operating_income"]["ytd"] / rev["ytd"] if rev["ytd"] else None,
        "operating_margin_ttm": rows["operating_income"]["ttm"] / rev["ttm"] if rev["ttm"] else None,
        "capex_intensity_ytd": rows["capex"]["ytd"] / rev["ytd"] if rev["ytd"] else None,
        "capex_intensity_ttm": rows["capex"]["ttm"] / rev["ttm"] if rev["ttm"] else None,
        "dna_intensity_ytd": rows["dna"]["ytd"] / rev["ytd"] if rev["ytd"] else None,
        "equity_gains_share_of_net_income_ytd": rows["equity_securities_gain"]["ytd"] / rows["net_income"]["ytd"]
        if rows["net_income"]["ytd"] else None,
        "cash_fcf_ytd": (rows["cfo"]["ytd"] - rows["capex"]["ytd"]) if rows["cfo"]["ytd"] is not None and rows["capex"]["ytd"] is not None else None,
        "cash_fcf_ytd_prior": (rows["cfo"]["ytd_prior"] - rows["capex"]["ytd_prior"]) if rows["cfo"]["ytd_prior"] is not None and rows["capex"]["ytd_prior"] is not None else None,
    }
    return {"period_end": str(end), "labels": ds.labels, "rows": rows, "ratios": ratios}


def _assumption_table(cfg: dict) -> list[str]:
    L = ["| Assumption | Value | Range | Units | Status | Owner |", "|---|---|---|---|---|---|"]
    for name, a in cfg["assumptions"].items():
        units = a["units"].lower()
        one = (money if units.startswith("usd") else (lambda v: f"{v:.2f}") if "beta" in units
               else (lambda v: f"{v:.2%}"))
        fmt = (lambda v: ", ".join(f"{x:.1%}" for x in v)) if isinstance(a["value"], list) else one
        rng = (f"{fmt(a['low'])} … {fmt(a['high'])}")
        L.append(f"| {name} | {fmt(a['value'])} | {rng} | {a['units']} | {a['status']} | {a['owner']} |")
    return L


def markdown(run: ValuationRun, ev: dict) -> str:
    cfg, b = run.cfg, run.base
    px = {k: v[cfg["headline_class"]] for k, v in run.prices.items() if k != "risk_free"}
    rf = run.prices["risk_free"]
    w = run.wacc
    r = ev["ratios"]
    L = [
        f"# {run.ticker} valuation — FCFF DCF (PRD phase B)",
        "",
        "**Every judgment input below is PROPOSED and unapproved.** The output shows what those inputs imply; it is "
        "not a price target or a recommendation. The reverse DCF and grids show how much the answer moves.",
        "",
        f"Valuation date {run.valuation_date} (latest 10-Q balance sheet) · first forecast year counts "
        f"{run.stub:.1%} of its cash flow · prices dated separately below.",
        "",
        "## Evidence the assumptions lean on (computed from reconciled facts)",
        "",
        "| Metric | " + " | ".join(ev["labels"]) + f" | YTD prior | YTD {ev['period_end']} | TTM |",
        "|---|" + "---:|" * (len(ev["labels"]) + 3),
    ]
    for m, row in ev["rows"].items():
        L.append(f"| {row['name']} | " + " | ".join(money(row["history"][lab]) for lab in ev["labels"])
                 + f" | {money(row['ytd_prior'])} | {money(row['ytd'])} | {money(row['ttm'])} |")
    L += [
        "",
        f"- YTD revenue growth {pct(r['revenue_growth_ytd'], True)}; operating margin YTD {pct(r['operating_margin_ytd'])}, "
        f"TTM {pct(r['operating_margin_ttm'])}.",
        f"- Capex intensity YTD {pct(r['capex_intensity_ytd'])}, TTM {pct(r['capex_intensity_ttm'])}; depreciation "
        f"intensity YTD {pct(r['dna_intensity_ytd'])}.",
        f"- Cash FCF (CFO − capex) YTD {money(r['cash_fcf_ytd'])} vs {money(r['cash_fcf_ytd_prior'])} a year earlier.",
        f"- Gains on equity securities are {pct(r['equity_gains_share_of_net_income_ytd'])} of YTD net income.",
        "",
        "## Assumptions",
        "",
        *_assumption_table(cfg),
        "",
        "## Sourced inputs",
        "",
        f"- Risk-free: FRED {rf.series} {rf.value:.2%} on {rf.date} ({rf.source_url}, snapshot `{rf.snapshot_id}`)",
        *[f"- {k}: {v['figure']} — \"{' '.join(v['quote'].split())}\" (snapshot `{v['snapshot_id']}`)"
          for k, v in cfg["sourced"].items()],
        "",
        "## Discount rate",
        "",
        f"Cost of equity {w.cost_of_equity:.2%} = {w.inputs.risk_free:.2%} + {w.inputs.beta:.2f} × {w.inputs.equity_risk_premium:.2%}; "
        f"after-tax cost of debt {w.after_tax_cost_of_debt:.2%}; preferred {w.inputs.cost_of_preferred:.2%} "
        f"(dividend on liquidation preference / market price). Market weights at {run.valuation_date}: equity "
        f"{w.weights['equity']:.1%}, debt {w.weights['debt']:.1%}, preferred {w.weights['preferred']:.1%}. "
        f"**WACC {w.wacc:.2%}.**",
        "",
        "## Equity bridge (all at the valuation date)",
        "",
        "| Item | Amount | Source |",
        "|---|---:|---|",
        f"| Operating EV (base) | {money(b.enterprise_value)} | model |",
        f"| + Cash and marketable securities (less operating cash {money(cfg['assumptions']['operating_cash']['value'])}) | "
        f"{money(b.inputs.bridge.excess_cash)} | {run.bridge_items['cash'].source}; {run.bridge_items['st_investments'].source} |",
        f"| + Non-marketable securities (carrying value) | {money(b.inputs.bridge.nonoperating_assets)} | {run.bridge_items['other_lt_investments'].source} |",
        f"| − Debt incl. finance leases | {money(b.inputs.bridge.debt)} | notes, current portion, finance leases, commercial paper |",
        f"| − Mandatory convertible preferred (liquidation preference) | {money(b.inputs.bridge.other_senior_claims)} | 10-Q quotes |",
        f"| = Equity value | {money(b.equity_value)} | |",
        f"| ÷ Diluted shares | {b.inputs.bridge.diluted_shares / 1e6:,.0f}m | {run.shares['outstanding'].value / 1e6:,.0f}m outstanding + "
        f"{run.shares['unvested_rsus'].value / 1e6:,.0f}m unvested RSUs |",
        "",
        "SBC stays inside operating margin and is not added back; existing RSUs are counted as shares; no separate "
        "future-dilution charge (PRD B3). Operating leases stay operating (lease cost inside margin, liability not in debt).",
        "",
        "## Results",
        "",
        "| Scenario | Operating EV | Equity value | Per share | Terminal share of EV |",
        "|---|---:|---:|---:|---:|",
        *[f"| {n} | {money(s.enterprise_value)} | {money(s.equity_value)} | {per_share(s.value_per_share)} | {s.terminal_share:.0%} |"
          for n, s in run.scenarios.items()],
        "",
        "| Price | Date | Market cap (all classes) |",
        "|---|---|---:|",
        *[f"| {cfg['headline_class']} {per_share(q.close)} | {q.date} | {money(run.market_cap[k])} |" for k, q in px.items()],
        "",
        *[f"- **{n}**: {' '.join((cfg['scenarios'].get(n) or {}).get('rationale', 'proposed assumptions').split())}"
          for n in run.scenarios],
        "",
        "Flags: " + ("; ".join(sorted({f for s in run.scenarios.values() for f in s.flags})) or "none"),
        "",
        "## Reverse DCF — assumptions consistent with price under this model",
        "",
        "One unknown at a time; every other assumption held at its base value. Bracketed Brent root finding over "
        "the bounds shown. \"none\" means no value inside the bounds reproduces the price.",
        "",
        "| Price | Solve for | Result | Bounds | Monotonic |",
        "|---|---|---|---|---|",
    ]
    for label, d in run.reverse.items():
        for var, sr in d.items():
            res = ", ".join(f"{x:.2%}" for x in sr.roots) if sr.roots else "no solution in bounds"
            L.append(f"| {per_share(px[label].close)} ({px[label].date}) | {var} | {res} ({sr.status}) | "
                     f"{sr.lo:.1%} … {sr.hi:.1%} | {'yes' if sr.monotonic else 'NO'} |")
    be = run.breakevens["capex_multiplier_at_latest_price"]
    L += [
        "",
        f"Capex break-even at {per_share(px['latest'].close)}: "
        + (f"the capex path scaled by {be.roots[0]:.2f}x reproduces the price." if be.roots else
           f"no capex multiplier in [{be.lo:.1f}x, {be.hi:.1f}x] reproduces the price with growth and margins held fixed; "
           "the gap is about growth, margins or the discount rate, not capex alone."),
        "",
        "## Sensitivity",
        "",
    ]
    for key, g in run.grids.items():
        L += [f"**{g['y']} (rows) × {g['x']} (columns), value per share**", "",
              "| | " + " | ".join(f"{x:.1%}" for x in g["xs"]) + " |", "|---|" + "---:|" * len(g["xs"])]
        for y, row in zip(g["ys"], g["values"]):
            L.append(f"| {y:.1%} | " + " | ".join("n/a" if v is None else f"{v:,.0f}" for v in row) + " |")
        L.append("")
    L += [
        "Sensitivity ranges are not statistical confidence intervals, and no probabilities are attached to scenarios.",
        "",
        "Non-marketable securities carry the disputed mark-to-market gains (see the accounting ledger). Value per share "
        "with those holdings haircut: " + ", ".join(f"{x['haircut']:.0%} → {per_share(x['value_per_share'])}"
                                                    for x in run.nonoperating_sensitivity) + ".",
        "",
        "## Open inputs before this can be relied on",
        "",
        "- Equity risk premium and beta are placeholders without a source (TEAM INPUT REQUIRED).",
        "- Depreciation is a proposed % of revenue; a PP&E roll-forward tied to the capex path is the next model step.",
        "- Cost of debt uses the 2026 USD coupon, not a current market yield.",
        "- All forecast assumptions await a teammate's approval.",
        "",
    ]
    if run.problems:
        L += ["## Input problems", "", *[f"- {p}" for p in run.problems], ""]
    return "\n".join(L)


def payload(run: ValuationRun, ev: dict) -> dict:
    return {
        "ticker": run.ticker, "valuation_date": str(run.valuation_date), "stub": run.stub,
        "problems": run.problems, "config": run.cfg, "evidence": ev,
        "base_revenue": asdict(run.base_revenue), "operating_nwc": asdict(run.nwc),
        "bridge_items": {k: asdict(v) for k, v in run.bridge_items.items()},
        "shares": {k: asdict(v) for k, v in run.shares.items()},
        "prices": {k: ({s: asdict(q) for s, q in v.items()} if k != "risk_free" else asdict(v)) for k, v in run.prices.items()},
        "market_cap": run.market_cap, "wacc": run.wacc.to_dict(),
        "scenarios": {k: v.to_dict() for k, v in run.scenarios.items()},
        "reverse": {k: {var: sr.to_dict() for var, sr in d.items()} for k, d in run.reverse.items()},
        "breakevens": {k: v.to_dict() for k, v in run.breakevens.items()},
        "grids": run.grids, "nonoperating_sensitivity": run.nonoperating_sensitivity,
    }


def write(run: ValuationRun, ev: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "valuation.md").write_text(markdown(run, ev))
    (out_dir / "valuation.json").write_text(json.dumps(payload(run, ev), indent=2, sort_keys=True, default=str))
    return out_dir
