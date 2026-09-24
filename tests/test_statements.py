"""Parser for SEC-rendered statement pages (R files), tested on real Alphabet FY2025 pages."""

from datetime import date
from pathlib import Path

from fre.statements import parse_r_page

FIX = Path(__file__).parent / "fixtures"


def test_income_statement_columns_scale_and_rows():
    st = parse_r_page((FIX / "googl_fy2025_R5_income.htm").read_bytes())
    assert st.title.startswith("CONSOLIDATED STATEMENTS OF INCOME")
    assert [(c.months, c.end) for c in st.columns] == [
        (12, date(2025, 12, 31)), (12, date(2024, 12, 31)), (12, date(2023, 12, 31))]
    rev = st.rows_for("us-gaap:Revenues")[0]
    assert rev.label == "Revenues"
    assert rev.raw == [402_836, 350_018, 307_394]
    assert st.scaled(rev, 0, "USD") == 402_836e6  # "$ in Millions" applied by the fact's unit


def test_total_rows_negative_parentheses_and_per_share_are_parsed():
    st = parse_r_page((FIX / "googl_fy2025_R5_income.htm").read_bytes())
    assert st.scaled(st.rows_for("us-gaap:OperatingIncomeLoss")[0], 0, "USD") == 129_039e6
    assert st.scaled(st.rows_for("us-gaap:NetIncomeLoss")[0], 0, "USD") == 132_170e6
    eps = st.rows_for("us-gaap:EarningsPerShareDiluted")[0]
    assert [st.scaled(eps, i, "USD/shares") for i in range(3)] == [10.81, 8.04, 5.80]  # never scaled


def test_balance_sheet_instant_columns_and_negative_values():
    st = parse_r_page((FIX / "googl_fy2025_R3_balance.htm").read_bytes())
    assert [(c.months, c.end) for c in st.columns] == [(None, date(2025, 12, 31)), (None, date(2024, 12, 31))]
    aoci = st.rows_for("us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax")[0]
    assert aoci.raw == [-1_916, -4_800]
    assert st.scaled(st.rows_for("us-gaap:Assets")[0], 0, "USD") == 595_281e6


def test_share_rows_use_the_share_scale_not_the_dollar_scale():
    st = parse_r_page(MSFT_LIKE)
    assert st.usd_scale == 1e6 and st.share_scale == 1e6
    basic = st.rows_for("us-gaap:EarningsPerShareBasic")[0]
    assert st.scaled(basic, 0, "USD/shares") == 18.00  # label is just "Basic"; the unit decides


MSFT_LIKE = b"""<table>
<tr><th class="tl" colspan="1"><div><strong>INCOME STATEMENTS - USD ($) shares in Millions, $ in Millions</strong></div></th>
<th class="th" colspan="1">12 Months Ended</th></tr>
<tr><th class="th"><div>Jun. 30, 2026</div></th></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_EarningsPerShareBasic', window );">Basic</a></td>
<td class="nump">$ 18.00<span></span></td></tr>
</table>"""


COVER = b"""<table>
<tr><th class="tl"><div><strong>COVER PAGE - shares shares in Millions</strong></div></th><th class="th" colspan="1">6 Months Ended</th><th class="th"></th></tr>
<tr><th class="th"><div>Jun. 30, 2026</div></th><th class="th"><div>Jul. 15, 2026</div></th></tr>
<tr class="rh"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_StatementClassOfStockAxis', window );"><strong>Class A Common Stock</strong></a></td><td class="text"></td><td class="text"></td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_dei_TradingSymbol', window );">Trading Symbol</a></td><td class="text">GOOGL</td><td class="text"></td></tr>
<tr class="re"><td class="pl"><a onclick="Show.showAR( this, 'defref_dei_SecurityExchangeName', window );">Security Exchange Name</a></td><td class="text">NASDAQ</td><td class="text"></td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_dei_EntityCommonStockSharesOutstanding', window );">Entity Common Stock, Shares Outstanding</a></td><td class="text"></td><td class="nump">5,868<span></span></td></tr>
<tr class="rh"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_StatementClassOfStockAxis', window );"><strong>Class B Common Stock</strong></a></td><td class="text"></td><td class="text"></td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_dei_EntityCommonStockSharesOutstanding', window );">Entity Common Stock, Shares Outstanding</a></td><td class="text"></td><td class="nump">835<span></span></td></tr>
</table>"""


def test_rows_remember_the_section_they_sit_under_and_text_rows_are_not_headings():
    st = parse_r_page(COVER)
    rows = st.rows_for("dei:EntityCommonStockSharesOutstanding")
    assert [r.section for r in rows] == ["Class A Common Stock", "Class B Common Stock"]
    assert [st.scaled(r, 1, "shares") for r in rows] == [5_868e6, 835e6]


def test_cover_rows_carry_their_trading_symbol_text():
    st = parse_r_page(COVER)
    sym = [r for r in st.rows if r.tag == "dei:TradingSymbol"]
    assert sym[0].section == "Class A Common Stock" and sym[0].text[0] == "GOOGL"


def test_primary_statement_filed_as_uncategorized_is_still_found(monkeypatch):
    """Meta's FY2021 FilingSummary lists its balance sheet under MenuCategory 'Uncategorized'."""
    from fre import statements
    summary = b"""<FilingSummary><MyReports>
<Report instance="x"><HtmlFileName>R3.htm</HtmlFileName><ShortName>CONSOLIDATED BALANCE SHEETS</ShortName><MenuCategory>Uncategorized</MenuCategory></Report>
<Report instance="x"><HtmlFileName>R4.htm</HtmlFileName><ShortName>CONSOLIDATED BALANCE SHEETS (Parenthetical)</ShortName><MenuCategory>Cover</MenuCategory></Report>
<Report instance="x"><HtmlFileName>R9.htm</HtmlFileName><ShortName>Debt (Details)</ShortName><MenuCategory>Details</MenuCategory></Report>
</MyReports></FilingSummary>"""
    pages = {"FilingSummary.xml": summary, "R3.htm": (FIX / "googl_fy2025_R3_balance.htm").read_bytes()}
    monkeypatch.setattr(statements.snapshot, "fetch", lambda url, **k: url.rsplit("/", 1)[1])
    monkeypatch.setattr(statements.snapshot, "load_bytes", lambda sid: pages[sid])
    got = statements.primary_statements(1, "0000000001-22-000001")
    assert [s.title.split(" - ")[0] for s in got] == ["CONSOLIDATED BALANCE SHEETS"]
