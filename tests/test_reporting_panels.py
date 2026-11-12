def test_monthly_panel_structure(monthly_reporting_panel):
    required_columns = {
        "Market_Id",
        "Commodity_Id",
        "Commodity_Name",
        "Year",
        "Month_Num",
        "Month",
        "Expected_Pair_Days",
        "Reported_Pair_Days",
    }

    assert required_columns.issubset(monthly_reporting_panel.columns)
    assert not monthly_reporting_panel.empty


def test_monthly_panel_pair_month_grain_is_unique(monthly_reporting_panel):
    key_columns = ["Market_Id", "Commodity_Id", "Year", "Month_Num"]

    assert not monthly_reporting_panel.duplicated(key_columns).any()


def test_monthly_panel_has_no_null_key_fields(monthly_reporting_panel):
    key_columns = ["Market_Id", "Commodity_Id", "Year", "Month_Num"]

    assert monthly_reporting_panel[key_columns].notna().all().all()


def test_monthly_panel_expected_days_are_positive(monthly_reporting_panel):
    assert (monthly_reporting_panel["Expected_Pair_Days"] > 0).all()


def test_monthly_panel_reported_days_are_non_negative(monthly_reporting_panel):
    assert (monthly_reporting_panel["Reported_Pair_Days"] >= 0).all()


def test_monthly_panel_reported_days_do_not_exceed_expected_days(
    monthly_reporting_panel,
):
    assert (
        monthly_reporting_panel["Reported_Pair_Days"]
        <= monthly_reporting_panel["Expected_Pair_Days"]
    ).all()
