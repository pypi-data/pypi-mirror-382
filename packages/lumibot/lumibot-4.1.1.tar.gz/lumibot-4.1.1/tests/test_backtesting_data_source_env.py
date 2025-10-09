"""
Test for BACKTESTING_DATA_SOURCE environment variable handling.
Ensures that datasource_class=None correctly auto-selects from the env var.
"""
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from lumibot.strategies import Strategy
from lumibot.backtesting import (
    PolygonDataBacktesting,
    ThetaDataBacktesting,
    YahooDataBacktesting,
    AlpacaBacktesting,
)


@pytest.fixture
def restore_theta_credentials():
    """Save and restore ThetaData credentials file after test."""
    creds_path = "/Users/robertgrzesik/ThetaData/ThetaTerminal/creds.txt"
    original = None

    # Save original credentials if file exists
    if os.path.exists(creds_path):
        with open(creds_path, 'r') as f:
            original = f.read()

    yield

    # Restore original credentials
    if original is not None:
        with open(creds_path, 'w') as f:
            f.write(original)
    elif os.path.exists(creds_path):
        # File didn't exist before, remove it
        os.remove(creds_path)


@pytest.fixture
def clean_environment():
    """Save and restore environment variables after test."""
    original_env = os.environ.copy()

    yield

    # Restore original environment completely
    os.environ.clear()
    os.environ.update(original_env)


class SimpleTestStrategy(Strategy):
    """Minimal strategy for testing datasource auto-selection."""

    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        if self.first_iteration:
            # Just buy one share to have some activity
            order = self.create_order("SPY", quantity=1, side="buy")
            self.submit_order(order)


