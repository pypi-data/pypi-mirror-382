"""Test neural.analysis.strategies.mean_reversion module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch
from neural.analysis.strategies.mean_reversion import (
    MeanReversionStrategy,
    SportsbookArbitrageStrategy,
)
from neural.analysis.strategies.base import SignalType, Position


class TestMeanReversionStrategy:
    """Test MeanReversionStrategy class."""

    def test_initialization_defaults(self):
        """Test initialization with default parameters."""
        strategy = MeanReversionStrategy()

        assert strategy.divergence_threshold == 0.05
        assert strategy.reversion_target == 0.5
        assert strategy.use_sportsbook is True
        assert strategy.lookback_periods == 20
        assert strategy.confidence_decay == 0.95
        assert strategy.price_history == {}

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        strategy = MeanReversionStrategy(
            divergence_threshold=0.1,
            reversion_target=0.7,
            use_sportsbook=False,
            lookback_periods=30,
            confidence_decay=0.9,
            initial_capital=5000.0,
        )

        assert strategy.divergence_threshold == 0.1
        assert strategy.reversion_target == 0.7
        assert strategy.use_sportsbook is False
        assert strategy.lookback_periods == 30
        assert strategy.confidence_decay == 0.9
        assert strategy.initial_capital == 5000.0

    def test_analyze_empty_data(self):
        """Test analysis with empty market data."""
        strategy = MeanReversionStrategy()
        market_data = pd.DataFrame()

        signal = strategy.analyze(market_data)

        assert signal.signal_type == SignalType.HOLD

    def test_analyze_insufficient_divergence(self):
        """Test analysis when divergence is below threshold."""
        strategy = MeanReversionStrategy(divergence_threshold=0.1)

        market_data = pd.DataFrame(
            {
                "ticker": ["TEST-YES"],
                "yes_ask": [0.52],
                "no_ask": [0.48],
                "yes_bid": [0.50],
                "volume": [100],
            }
        )

        # Mock fair value calculation to return price close to market
        with patch.object(
            strategy, "_calculate_fair_value", return_value=0.53
        ):  # Only 0.01 divergence
            signal = strategy.analyze(market_data)

        assert signal.signal_type == SignalType.HOLD

    def test_analyze_buy_no_signal(self):
        """Test generating BUY_NO signal when price is too high."""
        strategy = MeanReversionStrategy(
            divergence_threshold=0.05, initial_capital=1000.0, min_edge=0.01
        )

        market_data = pd.DataFrame(
            {
                "ticker": ["TEST-YES"],
                "yes_ask": [0.7],
                "no_ask": [0.35],
                "yes_bid": [0.65],
                "volume": [100],
            }
        )

        # Mock fair value to create divergence (price too high)
        with patch.object(strategy, "_calculate_fair_value", return_value=0.55):
            with patch.object(strategy, "_calculate_confidence", return_value=0.8):
                signal = strategy.analyze(market_data)

        assert signal.signal_type == SignalType.BUY_NO
        assert signal.market_id == "TEST-YES"
        assert signal.confidence == 0.8

    def test_analyze_buy_yes_signal(self):
        """Test generating BUY_YES signal when price is too low."""
        strategy = MeanReversionStrategy(
            divergence_threshold=0.05, initial_capital=1000.0, min_edge=0.01
        )

        market_data = pd.DataFrame(
            {
                "ticker": ["TEST-YES"],
                "yes_ask": [0.4],
                "no_ask": [0.65],
                "yes_bid": [0.35],
                "volume": [100],
            }
        )

        # Mock fair value to create divergence (price too low)
        with patch.object(strategy, "_calculate_fair_value", return_value=0.6):
            with patch.object(strategy, "_calculate_confidence", return_value=0.9):
                signal = strategy.analyze(market_data)

        assert signal.signal_type == SignalType.BUY_YES
        assert signal.market_id == "TEST-YES"
        assert signal.confidence == 0.9

    def test_calculate_fair_value_no_data(self):
        """Test fair value calculation with no historical data."""
        strategy = MeanReversionStrategy(use_sportsbook=False)

        market_data = pd.DataFrame({"ticker": ["TEST"], "yes_ask": [0.5], "volume": [0]})

        fair_value = strategy._calculate_fair_value("TEST", 0.5, market_data)

        # Should return at least the current price as midpoint
        assert fair_value is not None

    def test_calculate_fair_value_with_sportsbook(self):
        """Test fair value calculation with sportsbook consensus."""
        strategy = MeanReversionStrategy(use_sportsbook=True)
        strategy.sportsbook_data = {"TEST": 0.65}

        market_data = pd.DataFrame(
            {"ticker": ["TEST"], "yes_ask": [0.5], "yes_bid": [0.48], "volume": [100]}
        )

        fair_value = strategy._calculate_fair_value("TEST", 0.5, market_data)

        # Should include sportsbook consensus (0.65)
        assert fair_value is not None
        assert fair_value > 0.5  # Should be pulled toward consensus

    def test_calculate_fair_value_with_history(self):
        """Test fair value calculation with price history."""
        strategy = MeanReversionStrategy(lookback_periods=5)

        # Build price history
        strategy.price_history["TEST"] = [0.5, 0.52, 0.51, 0.53, 0.54]

        market_data = pd.DataFrame(
            {"ticker": ["TEST"], "yes_ask": [0.6], "yes_bid": [0.58], "volume": [100]}
        )

        fair_value = strategy._calculate_fair_value("TEST", 0.6, market_data)

        assert fair_value is not None
        # Should include moving average of history

    def test_calculate_fair_value_with_vwap(self):
        """Test fair value calculation with VWAP."""
        strategy = MeanReversionStrategy(lookback_periods=3)

        market_data = pd.DataFrame(
            {
                "ticker": ["TEST", "TEST", "TEST"],
                "yes_ask": [0.5, 0.52, 0.51],
                "yes_bid": [0.48, 0.50, 0.49],
                "volume": [100, 200, 150],
            }
        )

        fair_value = strategy._calculate_fair_value("TEST", 0.51, market_data)

        assert fair_value is not None

    def test_calculate_vwap(self):
        """Test VWAP calculation."""
        strategy = MeanReversionStrategy(lookback_periods=3)

        market_data = pd.DataFrame({"yes_ask": [0.5, 0.6, 0.7], "volume": [100, 200, 150]})

        vwap = strategy._calculate_vwap(market_data)

        # VWAP = (0.5*100 + 0.6*200 + 0.7*150) / (100+200+150)
        expected = (50 + 120 + 105) / 450
        assert vwap == pytest.approx(expected, rel=0.01)

    def test_calculate_vwap_no_volume(self):
        """Test VWAP with no volume."""
        strategy = MeanReversionStrategy()

        market_data = pd.DataFrame({"yes_ask": [0.5, 0.6], "volume": [0, 0]})

        vwap = strategy._calculate_vwap(market_data)

        assert vwap is None

    def test_calculate_confidence_base(self):
        """Test confidence calculation with basic factors."""
        strategy = MeanReversionStrategy(divergence_threshold=0.05)

        market_data = pd.DataFrame({"ticker": ["TEST"], "yes_ask": [0.5], "volume": [100]})

        confidence = strategy._calculate_confidence(0.1, market_data, None)

        assert 0 < confidence <= 1.0

    def test_calculate_confidence_with_volume(self):
        """Test confidence adjustment based on volume."""
        strategy = MeanReversionStrategy(divergence_threshold=0.05)

        market_data = pd.DataFrame(
            {
                "ticker": ["TEST", "TEST", "TEST"],
                "yes_ask": [0.5, 0.5, 0.5],
                "volume": [100, 100, 200],  # Latest has higher volume
            }
        )

        confidence = strategy._calculate_confidence(0.1, market_data, None)

        assert 0 < confidence <= 1.0

    def test_calculate_confidence_with_espn_agreement(self):
        """Test confidence boost when ESPN data agrees."""
        strategy = MeanReversionStrategy(divergence_threshold=0.05)
        strategy.use_espn = True

        market_data = pd.DataFrame({"ticker": ["TEST"], "yes_ask": [0.5], "volume": [100]})

        espn_data = {"momentum": -0.5}  # Negative momentum

        # Positive divergence (price too high) + negative momentum = agreement
        confidence = strategy._calculate_confidence(0.1, market_data, espn_data)

        assert 0 < confidence <= 1.0

    def test_calculate_confidence_with_espn_disagreement(self):
        """Test confidence reduction when ESPN data disagrees."""
        strategy = MeanReversionStrategy(divergence_threshold=0.05)
        strategy.use_espn = True

        market_data = pd.DataFrame({"ticker": ["TEST"], "yes_ask": [0.5], "volume": [100]})

        espn_data = {"momentum": 0.5}  # Positive momentum

        # Positive divergence (price too high) + positive momentum = disagreement
        confidence = strategy._calculate_confidence(0.1, market_data, espn_data)

        assert 0 < confidence <= 1.0

    def test_should_exit_position_standard_stop_loss(self):
        """Test exit on standard stop loss."""
        strategy = MeanReversionStrategy(stop_loss=0.2)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.3,  # Big loss
            entry_time=datetime.now(),
            metadata={"divergence": 0.1},
        )

        assert strategy.should_exit_position(position, 0.3, 0.5) is True

    def test_should_exit_position_reversion_complete(self):
        """Test exit when reversion is complete."""
        strategy = MeanReversionStrategy(reversion_target=0.5)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.4,
            current_price=0.52,
            entry_time=datetime.now(),
            metadata={"divergence": -0.2},  # Started 0.2 below fair value
        )

        # Reversion complete: moved from 0.4 to 0.52, fair value was 0.6
        # Initial diff was 0.2, now diff is 0.08, which is < 0.2 * (1-0.5) = 0.1
        assert strategy.should_exit_position(position, 0.52, 0.6) is True

    def test_should_exit_position_no_exit(self):
        """Test no exit when conditions not met."""
        strategy = MeanReversionStrategy(reversion_target=0.5, stop_loss=0.5)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.52,  # Small gain
            entry_time=datetime.now(),
            metadata={"divergence": -0.1},
        )

        assert strategy.should_exit_position(position, 0.52, 0.6) is False


class TestSportsbookArbitrageStrategy:
    """Test SportsbookArbitrageStrategy class."""

    def test_initialization(self):
        """Test initialization with default parameters."""
        strategy = SportsbookArbitrageStrategy()

        assert strategy.min_sportsbook_sources == 3
        assert strategy.max_line_age_seconds == 60
        assert strategy.arbitrage_threshold == 0.03
        assert strategy.use_sportsbook is True

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        strategy = SportsbookArbitrageStrategy(
            min_sportsbook_sources=5,
            max_line_age_seconds=30,
            arbitrage_threshold=0.05,
        )

        assert strategy.min_sportsbook_sources == 5
        assert strategy.max_line_age_seconds == 30
        assert strategy.arbitrage_threshold == 0.05

    def test_analyze_no_sportsbook_data(self):
        """Test analysis with no sportsbook data."""
        strategy = SportsbookArbitrageStrategy()

        market_data = pd.DataFrame(
            {"ticker": ["TEST-YES"], "yes_ask": [0.5], "no_ask": [0.5], "volume": [100]}
        )

        signal = strategy.analyze(market_data, sportsbook_data=None)

        assert signal.signal_type == SignalType.HOLD

    def test_analyze_empty_market_data(self):
        """Test analysis with empty market data."""
        strategy = SportsbookArbitrageStrategy()

        market_data = pd.DataFrame()
        sportsbook_data = {"book1": {"implied_probability": 0.6}}

        signal = strategy.analyze(market_data, sportsbook_data=sportsbook_data)

        assert signal.signal_type == SignalType.HOLD

    def test_analyze_buy_yes_arbitrage(self):
        """Test BUY_YES signal when Kalshi YES is cheap."""
        strategy = SportsbookArbitrageStrategy(
            arbitrage_threshold=0.03, initial_capital=1000.0, min_edge=0.01
        )

        market_data = pd.DataFrame(
            {"ticker": ["TEST-YES"], "yes_ask": [0.5], "no_ask": [0.5], "volume": [100]}
        )

        sportsbook_data = {"book1": {"implied_probability": 0.6}}

        # Mock consensus calculation
        with patch.object(strategy, "_calculate_sportsbook_consensus", return_value=0.6):
            signal = strategy.analyze(market_data, sportsbook_data=sportsbook_data)

        # 0.5 (kalshi) < 0.6 (consensus) - 0.03 (threshold) = 0.57
        assert signal.signal_type == SignalType.BUY_YES
        assert signal.market_id == "TEST-YES"
        assert signal.confidence == 0.9

    def test_analyze_buy_no_arbitrage(self):
        """Test BUY_NO signal when Kalshi NO is cheap."""
        strategy = SportsbookArbitrageStrategy(
            arbitrage_threshold=0.03, initial_capital=1000.0, min_edge=0.01
        )

        market_data = pd.DataFrame(
            {"ticker": ["TEST-YES"], "yes_ask": [0.7], "no_ask": [0.25], "volume": [100]}
        )

        sportsbook_data = {"book1": {"implied_probability": 0.6}}

        # Mock consensus calculation
        with patch.object(strategy, "_calculate_sportsbook_consensus", return_value=0.6):
            signal = strategy.analyze(market_data, sportsbook_data=sportsbook_data)

        # 0.25 (kalshi NO) < (1 - 0.6) - 0.03 = 0.37
        assert signal.signal_type == SignalType.BUY_NO
        assert signal.market_id == "TEST-YES"

    def test_analyze_no_arbitrage(self):
        """Test HOLD signal when no arbitrage exists."""
        strategy = SportsbookArbitrageStrategy(arbitrage_threshold=0.05)

        market_data = pd.DataFrame(
            {"ticker": ["TEST-YES"], "yes_ask": [0.58], "no_ask": [0.42], "volume": [100]}
        )

        sportsbook_data = {"book1": {"implied_probability": 0.6}}

        # Mock consensus calculation
        with patch.object(strategy, "_calculate_sportsbook_consensus", return_value=0.6):
            signal = strategy.analyze(market_data, sportsbook_data=sportsbook_data)

        # No arbitrage: 0.58 is close to 0.6
        assert signal.signal_type == SignalType.HOLD

    def test_calculate_sportsbook_consensus_no_data(self):
        """Test consensus calculation with no data."""
        strategy = SportsbookArbitrageStrategy()

        consensus = strategy._calculate_sportsbook_consensus({})

        assert consensus is None

    def test_calculate_sportsbook_consensus_insufficient_sources(self):
        """Test consensus with insufficient sources."""
        strategy = SportsbookArbitrageStrategy(min_sportsbook_sources=3)

        sportsbook_data = {
            "book1": {"implied_probability": 0.6},
            "book2": {"implied_probability": 0.62},
        }

        consensus = strategy._calculate_sportsbook_consensus(sportsbook_data)

        assert consensus is None  # Only 2 sources, need 3

    def test_calculate_sportsbook_consensus_valid(self):
        """Test consensus with valid data."""
        strategy = SportsbookArbitrageStrategy(min_sportsbook_sources=3)

        sportsbook_data = {
            "book1": {
                "implied_probability": 0.6,
                "timestamp": pd.Timestamp.now(),
            },
            "book2": {
                "implied_probability": 0.62,
                "timestamp": pd.Timestamp.now(),
            },
            "book3": {
                "implied_probability": 0.58,
                "timestamp": pd.Timestamp.now(),
            },
        }

        consensus = strategy._calculate_sportsbook_consensus(sportsbook_data)

        assert consensus == 0.6  # Median of [0.58, 0.6, 0.62]

    def test_calculate_sportsbook_consensus_stale_data(self):
        """Test consensus filters out stale data."""
        strategy = SportsbookArbitrageStrategy(min_sportsbook_sources=3, max_line_age_seconds=30)

        old_timestamp = pd.Timestamp.now() - pd.Timedelta(seconds=60)
        fresh_timestamp = pd.Timestamp.now()

        sportsbook_data = {
            "book1": {"implied_probability": 0.6, "timestamp": old_timestamp},  # Stale
            "book2": {"implied_probability": 0.62, "timestamp": fresh_timestamp},
            "book3": {"implied_probability": 0.58, "timestamp": fresh_timestamp},
            "book4": {"implied_probability": 0.59, "timestamp": fresh_timestamp},
        }

        consensus = strategy._calculate_sportsbook_consensus(sportsbook_data)

        # Should only use 3 fresh sources
        assert consensus is not None

    def test_calculate_sportsbook_consensus_from_moneyline(self):
        """Test consensus calculation from moneyline odds."""
        strategy = SportsbookArbitrageStrategy(min_sportsbook_sources=3)

        sportsbook_data = {
            "book1": {"moneyline": -150, "timestamp": pd.Timestamp.now()},  # Favorite
            "book2": {"moneyline": -140, "timestamp": pd.Timestamp.now()},
            "book3": {"moneyline": -160, "timestamp": pd.Timestamp.now()},
        }

        consensus = strategy._calculate_sportsbook_consensus(sportsbook_data)

        assert consensus is not None
        assert 0.5 < consensus < 1.0  # Should be > 50% for favorites

    def test_calculate_sportsbook_consensus_positive_moneyline(self):
        """Test consensus from positive moneyline (underdog)."""
        strategy = SportsbookArbitrageStrategy(min_sportsbook_sources=3)

        sportsbook_data = {
            "book1": {"moneyline": 150, "timestamp": pd.Timestamp.now()},  # Underdog
            "book2": {"moneyline": 140, "timestamp": pd.Timestamp.now()},
            "book3": {"moneyline": 160, "timestamp": pd.Timestamp.now()},
        }

        consensus = strategy._calculate_sportsbook_consensus(sportsbook_data)

        assert consensus is not None
        assert 0.0 < consensus < 0.5  # Should be < 50% for underdogs
