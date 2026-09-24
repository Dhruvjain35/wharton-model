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
    """History + latest YTD + TTM, read from the reconciled fundamentals run (never raw)."""
    ds, lat, lab = fund.reported, fund.latest, fund.latest_labels
    rows = {}
    for m, name in EVIDENCE_FLOWS:
        rows[m] = {"name": name, "history": {l: ds.value(m, l) for l in ds.labels},
                   "ytd": lat.value(m, lab["cur"]), "ytd_prior": lat.value(m, lab["prior"]),
                   "ttm": lat.value(m, lab["ttm"])}

    def div(a, b):
        return a / b if a is not None and b else None

    rev = rows["revenue"]
    ratios = {
        "revenue_growth_ytd": div(rev["ytd"], rev["ytd_prior"]) - 1 if div(rev["ytd"], rev["ytd_prior"]) is not None else None,
        "operating_margin_ytd": div(rows["operating_income"]["ytd"], rev["ytd"]),
        "operating_margin_ttm": div(rows["operating_income"]["ttm"], rev["ttm"]),
        "capex_intensity_ytd": div(rows["capex"]["ytd"], rev["ytd"]),
        "capex_intensity_ttm": div(rows["capex"]["ttm"], rev["ttm"]),
        "dna_intensity_ytd": div(rows["dna"]["ytd"], rev["ytd"]),
        "equity_gains_share_of_pretax_ytd": div(rows["equity_securities_gain"]["ytd"], lat.value("pretax_income", lab["cur"])),
        "cash_fcf_ytd": lat.value("fcf", lab["cur"]),
        "cash_fcf_ytd_prior": lat.value("fcf", lab["prior"]),
    }
    return {"period_end": lab["cur"][3:], "labels": ds.labels, "rows": rows, "ratios": ratios}


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


def _unverified_bridge(run: ValuationRun) -> list[str]:
    verified = ("matched", "matched-negated", "matched-in-notes")
    pairs = list(run.bridge_items.items()) + [("shares_outstanding", run.shares["outstanding"]),
                                              ("unvested_rsus", run.shares["unvested_rsus"])]
    bad, by_quote = [], []
    for key, v in pairs:
        if "[reconciliation:" not in v.source or any(f"[reconciliation: {o}]" in v.source for o in verified):
            continue
        (by_quote if key in run.confirmed else bad).append(key)
    L = []
    if by_quote:
        L.append(f"Confirmed by verified 10-Q quotes (not in a parsed table): {', '.join(by_quote)}.")
    L.append(f"**Not verified (check by hand):** {', '.join(bad)}." if bad
             else "Every balance-sheet input above is verified against the 10-Q (tables or quoted text).")
    return L + [""]


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
        f"- Pretax gains on equity securities are {pct(r['equity_gains_share_of_pretax_ytd'])} of YTD pretax income.",
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
        *_unverified_bridge(run),
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
        "Flags:",
        *[f"- **{n}**: {f}" for n, sc in run.scenarios.items() for f in sc.flags],
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
           f"no capex multiplier in [{be.lo:.1f}x, {be.hi:.1f}x] reproduces the price with growth and margins held fixed. "
           "Read this with the model's structure in mind: capex only enters the five explicit years, while terminal "
           "reinvestment is set by growth / ROIC, and the terminal value is most of EV."),
        "",
        "## Relative valuation cross-check (not averaged with the DCF)",
        "",
        "| Company | Window | Price date | Market cap (all classes) | P/E (mkt cap / trailing NI) | P/E (price / FY diluted EPS) | EV/EBIT | FCF yield |",
        "|---|---|---|---:|---:|---:|---:|---:|",
        *[f"| {t} | {m.window} | {m.price_date} | {money(m.market_cap)} | {'—' if m.pe is None else f'{m.pe:.1f}x'} | {'—' if m.pe_fy_eps is None else f'{m.pe_fy_eps:.1f}x ({m.fy_label})'} | "
          f"{'—' if m.ev_ebit is None else f'{m.ev_ebit:.1f}x'} | {'—' if m.fcf_yield is None else f'{m.fcf_yield:.2%}'} |"
          for t, m in run.multiples.items()],
        "",
        *[f"- {t}: " + "; ".join(m.notes) for t, m in run.multiples.items() if m.notes],
        f"- P/E uses all-class market cap / trailing net income; {run.ticker}'s trailing net income includes "
        f"{money(ev['rows']['equity_securities_gain']['ttm'])} of pretax gains on equity securities, so EV/EBIT is the cleaner comparison.",
        f"- Exit-multiple check: the base-case perpetuity terminal value equals "
        + (f"{b.implied_exit_ev_ebit:.1f}x" if b.implied_exit_ev_ebit else "n/a")
        + " year-N+1 EBIT. Compare with the trailing EV/EBIT multiples above: a perpetuity value far below what "
          "peers trade at today is one reason the model value sits below the price.",
        "",
        "## Preferred claim",
        "",
        *[f"- Deducted at {p['basis']} ({money(p['claim'])}): {per_share(p['value_per_share'])} per share"
          for p in run.preferred_sensitivity],
        "- The preferred converts into Class A/C shares by May 15, 2029 at a rate that depends on the share price; a "
        "conversion-value treatment would need the conversion-rate schedule from the filing.",
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
    import hashlib
    from datetime import datetime, timezone

    from ..engine import code_version

    body = _body(run, ev)
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    return {"run": {"kind": "valuation", "ticker": run.ticker,
                    "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "code_version": code_version(), "snapshots_read": run.snapshots_read},
            "outputs_digest": digest, **body}


def _body(run: ValuationRun, ev: dict) -> dict:
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
        "preferred_sensitivity": run.preferred_sensitivity,
        "multiples": {k: v.to_dict() for k, v in run.multiples.items()},
        "implied_exit_ev_ebit": {k: v.implied_exit_ev_ebit for k, v in run.scenarios.items()},
    }


def write(run: ValuationRun, ev: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "valuation.md").write_text(markdown(run, ev))
    (out_dir / "valuation.json").write_text(json.dumps(payload(run, ev), indent=2, sort_keys=True, default=str))
    return out_dir
