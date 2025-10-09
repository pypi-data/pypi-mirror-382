"""Parity checks between DataBento pandas and polars backends."""

import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
import pytest
import pytz

from lumibot.backtesting.databento_backtesting import DataBentoDataBacktesting as DataBentoPandas
from lumibot.data_sources.databento_data_polars_backtesting import DataBentoDataPolarsBacktesting
from lumibot.entities import Asset
from lumibot.credentials import DATABENTO_CONFIG
from lumibot.tools import databento_helper, databento_helper_polars

DATABENTO_API_KEY = DATABENTO_CONFIG.get("API_KEY")


def _clear_databento_caches():
    for cache_dir in (
        databento_helper.LUMIBOT_DATABENTO_CACHE_FOLDER,
        databento_helper_polars.LUMIBOT_DATABENTO_CACHE_FOLDER,
    ):
        path = Path(cache_dir)
        if path.exists():
            shutil.rmtree(path)


@pytest.mark.apitest
@pytest.mark.skipif(
    not DATABENTO_API_KEY or DATABENTO_API_KEY == '<your key here>',
    reason="This test requires a Databento API key",
)
def test_databento_price_parity():
    """Ensure pandas and polars backends deliver identical prices."""

    _clear_databento_caches()

    tz = pytz.timezone("America/New_York")
    start = tz.localize(datetime(2025, 9, 15, 0, 0))
    end = tz.localize(datetime(2025, 9, 29, 23, 59))
    asset = Asset("MES", asset_type=Asset.AssetType.CONT_FUTURE)

    pandas_ds = DataBentoPandas(
        datetime_start=start,
        datetime_end=end,
        api_key=DATABENTO_API_KEY,
        show_progress_bar=False,
    )
    polars_ds = DataBentoDataPolarsBacktesting(
        datetime_start=start,
        datetime_end=end,
        api_key=DATABENTO_API_KEY,
        show_progress_bar=False,
    )

    # Prime caches
    pandas_bars = pandas_ds.get_historical_prices(asset, 500, timestep="minute").df
    polars_bars = polars_ds.get_historical_prices(asset, 500, timestep="minute").df

    pd.testing.assert_frame_equal(polars_bars, pandas_bars)

    checkpoints = [
        (0, 0),
        (3, 40),
        (4, 0),
        (7, 35),
        (11, 5),
        (14, 5),
    ]

    for hour, minute in checkpoints:
        current_dt = tz.localize(datetime(2025, 9, 15, hour, minute))
        pandas_ds._datetime = current_dt
        polars_ds._datetime = current_dt
        pandas_price = pandas_ds.get_last_price(asset)
        polars_price = polars_ds.get_last_price(asset)
        assert pandas_price == pytest.approx(polars_price), (
            f"Mismatch at {current_dt}: pandas={pandas_price}, polars={polars_price}"
        )
