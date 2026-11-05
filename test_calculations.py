import pandas as pd
from data_tools import clean_data, build_summary, find_missing_columns, guess_column
from ai_analyst import find_unverified_numbers


def sample_table():
    return pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "product": ["A", "B", "A", "C"],
        "quantity": [2, 3, 1, None],
        "unit_price": [100, 50, 100, 10],
        "customer_region": ["Lagos", "Abuja", "Lagos", "Ibadan"],
    })


def test_rows_with_missing_quantity_are_removed():
    df = clean_data(sample_table())
    assert len(df) == 3


def test_revenue_is_quantity_times_price():
    df = clean_data(sample_table())
    assert df["revenue"].tolist() == [200, 150, 100]


def test_total_sales():
    summary = build_summary(clean_data(sample_table()))
    assert summary["total_sales_naira"] == 450


def test_best_product_and_its_share():
    summary = build_summary(clean_data(sample_table()))
    assert summary["best_product"] == "A"
    assert summary["best_product_share_percent"] == 66.7


def test_weakest_product_and_best_city():
    summary = build_summary(clean_data(sample_table()))
    assert summary["weakest_product"] == "B"
    assert summary["best_region"] == "Lagos"


def test_dates_ignore_removed_rows():
    summary = build_summary(clean_data(sample_table()))
    assert summary["first_date"] == "2026-01-01"
    assert summary["last_date"] == "2026-01-03"


def test_missing_columns_are_found():
    df = pd.DataFrame({"date": ["2026-01-01"], "product": ["A"]})
    assert find_missing_columns(df) == ["quantity", "unit_price", "customer_region"]


def test_column_guessing():
    assert guess_column("quantity", ["Date", "Item", "Qty"]) == "Qty"
    assert guess_column("date", ["Item", "Qty"]) is None


def test_checker_catches_a_made_up_number():
    facts = {"total": 450}
    assert find_unverified_numbers("Sales were 999 Naira.", facts) == ["999"]


def test_checker_accepts_a_real_number():
    facts = {"total": 450}
    assert find_unverified_numbers("Sales were 450 Naira.", facts) == []