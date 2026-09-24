"""Peer comparison (PRD A5): a table that exposes tradeoffs. No composite score."""

from __future__ import annotations

from .dossier import money, pct, times
from .engine import Run

COLUMNS = [
    ("revenue", "Revenue", money),
    ("revenue_cagr", "Revenue CAGR (window)", pct),
    ("operating_margin", "Operating margin", pct),
    ("net_margin", "Net margin", pct),
    ("fcf_margin", "FCF margin", pct),
    ("capex_intensity", "Capex / revenue", pct),
    ("capex_to_depreciation", "Capex / depreciation", times),
    ("sbc_intensity", "SBC / revenue", pct),
    ("cash_conversion", "CFO / net income", times),
    ("diluted_share_change", "Diluted share change", lambda v: pct(v, True)),
    ("nonoperating_share_of_pretax", "Non-operating / pretax", pct),
    ("net_debt", "Net debt", money),
]


def _fye(run: Run) -> str:
    f = run.reported.company.fiscal_year_end
    return f"{f[:2]}-{f[2:]}"


def notes(pilot: Run, peers: list[Run]) -> list[str]:
    """Comparability facts the data itself establishes."""
    out = []
    for p in peers:
        if p.reported.company.fiscal_year_end != pilot.reported.company.fiscal_year_end:
            last = p.reported.labels[-1]
            end = p.reported.fact("revenue", last).period_end
            out.append(f"{p.ticker}'s fiscal year ends {_fye(p)}: its {last} ended {end}, not on "
                       f"{pilot.ticker}'s {_fye(pilot)} calendar. Latest-year columns are not the same twelve months.")
    for r in [pilot, *peers]:
        last = r.reported.labels[-1]
        gp = r.reported.fact("gross_profit", last)
        out.append(f"{r.ticker} {'reports' if gp.value is not None else 'does not report'} gross profit"
                   + ("" if gp.value is not None else "; gross margin uses revenue minus cost of revenue as presented."))
    out.append("Business-mix comparability (segments, customers, capital intensity drivers) is a team judgment: "
               "write it from Item 1 of each 10-K before relying on this table.")
    return out


def table(pilot: Run, peers: list[Run]) -> str:
    runs = [pilot, *peers]
    head = "| Metric | " + " | ".join(f"{r.ticker} {r.reported.labels[-1]} (FYE {_fye(r)})" for r in runs) + " |"
    L = [head, "|---|" + "---:|" * len(runs)]
    for metric, name, fmt in COLUMNS:
        L.append(f"| {name} | " + " | ".join(fmt(r.reported.value(metric, r.reported.labels[-1])) for r in runs) + " |")
    return "\n".join(L)


def markdown(pilot: Run, peers: list[Run]) -> str:
    if not peers:
        return ""
    return "\n".join([table(pilot, peers), "", *[f"- {n}" for n in notes(pilot, peers)]])