class TestBacktestingDataSourceEnv:
    """Test BACKTESTING_DATA_SOURCE environment variable."""

    def test_auto_select_polygon_case_insensitive(self, clean_environment, restore_theta_credentials, caplog):
        """Test that BACKTESTING_DATA_SOURCE=polygon (lowercase) selects PolygonDataBacktesting."""
        # Configure caplog to capture INFO level logs from lumibot.strategies._strategy
        import logging
        caplog.set_level(logging.INFO, logger='lumibot.strategies._strategy')

        with patch.dict(os.environ, {'BACKTESTING_DATA_SOURCE': 'polygon'}):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 10)  # Shorter backtest for speed

            # Run a short backtest to verify env var is read
            SimpleTestStrategy.run_backtest(
                None,  # Auto-select from env var
                backtesting_start=backtesting_start,
                backtesting_end=backtesting_end,
                polygon_api_key="test_key",
                show_plot=False,
                show_tearsheet=False,
                show_indicators=False,
                show_progress_bar=False,
            )

            # Verify the log message shows polygon was selected
            assert any("Auto-selected backtesting data source from BACKTESTING_DATA_SOURCE env var: polygon" in record.message
                      for record in caplog.records)

    def test_auto_select_thetadata_case_insensitive(self, clean_environment, restore_theta_credentials, caplog):
        """Test that BACKTESTING_DATA_SOURCE=THETADATA (uppercase) selects ThetaDataBacktesting."""
        with patch.dict(os.environ, {'BACKTESTING_DATA_SOURCE': 'THETADATA'}):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 10)  # Shorter backtest for speed

            # Try to run backtest - may fail due to test credentials, but that's okay
            try:
                SimpleTestStrategy.run_backtest(
                    None,  # Auto-select from env var
                    backtesting_start=backtesting_start,
                    backtesting_end=backtesting_end,
                    thetadata_username="test_user",
                    thetadata_password="test_pass",
                    show_plot=False,
                    show_tearsheet=False,
                    show_indicators=False,
                    show_progress_bar=False,
                )
            except Exception:
                # Expected to fail with test credentials - that's okay
                pass

            # Verify the log message shows thetadata was selected OR check for ThetaData error
            thetadata_selected = any("Auto-selected backtesting data source from BACKTESTING_DATA_SOURCE env var: THETADATA" in record.message
                                    for record in caplog.records)
            thetadata_attempted = any("Cannot connect to Theta Data" in record.message or "ThetaData" in record.message
                                     for record in caplog.records)
            assert thetadata_selected or thetadata_attempted, "ThetaData was not selected from env var"

    def test_auto_select_yahoo(self, clean_environment, restore_theta_credentials, caplog):
        """Test that BACKTESTING_DATA_SOURCE=Yahoo selects YahooDataBacktesting."""
        with patch.dict(os.environ, {'BACKTESTING_DATA_SOURCE': 'Yahoo'}):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 10)  # Shorter backtest for speed

            # Run a short backtest to verify env var is read
            # If this completes without error, Yahoo was successfully selected
            SimpleTestStrategy.run_backtest(
                None,  # Auto-select from env var
                backtesting_start=backtesting_start,
                backtesting_end=backtesting_end,
                show_plot=False,
                show_tearsheet=False,
                show_indicators=False,
                show_progress_bar=False,
            )

            # If we got here without exception, Yahoo was successfully used
            # (No explicit verification needed - successful backtest is the proof)

    def test_invalid_data_source_raises_error(self, clean_environment, restore_theta_credentials):
        """Test that invalid BACKTESTING_DATA_SOURCE raises ValueError."""
        with patch.dict(os.environ, {'BACKTESTING_DATA_SOURCE': 'InvalidSource'}):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 31)

            with pytest.raises(ValueError, match="Unknown BACKTESTING_DATA_SOURCE"):
                SimpleTestStrategy.run_backtest(
                    None,  # Auto-select from env var
                    backtesting_start=backtesting_start,
                    backtesting_end=backtesting_end,
                    show_plot=False,
                    show_tearsheet=False,
                    show_indicators=False,
                )

    def test_explicit_datasource_overrides_env(self, clean_environment, restore_theta_credentials, caplog):
        """Test that explicit datasource_class overrides BACKTESTING_DATA_SOURCE env var."""
        with patch.dict(os.environ, {'BACKTESTING_DATA_SOURCE': 'polygon'}):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 10)  # Shorter backtest for speed

            # Run backtest with explicit Yahoo datasource despite env saying polygon
            SimpleTestStrategy.run_backtest(
                YahooDataBacktesting,  # Explicit override
                backtesting_start=backtesting_start,
                backtesting_end=backtesting_end,
                show_plot=False,
                show_tearsheet=False,
                show_indicators=False,
                show_progress_bar=False,
            )

            # Verify the auto-select message was NOT logged (explicit datasource was used)
            assert not any("Auto-selected backtesting data source" in record.message
                          for record in caplog.records)

    def test_default_thetadata_when_no_env_set(self, clean_environment, restore_theta_credentials, caplog):
        """Test that ThetaData is the default when BACKTESTING_DATA_SOURCE is not set."""
        # Remove BACKTESTING_DATA_SOURCE from env
        env_without_datasource = {k: v for k, v in os.environ.items() if k != 'BACKTESTING_DATA_SOURCE'}

        with patch.dict(os.environ, env_without_datasource, clear=True):
            # Re-import credentials to pick up env change
            from importlib import reload
            import lumibot.credentials
            reload(lumibot.credentials)

            backtesting_start = datetime(2023, 1, 1)
            backtesting_end = datetime(2023, 1, 10)  # Shorter backtest for speed

            # Try to run backtest - may fail due to test credentials, but that's okay
            try:
                SimpleTestStrategy.run_backtest(
                    None,  # Auto-select from env var (should default to ThetaData)
                    backtesting_start=backtesting_start,
                    backtesting_end=backtesting_end,
                    thetadata_username="test_user",
                    thetadata_password="test_pass",
                    show_plot=False,
                    show_tearsheet=False,
                    show_indicators=False,
                    show_progress_bar=False,
                )
            except Exception:
                # Expected to fail with test credentials - that's okay
                pass

            # Verify ThetaData was attempted (no auto-select message since it's the default)
            assert any("Cannot connect to Theta Data" in record.message or "ThetaData" in record.message
                      for record in caplog.records), "ThetaData was not used as default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
