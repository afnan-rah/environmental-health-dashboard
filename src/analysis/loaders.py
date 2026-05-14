"""Load cleaned datasets for analysis and dashboards."""

from __future__ import annotations

import pandas as pd

from src.utils.paths import ARSENIC_CLEAN_CSV, MOSQUITO_CLEAN_CSV


def load_arsenic_cleaned() -> pd.DataFrame:
    return pd.read_csv(
        ARSENIC_CLEAN_CSV,
        parse_dates=["test_date"],
        dtype={"zip5": str},
    )


def load_mosquito_cleaned() -> pd.DataFrame:
    return pd.read_csv(
        MOSQUITO_CLEAN_CSV,
        parse_dates=["trap_set_date", "trap_pickup_date"],
    )
