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
    assert rev.values == [402_836e6, 350_018e6, 307_394e6]  # "$ in Millions" applied


def test_total_rows_negative_parentheses_and_per_share_are_parsed():
    st = parse_r_page((FIX / "googl_fy2025_R5_income.htm").read_bytes())
    assert st.rows_for("us-gaap:OperatingIncomeLoss")[0].values[0] == 129_039e6
    assert st.rows_for("us-gaap:NetIncomeLoss")[0].values[0] == 132_170e6
    eps = st.rows_for("us-gaap:EarningsPerShareDiluted")[0]
    assert eps.unit == "USD/shares" and eps.values == [10.81, 8.04, 5.80]  # not scaled by millions


def test_balance_sheet_instant_columns_and_negative_values():
    st = parse_r_page((FIX / "googl_fy2025_R3_balance.htm").read_bytes())
    assert [(c.months, c.end) for c in st.columns] == [(None, date(2025, 12, 31)), (None, date(2024, 12, 31))]
    aoci = st.rows_for("us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax")[0]
    assert aoci.values == [-1_916e6, -4_800e6]
    assert st.rows_for("us-gaap:Assets")[0].values[0] == 595_281e6
