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
