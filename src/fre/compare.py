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
    ("capex_to_depreciation", "Capex / depreciation (definitions differ)", times),
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
                   + ("." if gp.value is not None else "; gross margin uses revenue minus cost of revenue as presented."))
    tags = []
    for r in [pilot, *peers]:
        f = r.reported.fact("dna", r.reported.labels[-1])
        loc = f.sources[0].locator if f.sources else "missing"
        tags.append(f"{r.ticker} uses {loc}" + (" (property and equipment only; excludes amortization)"
                                                 if loc.endswith(":Depreciation") else ""))
    out.append("Capex / depreciation is NOT like-for-like: " + "; ".join(tags) + ".")
    out.append("The comparability notes above are drafted from each 10-K; the team should review them before relying "
               "on the comparison.")
    return out


def table(pilot: Run, peers: list[Run]) -> str:
    runs = [pilot, *peers]
    head = "| Metric | " + " | ".join(f"{r.ticker} {r.reported.labels[-1]} (FYE {_fye(r)})" for r in runs) + " |"
    L = [head, "|---|" + "---:|" * len(runs)]
    for metric, name, fmt in COLUMNS:
        L.append(f"| {name} | " + " | ".join(fmt(r.reported.value(metric, r.reported.labels[-1])) for r in runs) + " |")
    return "\n".join(L)


HISTORY = [("revenue_growth", "Revenue growth", lambda v: pct(v, True)), ("operating_margin", "Operating margin", pct),
           ("fcf_margin", "FCF margin", pct), ("capex_intensity", "Capex / revenue", pct)]


def history(runs: list[Run]) -> str:
    """Every loaded year for each company, with its fiscal-year end, so trends compare like with like."""
    L = []
    for metric, name, fmt in HISTORY:
        L += [f"**{name}**", "", "| Company (currency) | " + " | ".join(f"Y-{i}" for i in range(4, -1, -1)) + " |",
              "|---|" + "---:|" * 5]
        for r in runs:
            ds = r.reported
            cells = [f"{fmt(ds.value(metric, lab))} ({ds.fact('revenue', lab).period_end:%b %Y})" for lab in ds.labels[-5:]]
            L.append(f"| {r.ticker} ({r.reported.company.currency}) | " + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L)


def comparability(runs: list[Run]) -> list[str]:
    from .pipeline import config

    c = config().get("comparability") or {}
    out = []
    for r in runs:
        entry = c.get(r.ticker)
        if not entry:
            out.append(f"- **{r.ticker}**: no comparability note yet (PRD A5 requires one).")
            continue
        quotes = " ".join(f"“{' '.join(q['quote'].split())}”" for q in entry["quotes"])
        out.append(f"- **{r.ticker}**: {' '.join(entry['note'].split())} Source (10-K, verified verbatim): {quotes}")
    return out


def markdown(pilot: Run, peers: list[Run], multiples: dict | None = None) -> str:
    if not peers:
        return ""
    runs = [pilot, *peers]
    L = ["Latest fiscal year of each company:", "", table(pilot, peers), "", "Five-year history (period end in brackets):", "",
         history(runs), "Comparability:", "", *comparability(runs), "", *[f"- {n}" for n in notes(pilot, peers)]]
    if multiples:
        L += ["", "Market multiples (relative valuation; every share class counted):", "",
              "| Company | Trailing window | Price date | Market cap | P/E | EV/EBIT | FCF yield |", "|---|---|---|---:|---:|---:|---:|"]
        for t, m in multiples.items():
            L.append(f"| {t} | {m.window} | {m.price_date} | {money(m.market_cap)} | {'—' if m.pe is None else f'{m.pe:.1f}x'} | "
                     f"{'—' if m.ev_ebit is None else f'{m.ev_ebit:.1f}x'} | {'—' if m.fcf_yield is None else f'{m.fcf_yield:.2%}'} |")
        L += [f"- {t}: {'; '.join(m.notes)}" for t, m in multiples.items() if m.notes]
    return "\n".join(L)
