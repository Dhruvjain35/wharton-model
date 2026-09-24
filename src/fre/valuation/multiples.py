"""Market multiples (PRD A2 P/E and FCF yield; relative-valuation cross-check in section 5).

Every multiple states its formula, price date, share basis and trailing window.
Market capitalization always counts every share class (PRD B3): each class from the
latest filing's cover page, priced at its own listed symbol; an unlisted class that
converts 1:1 is priced at the class it converts into, and that is recorded.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

from ..statements import ARCHIVES, parse_r_page
from .. import snapshot


@dataclass
class ClassShares:
    section: str
    shares: float
    symbol: str
    price: float
    price_date: date


@dataclass
class Multiples:
    ticker: str
    price_date: date
    window: str  # e.g. "TTM to 2026-06-30" or "FY2026"
    balance_date: str
    classes: list[ClassShares]
    market_cap: float
    enterprise_value: float | None
    net_income: float | None
    ebit: float | None
    fcf: float | None
    pe: float | None
    ev_ebit: float | None
    fcf_yield: float | None
    ev_components: dict = field(default_factory=dict)
    pe_fy_eps: float | None = None  # headline class price / last fiscal-year diluted EPS (PRD A2 definition)
    fy_label: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def compute(ticker: str, price_date: date, classes: list[ClassShares], window: str, balance_date: str,
            net_income: float | None, ebit: float | None, fcf: float | None, debt: float | None,
            preferred: float | None, cash: float | None, marketable: float | None) -> Multiples:
    mcap = sum(c.shares * c.price for c in classes)
    notes = []
    comps = {"market_cap": mcap, "debt": debt, "preferred": preferred, "cash": cash, "marketable": marketable}
    ev = None
    missing = [k for k, v in comps.items() if v is None]
    notes.append("EV = market cap + debt incl. finance leases + preferred at carrying value - cash - marketable securities")
    if missing:  # missing is not zero; a component a company lacks must be attested
        notes.append(f"EV not computed: {', '.join(missing)} not reported at the balance-sheet date")
    else:
        ev = mcap + debt + preferred - cash - marketable

    def ratio(a, b, what):
        if a is None or b is None:
            notes.append(f"{what}: input missing")
            return None
        if b <= 0:
            notes.append(f"{what}: undefined for a nonpositive denominator")
            return None
        return a / b

    return Multiples(ticker=ticker, price_date=price_date, window=window, balance_date=balance_date, classes=classes,
                     market_cap=mcap, enterprise_value=ev, net_income=net_income, ebit=ebit, fcf=fcf,
                     pe=ratio(mcap, net_income, "P/E"), ev_ebit=ratio(ev, ebit, "EV/EBIT"),
                     fcf_yield=None if fcf is None or mcap <= 0 else fcf / mcap, ev_components=comps, notes=notes)


def cover_classes(cik: int, accession: str) -> list[tuple[str, float, str | None]]:
    """(class heading, shares, trading symbol printed for that class or None) from the cover page (R1)."""
    url = f"{ARCHIVES}/{cik}/{accession.replace('-', '')}/R1.htm"
    st = parse_r_page(snapshot.load_bytes(snapshot.fetch(url)))
    symbols = {r.section: next((t for t in r.text if t), None) for r in st.rows if r.tag == "dei:TradingSymbol"}
    titles = {r.section: next((t for t in r.text if t), None) for r in st.rows if r.tag == "dei:Security12bTitle"}
    out = []
    for r in st.rows_for("dei:EntityCommonStockSharesOutstanding"):
        vals = [st.scaled(r, i, "shares") for i in range(len(st.columns))]
        v = next((x for x in reversed(vals) if x is not None), None)
        if v is not None:
            name = (titles.get(r.section) or r.section or "Common stock").split(",")[0]  # the security title, not the member label
            out.append((name, v, symbols.get(r.section)))
    return out


def symbol_for(section: str, mapping: list[list[str]]) -> tuple[str, str]:
    """First mapping entry whose text appears in the class heading; ('', symbol) is the default."""
    for needle, sym in mapping:
        if needle and needle.lower() in section.lower():
            return sym, f"'{section}' priced at {sym}"
    default = next(sym for needle, sym in mapping if not needle)
    return default, f"'{section}' priced at {default}"


def for_run(ticker: str, run, price_date: date, symbol_map: list[list[str]]) -> Multiples:
    """Multiples for a fundamentals run: trailing window = TTM if a 10-Q followed the 10-K, else the last fiscal year."""
    from .market import close_on_or_before

    ds = run.reported
    last = ds.labels[-1]
    if run.latest is not None:
        lat, lab = run.latest, run.latest_labels
        window, bs = f"TTM to {lab['cur'][3:]}", lab["bs"]
        get = lambda m: lat.value(m, lab["ttm"])  # noqa: E731
        getb = lambda m: lat.value(m, bs)  # noqa: E731
        accession = lat.fact("revenue", lab["cur"]).sources[0].accession
        fcf = lat.value("fcf", lab["ttm"])
    else:
        window, bs = last, last
        get = getb = lambda m: ds.value(m, last)  # noqa: E731
        accession = ds.annual_filings[last]
        fcf = ds.value("fcf", last)
    parts = {m: getb(m) for m in ("debt_lt_noncurrent", "debt_lt_current", "finance_lease_liability", "commercial_paper")}
    debt = None if None in parts.values() else sum(parts.values())  # missing is not zero; attest what a company lacks
    missing_debt = [m for m, v in parts.items() if v is None]
    classes, notes = [], []
    for section, shares, printed in cover_classes(int(ds.company.cik), accession):
        if printed:
            sym, note = printed, f"'{section}' priced at its own trading symbol {printed} (cover page)"
        else:
            sym, note = symbol_for(section, symbol_map)
            note += " (no trading symbol on the cover page; config mapping)"
        q = close_on_or_before(sym, price_date)
        classes.append(ClassShares(section=section, shares=shares, symbol=sym, price=q.close, price_date=q.date))
        notes.append(note)
    m = compute(ticker, price_date, classes, window, bs.replace("AT", ""), get("net_income"), get("operating_income"), fcf,
                debt, getb("preferred_equity"), getb("cash"), getb("st_investments"))
    m.notes = notes + ([f"debt component(s) not reported at {bs.replace('AT', '')}: {', '.join(missing_debt)}"]
                       if missing_debt else []) + m.notes
    head = classes[0]
    eps = ds.value("eps_diluted", last)
    m.fy_label = last
    if eps and eps > 0:
        m.pe_fy_eps = head.price / eps
    return m
