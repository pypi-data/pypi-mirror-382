"""Test neural.analysis.strategies.base module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch
from neural.analysis.strategies.base import (
    Strategy,
    BaseStrategy,
    StrategyConfig,
    Signal,
    SignalType,
    Position,
)


class ConcreteStrategy(Strategy):
    """Concrete implementation for testing abstract Strategy class."""

    def analyze(self, market_data, espn_data=None, **kwargs):
        """Simple implementation that returns HOLD signal."""
        return self.hold()


class TestStrategyConfig:
    """Test StrategyConfig dataclass."""

    def test_strategy_config_defaults(self):
        """Test default configuration values."""
        config = StrategyConfig()

        assert config.max_position_size == 0.1
        assert config.min_edge == 0.03
        assert config.use_kelly is False
        assert config.kelly_fraction == 0.25
        assert config.stop_loss is None
        assert config.take_profit is None
        assert config.max_positions == 10
        assert config.fee_rate == 0.0

    def test_strategy_config_custom(self):
        """Test custom configuration values."""
        config = StrategyConfig(
            max_position_size=0.2,
            min_edge=0.05,
            use_kelly=True,
            kelly_fraction=0.5,
            stop_loss=0.3,
            take_profit=1.0,
            max_positions=5,
            fee_rate=0.01,
        )

        assert config.max_position_size == 0.2
        assert config.min_edge == 0.05
        assert config.use_kelly is True
        assert config.kelly_fraction == 0.5
        assert config.stop_loss == 0.3
        assert config.take_profit == 1.0
        assert config.max_positions == 5
        assert config.fee_rate == 0.01


class TestSignalType:
    """Test SignalType enum."""

    def test_signal_types(self):
        """Test all signal type values."""
        assert SignalType.BUY_YES.value == "buy_yes"
        assert SignalType.BUY_NO.value == "buy_no"
        assert SignalType.SELL_YES.value == "sell_yes"
        assert SignalType.SELL_NO.value == "sell_no"
        assert SignalType.HOLD.value == "hold"
        assert SignalType.CLOSE.value == "close"


class TestSignal:
    """Test Signal dataclass."""

    def test_signal_creation(self):
        """Test creating a signal with required fields."""
        signal = Signal(
            signal_type=SignalType.BUY_YES,
            market_id="TESTMARKET",
            recommended_size=0.1,
            confidence=0.8,
        )

        assert signal.signal_type == SignalType.BUY_YES
        assert signal.market_id == "TESTMARKET"
        assert signal.recommended_size == 0.1
        assert signal.confidence == 0.8
        assert signal.timestamp is not None

    def test_signal_with_optional_fields(self):
        """Test signal with optional fields."""
        metadata = {"reason": "test"}
        signal = Signal(
            signal_type=SignalType.BUY_NO,
            market_id="TESTMARKET",
            recommended_size=0.15,
            confidence=0.9,
            edge=0.05,
            expected_value=1.5,
            max_contracts=100,
            stop_loss_price=0.3,
            take_profit_price=0.7,
            metadata=metadata,
        )

        assert signal.edge == 0.05
        assert signal.expected_value == 1.5
        assert signal.max_contracts == 100
        assert signal.stop_loss_price == 0.3
        assert signal.take_profit_price == 0.7
        assert signal.metadata == metadata

    def test_signal_backward_compatibility(self):
        """Test backward compatibility properties."""
        signal = Signal(
            signal_type=SignalType.BUY_YES,
            market_id="TESTMARKET",
            recommended_size=0.1,
            confidence=0.8,
        )

        assert signal.type == SignalType.BUY_YES
        assert signal.ticker == "TESTMARKET"
        assert signal.size == 0.1


class TestPosition:
    """Test Position dataclass."""

    def test_position_creation(self):
        """Test creating a position."""
        entry_time = datetime.now()
        position = Position(
            ticker="TESTMARKET",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.6,
            entry_time=entry_time,
        )

        assert position.ticker == "TESTMARKET"
        assert position.side == "yes"
        assert position.size == 100
        assert position.entry_price == 0.5
        assert position.current_price == 0.6
        assert position.entry_time == entry_time

    def test_position_pnl_yes_side(self):
        """Test P&L calculation for YES position."""
        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.6,
            entry_time=datetime.now(),
        )

        assert position.pnl == pytest.approx(10.0, rel=0.01)  # (0.6 - 0.5) * 100

    def test_position_pnl_no_side(self):
        """Test P&L calculation for NO position."""
        position = Position(
            ticker="TEST",
            side="no",
            size=100,
            entry_price=0.4,
            current_price=0.3,
            entry_time=datetime.now(),
        )

        assert position.pnl == pytest.approx(10.0, rel=0.01)  # (0.4 - 0.3) * 100

    def test_position_pnl_percentage(self):
        """Test P&L percentage calculation."""
        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.6,
            entry_time=datetime.now(),
        )

        assert position.pnl_percentage == pytest.approx(20.0, rel=0.01)  # 10 / (0.5 * 100) * 100


class TestStrategy:
    """Test Strategy base class."""

    def test_strategy_initialization_defaults(self):
        """Test strategy initialization with default values."""
        strategy = ConcreteStrategy()

        assert strategy.name == "ConcreteStrategy"
        assert strategy.initial_capital == 1000.0
        assert strategy.current_capital == 1000.0
        assert strategy.max_position_size == 0.1
        assert strategy.min_edge == 0.03
        assert strategy.use_kelly is False
        assert strategy.kelly_fraction == 0.25
        assert strategy.stop_loss is None
        assert strategy.take_profit is None
        assert strategy.max_positions == 10
        assert strategy.fee_rate == 0.0
        assert strategy.positions == []
        assert strategy.signals == []
        assert strategy.trade_history == []

    def test_strategy_initialization_custom(self):
        """Test strategy initialization with custom values."""
        strategy = ConcreteStrategy(
            name="CustomStrategy",
            initial_capital=5000.0,
            max_position_size=0.2,
            min_edge=0.05,
            use_kelly=True,
            kelly_fraction=0.5,
            stop_loss=0.3,
            take_profit=1.0,
            max_positions=5,
            fee_rate=0.01,
        )

        assert strategy.name == "CustomStrategy"
        assert strategy.initial_capital == 5000.0
        assert strategy.current_capital == 5000.0
        assert strategy.max_position_size == 0.2
        assert strategy.min_edge == 0.05
        assert strategy.use_kelly is True
        assert strategy.kelly_fraction == 0.5
        assert strategy.stop_loss == 0.3
        assert strategy.take_profit == 1.0
        assert strategy.max_positions == 5
        assert strategy.fee_rate == 0.01

    def test_calculate_edge(self):
        """Test edge calculation."""
        strategy = ConcreteStrategy()

        edge = strategy.calculate_edge(true_probability=0.6, market_price=0.5, confidence=1.0)
        assert edge == pytest.approx(0.1, rel=0.01)

        edge = strategy.calculate_edge(true_probability=0.6, market_price=0.5, confidence=0.5)
        assert edge == pytest.approx(0.05, rel=0.01)

    def test_calculate_position_size_no_edge(self):
        """Test position size calculation with insufficient edge."""
        strategy = ConcreteStrategy(min_edge=0.05)

        size = strategy.calculate_position_size(edge=0.02, odds=2.0, confidence=1.0)
        assert size == 0

    def test_calculate_position_size_fixed_percentage(self):
        """Test position size with fixed percentage."""
        strategy = ConcreteStrategy(
            initial_capital=1000.0, max_position_size=0.1, min_edge=0.03, use_kelly=False
        )

        size = strategy.calculate_position_size(edge=0.05, odds=2.0, confidence=1.0)
        assert size > 0
        assert size <= 100  # Max 10% of 1000

    def test_calculate_position_size_kelly(self):
        """Test position size with Kelly criterion."""
        strategy = ConcreteStrategy(
            initial_capital=1000.0,
            use_kelly=True,
            kelly_fraction=0.25,
            max_position_size=0.2,
            min_edge=0.03,
        )

        size = strategy.calculate_position_size(edge=0.1, odds=2.0, confidence=1.0)
        assert size > 0
        assert size <= 200  # Max 20% of 1000

    def test_calculate_fees_custom_rate(self):
        """Test fee calculation with custom rate."""
        strategy = ConcreteStrategy(fee_rate=0.01)

        fees = strategy.calculate_fees(price=0.5, size=100)
        assert fees == 1.0  # 0.01 * 100

    def test_calculate_fees_kalshi_formula(self):
        """Test fee calculation with Kalshi formula."""
        strategy = ConcreteStrategy(fee_rate=0.0)

        fees = strategy.calculate_fees(price=0.5, size=100)
        expected = 0.07 * 0.5 * 0.5 * 100  # 1.75
        assert fees == expected

    def test_get_exposure_ratio_no_positions(self):
        """Test exposure ratio with no positions."""
        strategy = ConcreteStrategy()

        assert strategy.get_exposure_ratio() == 0.0

    def test_get_exposure_ratio_with_positions(self):
        """Test exposure ratio with positions."""
        strategy = ConcreteStrategy(initial_capital=1000.0)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.5,
            entry_time=datetime.now(),
        )
        strategy.positions.append(position)

        exposure = strategy.get_exposure_ratio()
        assert exposure == 0.05  # (100 * 0.5) / 1000

    def test_can_open_position_true(self):
        """Test can open position when allowed."""
        strategy = ConcreteStrategy()

        assert strategy.can_open_position() is True

    def test_can_open_position_max_positions(self):
        """Test can't open position when at max."""
        strategy = ConcreteStrategy(max_positions=2)

        for i in range(2):
            position = Position(
                ticker=f"TEST{i}",
                side="yes",
                size=10,
                entry_price=0.5,
                current_price=0.5,
                entry_time=datetime.now(),
            )
            strategy.positions.append(position)

        assert strategy.can_open_position() is False

    def test_can_open_position_high_exposure(self):
        """Test can't open position when exposure is high."""
        strategy = ConcreteStrategy(initial_capital=1000.0)

        position = Position(
            ticker="TEST",
            side="yes",
            size=1000,
            entry_price=0.85,
            current_price=0.85,
            entry_time=datetime.now(),
        )
        strategy.positions.append(position)

        assert strategy.can_open_position() is False

    def test_buy_yes_signal(self):
        """Test generating BUY_YES signal."""
        strategy = ConcreteStrategy()

        signal = strategy.buy_yes(ticker="TEST", size=100, confidence=0.8)

        assert signal.signal_type == SignalType.BUY_YES
        assert signal.market_id == "TEST"
        assert signal.confidence == 0.8

    def test_buy_no_signal(self):
        """Test generating BUY_NO signal."""
        strategy = ConcreteStrategy()

        signal = strategy.buy_no(ticker="TEST", size=100, confidence=0.7)

        assert signal.signal_type == SignalType.BUY_NO
        assert signal.market_id == "TEST"
        assert signal.confidence == 0.7

    def test_hold_signal(self):
        """Test generating HOLD signal."""
        strategy = ConcreteStrategy()

        signal = strategy.hold(ticker="TEST")

        assert signal.signal_type == SignalType.HOLD
        assert signal.market_id == "TEST"
        assert signal.recommended_size == 0
        assert signal.confidence == 0.0

    def test_close_signal(self):
        """Test generating CLOSE signal."""
        strategy = ConcreteStrategy()

        signal = strategy.close(ticker="TEST", reason="stop_loss")

        assert signal.signal_type == SignalType.CLOSE
        assert signal.market_id == "TEST"
        assert signal.metadata["reason"] == "stop_loss"

    def test_should_close_position_stop_loss(self):
        """Test should close position on stop loss."""
        strategy = ConcreteStrategy(stop_loss=0.2)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.3,  # 40% loss
            entry_time=datetime.now(),
        )

        assert strategy.should_close_position(position) is True

    def test_should_close_position_take_profit(self):
        """Test should close position on take profit."""
        strategy = ConcreteStrategy(take_profit=0.5)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.8,  # 60% profit
            entry_time=datetime.now(),
        )

        assert strategy.should_close_position(position) is True

    def test_should_close_position_no_triggers(self):
        """Test should not close position when no triggers hit."""
        strategy = ConcreteStrategy(stop_loss=0.5, take_profit=1.0)

        position = Position(
            ticker="TEST",
            side="yes",
            size=100,
            entry_price=0.5,
            current_price=0.55,  # Small profit
            entry_time=datetime.now(),
        )

        assert strategy.should_close_position(position) is False

    def test_kelly_size_calculation(self):
        """Test Kelly size calculation."""
        strategy = ConcreteStrategy(initial_capital=1000.0, kelly_fraction=0.25)

        size = strategy.kelly_size(edge=0.1, odds=2.0)
        assert size > 0

    def test_kelly_size_negative_edge(self):
        """Test Kelly size with negative edge."""
        strategy = ConcreteStrategy()

        size = strategy.kelly_size(edge=-0.05, odds=2.0)
        assert size == 0

    def test_update_capital(self):
        """Test capital update."""
        strategy = ConcreteStrategy(initial_capital=1000.0)

        strategy.update_capital(100.0)
        assert strategy.current_capital == 1100.0

        strategy.update_capital(-50.0)
        assert strategy.current_capital == 1050.0

    def test_set_espn_data(self):
        """Test setting ESPN data."""
        strategy = ConcreteStrategy()
        espn_data = {"momentum": 0.5}

        strategy.set_espn_data(espn_data)

        assert strategy.espn_data == espn_data
        assert strategy.use_espn is True

    def test_set_sportsbook_consensus(self):
        """Test setting sportsbook data."""
        strategy = ConcreteStrategy()
        sportsbook_data = {"TEAM-A": 0.6}

        strategy.set_sportsbook_consensus(sportsbook_data)

        assert strategy.sportsbook_data == sportsbook_data

    def test_get_sportsbook_consensus(self):
        """Test getting sportsbook consensus."""
        strategy = ConcreteStrategy()
        strategy.sportsbook_data = {"TEAM-A": 0.6}

        consensus = strategy.get_sportsbook_consensus("TEAM-A")
        assert consensus == 0.6

        consensus = strategy.get_sportsbook_consensus("TEAM-B")
        assert consensus is None

    def test_get_performance_metrics_no_trades(self):
        """Test performance metrics with no trades."""
        strategy = ConcreteStrategy()

        metrics = strategy.get_performance_metrics()
        assert metrics == {}

    def test_get_performance_metrics_with_trades(self):
        """Test performance metrics with trades."""
        strategy = ConcreteStrategy(initial_capital=1000.0)
        strategy.trade_history = [
            {"pnl": 50.0},
            {"pnl": -20.0},
            {"pnl": 30.0},
            {"pnl": 40.0},
        ]
        strategy.current_capital = 1100.0

        metrics = strategy.get_performance_metrics()

        assert metrics["total_trades"] == 4
        assert metrics["win_rate"] == 0.75  # 3 wins out of 4
        assert metrics["total_pnl"] == 100.0
        assert metrics["avg_pnl"] == 25.0
        assert metrics["total_return"] == pytest.approx(10.0, rel=1e-10)  # 10% return
        assert metrics["max_win"] == 50.0
        assert metrics["max_loss"] == -20.0

    def test_reset_strategy(self):
        """Test resetting strategy state."""
        strategy = ConcreteStrategy(initial_capital=1000.0)
        strategy.current_capital = 1500.0
        strategy.positions.append(
            Position(
                ticker="TEST",
                side="yes",
                size=100,
                entry_price=0.5,
                current_price=0.6,
                entry_time=datetime.now(),
            )
        )
        strategy.trade_history.append({"pnl": 50.0})

        strategy.reset()

        assert strategy.current_capital == 1000.0
        assert strategy.positions == []
        assert strategy.closed_positions == []
        assert strategy.signals == []
        assert strategy.trade_history == []

    def test_strategy_str_representation(self):
        """Test string representation."""
        strategy = ConcreteStrategy(name="TestStrat", initial_capital=1000.0)

        str_repr = str(strategy)
        assert "TestStrat" in str_repr
        assert "1000.00" in str_repr


class TestBaseStrategy:
    """Test BaseStrategy class."""

    def test_base_strategy_with_config(self):
        """Test BaseStrategy initialization with config."""
        config = StrategyConfig(
            max_position_size=0.2, min_edge=0.05, use_kelly=True, max_positions=5
        )

        class ConcreteBase(BaseStrategy):
            def analyze(self, market_data, espn_data=None, **kwargs):
                return self.hold()

        strategy = ConcreteBase(name="TestBase", config=config)

        assert strategy.name == "TestBase"
        assert strategy.max_position_size == 0.2
        assert strategy.min_edge == 0.05
        assert strategy.use_kelly is True
        assert strategy.max_positions == 5
        assert strategy.config == config

    def test_base_strategy_default_config(self):
        """Test BaseStrategy with default config."""

        class ConcreteBase(BaseStrategy):
            def analyze(self, market_data, espn_data=None, **kwargs):
                return self.hold()

        strategy = ConcreteBase()

        assert strategy.max_position_size == 0.1
        assert strategy.min_edge == 0.03
        assert strategy.config is not None
