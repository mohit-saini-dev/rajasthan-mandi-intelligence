from pathlib import Path

import pandas as pd
import pytest


PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


@pytest.fixture(scope="module")
def interruption_audit():
    return pd.read_csv(PROCESSED_DIR / "interruption_audit_summary.csv")


@pytest.fixture(scope="module")
def trailing_findings():
    return pd.read_csv(PROCESSED_DIR / "trailing_silence_final_findings.csv")


@pytest.fixture(scope="module")
def trailing_audit():
    return pd.read_csv(
        PROCESSED_DIR / "trailing_silence_raw_processed_audit.csv"
    )


def test_interruption_audit_monthly_row_counts_match(interruption_audit):
    assert interruption_audit["Monthly_Row_Counts_Match"].notna().all()
    assert interruption_audit["Monthly_Row_Counts_Match"].all()


def test_interruption_audit_active_date_counts_match(interruption_audit):
    assert interruption_audit["Monthly_Active_Date_Counts_Match"].notna().all()
    assert interruption_audit["Monthly_Active_Date_Counts_Match"].all()


def test_trailing_reconciliation_status_values_are_valid(trailing_findings):
    allowed_statuses = {"PASS", "NOT APPLICABLE"}

    assert trailing_findings["Reconciliation_Status"].notna().all()
    assert set(trailing_findings["Reconciliation_Status"].unique()).issubset(
        allowed_statuses
    )


def test_trailing_pass_records_have_matching_month_counts(trailing_findings):
    passed = trailing_findings[
        trailing_findings["Reconciliation_Status"] == "PASS"
    ]

    assert not passed.empty
    assert passed["Reconciliation_Month_Count_Matches"].notna().all()
    assert passed["Reconciliation_Month_Count_Matches"].all()


def test_trailing_audit_active_date_counts_match(trailing_audit):
    assert trailing_audit["Active_Date_Counts_Match"].notna().all()
    assert trailing_audit["Active_Date_Counts_Match"].all()


@pytest.mark.parametrize(
    ("presence_column", "count_column"),
    [
        ("Raw_Source_Records_Present", "Raw_Rows"),
        ("Processed_Records_Present", "Processed_Rows"),
    ],
)
def test_trailing_record_presence_flags_match_row_counts(
    trailing_audit,
    presence_column,
    count_column,
):
    expected_presence = trailing_audit[count_column] > 0

    assert trailing_audit[presence_column].notna().all()
    assert (
        trailing_audit[presence_column].astype(bool).to_numpy()
        == expected_presence.to_numpy()
    ).all()
