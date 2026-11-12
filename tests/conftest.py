from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture(scope="session")
def dim_date():
    return pd.read_csv(PROCESSED_DIR / "dim_date.csv")


@pytest.fixture(scope="session")
def dim_market():
    return pd.read_csv(PROCESSED_DIR / "dim_market.csv")


@pytest.fixture(scope="session")
def dim_commodity():
    return pd.read_csv(PROCESSED_DIR / "dim_commodity.csv")


@pytest.fixture(scope="session")
def fact():
    return pd.read_csv(PROCESSED_DIR / "fact_market_arrivals.csv")


@pytest.fixture(scope="session")
def monthly_reporting_panel():
    return pd.read_csv(
        PROCESSED_DIR / "monthly_reporting_pair_month_panel.csv"
    )
