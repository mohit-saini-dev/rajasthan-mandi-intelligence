def test_date_dimension_structure(dim_date):
    required_columns = {
        "Date",
        "Date_Id",
        "Year",
        "Quarter",
        "Month_No",
        "Month_Name",
        "Day_Name",
        "Is_Weekend",
    }

    assert required_columns.issubset(dim_date.columns)
    assert not dim_date.empty


def test_date_dimension_primary_key(dim_date):
    assert dim_date["Date_Id"].notna().all()
    assert dim_date["Date_Id"].is_unique


def test_market_dimension_structure(dim_market):
    required_columns = {"Market_Name", "Market_Id"}

    assert required_columns.issubset(dim_market.columns)
    assert not dim_market.empty


def test_market_dimension_primary_key(dim_market):
    assert dim_market["Market_Id"].notna().all()
    assert dim_market["Market_Id"].is_unique


def test_commodity_dimension_structure(dim_commodity):
    required_columns = {"Commodity_Name", "Commodity_Id"}

    assert required_columns.issubset(dim_commodity.columns)
    assert not dim_commodity.empty


def test_commodity_dimension_primary_key(dim_commodity):
    assert dim_commodity["Commodity_Id"].notna().all()
    assert dim_commodity["Commodity_Id"].is_unique
