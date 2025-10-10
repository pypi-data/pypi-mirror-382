"""Test neural.analysis.risk.position_sizing module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from neural.analysis.risk.position_sizing import (
    kelly_criterion,
    fixed_percentage,
    edge_proportional,
    martingale,
    anti_martingale,
    volatility_adjusted,
    confidence_weighted,
    optimal_f,
    risk_parity,
    PositionSizer,
)


class TestKellyCriterion:
    """Test Kelly Criterion position sizing."""

    def test_kelly_positive_edge(self):
        """Test Kelly with positive edge."""
        size = kelly_criterion(edge=0.1, odds=2.0, kelly_fraction=1.0, max_position=1.0)

        assert size > 0
        assert size <= 1.0

    def test_kelly_negative_edge(self):
        """Test Kelly with negative edge returns zero."""
        size = kelly_criterion(edge=-0.05, odds=2.0)

        assert size == 0.0

    def test_kelly_zero_edge(self):
        """Test Kelly with zero edge returns zero."""
        size = kelly_criterion(edge=0.0, odds=2.0)

        assert size == 0.0

    def test_kelly_with_fraction(self):
        """Test Kelly with safety fraction."""
        full_size = kelly_criterion(edge=0.1, odds=2.0, kelly_fraction=1.0, max_position=1.0)
        half_size = kelly_criterion(edge=0.1, odds=2.0, kelly_fraction=0.5, max_position=1.0)

        assert half_size < full_size
        assert half_size == pytest.approx(full_size * 0.5, rel=0.1)

    def test_kelly_max_position_limit(self):
        """Test Kelly respects max position limit."""
        size = kelly_criterion(edge=0.5, odds=10.0, kelly_fraction=1.0, max_position=0.2)

        assert size <= 0.2

    def test_kelly_negative_odds(self):
        """Test Kelly with negative odds returns zero."""
        size = kelly_criterion(edge=0.1, odds=-1.0)

        assert size == 0.0


class TestFixedPercentage:
    """Test fixed percentage position sizing."""

    def test_fixed_percentage_basic(self):
        """Test basic fixed percentage calculation."""
        contracts = fixed_percentage(capital=10000, percentage=0.02)

        assert contracts == 200  # 2% of 10000

    def test_fixed_percentage_minimum(self):
        """Test minimum contracts enforcement."""
        contracts = fixed_percentage(capital=100, percentage=0.02, min_contracts=10)

        assert contracts >= 10

    def test_fixed_percentage_maximum(self):
        """Test maximum contracts enforcement."""
        contracts = fixed_percentage(
            capital=10000, percentage=0.1, min_contracts=10, max_contracts=500
        )

        assert contracts <= 500

    def test_fixed_percentage_custom_params(self):
        """Test with custom parameters."""
        contracts = fixed_percentage(capital=5000, percentage=0.05, min_contracts=25)

        assert contracts == 250  # 5% of 5000


class TestEdgeProportional:
    """Test edge proportional position sizing."""

    def test_edge_proportional_basic(self):
        """Test basic edge proportional sizing."""
        contracts = edge_proportional(edge=0.05, capital=10000, min_edge=0.02)

        assert contracts > 0

    def test_edge_proportional_insufficient_edge(self):
        """Test returns zero when edge below minimum."""
        contracts = edge_proportional(edge=0.01, capital=10000, min_edge=0.02)

        assert contracts == 0

    def test_edge_proportional_scales_with_edge(self):
        """Test position scales with edge strength."""
        small_edge = edge_proportional(edge=0.03, capital=10000, min_edge=0.02)
        large_edge = edge_proportional(edge=0.1, capital=10000, min_edge=0.02)

        assert large_edge > small_edge

    def test_edge_proportional_max_cap(self):
        """Test maximum percentage cap."""
        contracts = edge_proportional(edge=0.5, capital=10000, min_edge=0.02, max_percentage=0.1)

        assert contracts <= 1000  # Max 10% of 10000


class TestMartingale:
    """Test martingale position sizing."""

    def test_martingale_no_losses(self):
        """Test martingale with no losses."""
        contracts = martingale(capital=10000, consecutive_losses=0, base_size=0.01)

        assert contracts == 100  # 1% of 10000

    def test_martingale_one_loss(self):
        """Test martingale after one loss."""
        contracts = martingale(capital=10000, consecutive_losses=1, base_size=0.01, multiplier=2.0)

        assert contracts == 200  # 2% of 10000

    def test_martingale_multiple_losses(self):
        """Test martingale after multiple losses."""
        contracts = martingale(capital=10000, consecutive_losses=3, base_size=0.01, multiplier=2.0)

        assert contracts == 800  # 8% of 10000 (2^3)

    def test_martingale_max_cap(self):
        """Test martingale maximum size cap."""
        contracts = martingale(
            capital=10000,
            consecutive_losses=10,
            base_size=0.01,
            multiplier=2.0,
            max_size=0.16,
        )

        assert contracts <= 1600  # Max 16% of 10000


class TestAntiMartingale:
    """Test anti-martingale position sizing."""

    def test_anti_martingale_no_wins(self):
        """Test anti-martingale with no wins."""
        contracts = anti_martingale(capital=10000, consecutive_wins=0, base_size=0.01)

        assert contracts == 100  # 1% of 10000

    def test_anti_martingale_one_win(self):
        """Test anti-martingale after one win."""
        contracts = anti_martingale(
            capital=10000, consecutive_wins=1, base_size=0.01, multiplier=1.5
        )

        assert contracts == 150  # 1.5% of 10000

    def test_anti_martingale_multiple_wins(self):
        """Test anti-martingale after multiple wins."""
        contracts = anti_martingale(
            capital=10000, consecutive_wins=2, base_size=0.01, multiplier=1.5
        )

        assert contracts == 225  # 2.25% of 10000 (1.5^2)

    def test_anti_martingale_max_cap(self):
        """Test anti-martingale maximum size cap."""
        contracts = anti_martingale(
            capital=10000,
            consecutive_wins=10,
            base_size=0.01,
            multiplier=1.5,
            max_size=0.1,
        )

        assert contracts <= 1000  # Max 10% of 10000


class TestVolatilityAdjusted:
    """Test volatility adjusted position sizing."""

    def test_volatility_adjusted_low_vol(self):
        """Test larger positions in low volatility."""
        contracts = volatility_adjusted(
            capital=10000, current_volatility=0.1, target_volatility=0.15
        )

        assert contracts > 200  # More than 2% base

    def test_volatility_adjusted_high_vol(self):
        """Test smaller positions in high volatility."""
        contracts = volatility_adjusted(
            capital=10000, current_volatility=0.3, target_volatility=0.15
        )

        assert contracts < 200  # Less than 2% base

    def test_volatility_adjusted_zero_vol(self):
        """Test returns zero for zero volatility."""
        contracts = volatility_adjusted(
            capital=10000, current_volatility=0.0, target_volatility=0.15
        )

        assert contracts == 0

    def test_volatility_adjusted_min_max(self):
        """Test min and max bounds."""
        contracts = volatility_adjusted(
            capital=10000,
            current_volatility=0.5,
            target_volatility=0.15,
            min_size=0.01,
            max_size=0.05,
        )

        assert 100 <= contracts <= 500  # Between 1% and 5%


class TestConfidenceWeighted:
    """Test confidence weighted position sizing."""

    def test_confidence_weighted_high_confidence(self):
        """Test larger position with high confidence."""
        contracts = confidence_weighted(capital=10000, confidence=0.9, max_size=0.1)

        assert contracts > 0
        assert contracts <= 1000  # Max 10%

    def test_confidence_weighted_low_confidence(self):
        """Test returns zero below minimum confidence."""
        contracts = confidence_weighted(capital=10000, confidence=0.3, min_confidence=0.5)

        assert contracts == 0

    def test_confidence_weighted_scaling(self):
        """Test position scales with confidence."""
        low_conf = confidence_weighted(capital=10000, confidence=0.6, min_confidence=0.5)
        high_conf = confidence_weighted(capital=10000, confidence=0.9, min_confidence=0.5)

        assert high_conf > low_conf

    def test_confidence_weighted_power_factor(self):
        """Test confidence power scaling."""
        linear = confidence_weighted(capital=10000, confidence=0.7, confidence_power=1.0)
        exponential = confidence_weighted(capital=10000, confidence=0.7, confidence_power=2.0)

        assert linear > exponential  # Exponential is more conservative


class TestOptimalF:
    """Test optimal F position sizing."""

    def test_optimal_f_positive_expectancy(self):
        """Test optimal F with positive expectancy."""
        contracts = optimal_f(
            capital=10000, win_rate=0.6, avg_win=100, avg_loss=80, safety_factor=0.5
        )

        assert contracts > 0

    def test_optimal_f_negative_expectancy(self):
        """Test optimal F with negative expectancy."""
        contracts = optimal_f(
            capital=10000, win_rate=0.4, avg_win=80, avg_loss=100, safety_factor=0.5
        )

        assert contracts >= 0  # Should be zero or very small

    def test_optimal_f_invalid_win_rate(self):
        """Test returns zero for invalid win rate."""
        contracts = optimal_f(capital=10000, win_rate=1.5, avg_win=100, avg_loss=80)  # Invalid

        assert contracts == 0

    def test_optimal_f_zero_loss(self):
        """Test returns zero when avg loss is zero."""
        contracts = optimal_f(capital=10000, win_rate=0.6, avg_win=100, avg_loss=0)

        assert contracts == 0

    def test_optimal_f_safety_factor(self):
        """Test safety factor reduces position size."""
        full = optimal_f(capital=10000, win_rate=0.6, avg_win=100, avg_loss=80, safety_factor=1.0)
        half = optimal_f(capital=10000, win_rate=0.6, avg_win=100, avg_loss=80, safety_factor=0.5)

        assert half < full


class TestRiskParity:
    """Test risk parity position sizing."""

    def test_risk_parity_basic(self):
        """Test basic risk parity allocation."""
        positions = {
            "TICKER-A": {"volatility": 0.2, "price": 0.5},
            "TICKER-B": {"volatility": 0.3, "price": 0.6},
        }

        sizes = risk_parity(capital=10000, positions=positions, target_risk=0.02)

        assert "TICKER-A" in sizes
        assert "TICKER-B" in sizes
        assert all(size > 0 for size in sizes.values())

    def test_risk_parity_inverse_volatility(self):
        """Test higher allocation to lower volatility positions."""
        positions = {
            "LOW-VOL": {"volatility": 0.1, "price": 0.5},
            "HIGH-VOL": {"volatility": 0.3, "price": 0.5},
        }

        sizes = risk_parity(capital=10000, positions=positions)

        # Low volatility should get larger allocation
        assert sizes["LOW-VOL"] > sizes["HIGH-VOL"]

    def test_risk_parity_empty_positions(self):
        """Test returns empty dict for empty positions."""
        sizes = risk_parity(capital=10000, positions={})

        assert sizes == {}

    def test_risk_parity_single_position(self):
        """Test with single position."""
        positions = {"TICKER-A": {"volatility": 0.2, "price": 0.5}}

        sizes = risk_parity(capital=10000, positions=positions)

        assert "TICKER-A" in sizes
        assert sizes["TICKER-A"] > 0


class TestPositionSizer:
    """Test PositionSizer class."""

    def test_position_sizer_initialization(self):
        """Test sizer initialization."""
        sizer = PositionSizer(initial_capital=10000, default_method="kelly")

        assert sizer.initial_capital == 10000
        assert sizer.current_capital == 10000
        assert sizer.default_method == "kelly"
        assert sizer.consecutive_wins == 0
        assert sizer.consecutive_losses == 0

    def test_calculate_size_kelly(self):
        """Test size calculation with Kelly method."""
        sizer = PositionSizer(initial_capital=10000, default_method="kelly")

        size = sizer.calculate_size(edge=0.05, odds=2.0, kelly_fraction=0.25)

        assert size > 0

    def test_calculate_size_fixed(self):
        """Test size calculation with fixed method."""
        sizer = PositionSizer(initial_capital=10000, default_method="fixed")

        size = sizer.calculate_size(method="fixed", percentage=0.02)

        assert size == 200

    def test_calculate_size_edge(self):
        """Test size calculation with edge proportional method."""
        sizer = PositionSizer(initial_capital=10000, default_method="edge")

        size = sizer.calculate_size(method="edge", edge=0.05, min_edge=0.02)

        assert size > 0

    def test_calculate_size_martingale(self):
        """Test size calculation with martingale method."""
        sizer = PositionSizer(initial_capital=10000)
        sizer.consecutive_losses = 2

        size = sizer.calculate_size(method="martingale", base_size=0.01)

        assert size > 0

    def test_calculate_size_anti_martingale(self):
        """Test size calculation with anti-martingale method."""
        sizer = PositionSizer(initial_capital=10000)
        sizer.consecutive_wins = 2

        size = sizer.calculate_size(method="anti_martingale", base_size=0.01)

        assert size > 0

    def test_calculate_size_volatility(self):
        """Test size calculation with volatility method."""
        sizer = PositionSizer(initial_capital=10000)

        size = sizer.calculate_size(
            method="volatility", current_volatility=0.2, target_volatility=0.15
        )

        assert size > 0

    def test_calculate_size_confidence(self):
        """Test size calculation with confidence method."""
        sizer = PositionSizer(initial_capital=10000)

        size = sizer.calculate_size(method="confidence", confidence=0.8)

        assert size > 0

    def test_calculate_size_optimal_f_no_trades(self):
        """Test optimal F falls back to fixed when no trades."""
        sizer = PositionSizer(initial_capital=10000)

        size = sizer.calculate_size(method="optimal_f", percentage=0.02)

        # Should fall back to fixed percentage
        assert size > 0

    def test_calculate_size_optimal_f_with_history(self):
        """Test optimal F with trade history."""
        sizer = PositionSizer(initial_capital=10000)
        sizer.total_trades = 10
        sizer.winning_trades = 6
        sizer.total_profit = 600
        sizer.total_loss = 320

        size = sizer.calculate_size(method="optimal_f")

        assert size > 0

    def test_calculate_size_invalid_method(self):
        """Test raises error for invalid method."""
        sizer = PositionSizer(initial_capital=10000)

        with pytest.raises(ValueError, match="Unknown sizing method"):
            sizer.calculate_size(method="invalid_method")

    def test_update_performance_win(self):
        """Test performance update after win."""
        sizer = PositionSizer(initial_capital=10000)

        sizer.update_performance(pnl=100)

        assert sizer.current_capital == 10100
        assert sizer.total_trades == 1
        assert sizer.winning_trades == 1
        assert sizer.consecutive_wins == 1
        assert sizer.consecutive_losses == 0
        assert sizer.total_profit == 100

    def test_update_performance_loss(self):
        """Test performance update after loss."""
        sizer = PositionSizer(initial_capital=10000)

        sizer.update_performance(pnl=-50)

        assert sizer.current_capital == 9950
        assert sizer.total_trades == 1
        assert sizer.winning_trades == 0
        assert sizer.consecutive_wins == 0
        assert sizer.consecutive_losses == 1
        assert sizer.total_loss == 50

    def test_update_performance_streak(self):
        """Test consecutive win/loss tracking."""
        sizer = PositionSizer(initial_capital=10000)

        sizer.update_performance(100)
        sizer.update_performance(50)
        sizer.update_performance(75)

        assert sizer.consecutive_wins == 3

        sizer.update_performance(-30)

        assert sizer.consecutive_wins == 0
        assert sizer.consecutive_losses == 1

    def test_get_stats(self):
        """Test getting performance statistics."""
        sizer = PositionSizer(initial_capital=10000)

        sizer.update_performance(100)
        sizer.update_performance(-50)
        sizer.update_performance(150)

        stats = sizer.get_stats()

        assert stats["current_capital"] == 10200
        assert stats["total_return"] == pytest.approx(2.0, rel=1e-10)  # 2% return
        assert stats["total_trades"] == 3
        assert stats["win_rate"] == pytest.approx(2 / 3, rel=0.01)
        assert stats["consecutive_wins"] == 1
        assert stats["consecutive_losses"] == 0
        assert stats["avg_win"] == 125.0  # (100 + 150) / 2
        assert stats["avg_loss"] == 50.0

    def test_calculate_size_uses_default_method(self):
        """Test calculate_size uses default method when not specified."""
        sizer = PositionSizer(initial_capital=10000, default_method="fixed")

        size = sizer.calculate_size(percentage=0.03)

        assert size == 300  # 3% of 10000

    def test_capital_updates_affect_sizing(self):
        """Test that capital updates affect subsequent sizing."""
        sizer = PositionSizer(initial_capital=10000, default_method="fixed")

        initial_size = sizer.calculate_size(percentage=0.1)
        assert initial_size == 1000

        sizer.update_performance(1000)  # Increase capital

        new_size = sizer.calculate_size(percentage=0.1)
        assert new_size == 1100  # 10% of 11000
