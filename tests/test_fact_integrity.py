def test_fact_table_structure(fact):
    required_columns = {
        "Date_Id",
        "Market_Id",
        "Commodity_Id",
        "Arrival_Qty",
        "Modal_Price",
    }

    assert required_columns.issubset(fact.columns)
    assert not fact.empty


def test_fact_composite_key_not_null(fact):
    key_columns = ["Date_Id", "Market_Id", "Commodity_Id"]

    assert fact[key_columns].notna().all().all()


def test_fact_composite_grain_is_unique(fact):
    key_columns = ["Date_Id", "Market_Id", "Commodity_Id"]

    assert not fact.duplicated(key_columns).any()


def test_fact_date_foreign_keys(fact, dim_date):
    assert fact["Date_Id"].isin(dim_date["Date_Id"]).all()


def test_fact_market_foreign_keys(fact, dim_market):
    assert fact["Market_Id"].isin(dim_market["Market_Id"]).all()


def test_fact_commodity_foreign_keys(fact, dim_commodity):
    assert fact["Commodity_Id"].isin(dim_commodity["Commodity_Id"]).all()


def test_arrival_quantities_are_non_negative(fact):
    assert fact["Arrival_Qty"].notna().all()
    assert (fact["Arrival_Qty"] >= 0).all()


def test_modal_prices_are_non_negative(fact):
    assert fact["Modal_Price"].notna().all()
    assert (fact["Modal_Price"] >= 0).all()
