"""Test neural.trading.paper_client module."""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from neural.trading.paper_client import PaperTradingClient, PaperOrder


class TestPaperOrder:
    """Test PaperOrder dataclass."""

    def test_paper_order_creation(self):
        """Test creating a paper order."""
        order = PaperOrder(
            order_id="TEST001",
            market_id="TESTMARKET",
            symbol="TESTMARKET_yes",
            market_name="Test Market",
            side="yes",
            action="buy",
            quantity=100,
            order_type="market",
        )

        assert order.order_id == "TEST001"
        assert order.market_id == "TESTMARKET"
        assert order.side == "yes"
        assert order.action == "buy"
        assert order.quantity == 100
        assert order.status == "pending"

    def test_paper_order_with_price(self):
        """Test paper order with limit price."""
        order = PaperOrder(
            order_id="TEST002",
            market_id="TESTMARKET",
            symbol="TESTMARKET_no",
            market_name="Test Market",
            side="no",
            action="sell",
            quantity=50,
            order_type="limit",
            price=0.65,
        )

        assert order.price == 0.65
        assert order.order_type == "limit"


class TestPaperTradingClient:
    """Test PaperTradingClient class."""

    def test_initialization_defaults(self, tmp_path):
        """Test client initialization with default values."""
        client = PaperTradingClient(data_dir=str(tmp_path / "paper_data"))

        assert client.portfolio.cash == 10000.0
        assert client.portfolio.commission_per_trade == 0.50
        assert client.save_trades is True
        assert client.order_counter == 0
        assert client.pending_orders == {}

    def test_initialization_custom_params(self, tmp_path):
        """Test client initialization with custom parameters."""
        client = PaperTradingClient(
            initial_capital=5000.0,
            commission_per_trade=0.25,
            slippage_pct=0.001,
            save_trades=False,
            data_dir=str(tmp_path / "custom_data"),
        )

        assert client.portfolio.cash == 5000.0
        assert client.portfolio.commission_per_trade == 0.25
        assert client.save_trades is False

    def test_generate_order_id(self, tmp_path):
        """Test order ID generation."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        order_id1 = client._generate_order_id()
        order_id2 = client._generate_order_id()

        assert order_id1.startswith("PAPER_")
        assert order_id2.startswith("PAPER_")
        assert order_id1 != order_id2
        assert client.order_counter == 2

    def test_get_market_price_cached(self, tmp_path):
        """Test getting cached market price."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.market_prices["TEST_yes"] = 0.65

        price = client._get_market_price("TEST", "yes")

        assert price == 0.65

    def test_get_market_price_default(self, tmp_path):
        """Test getting default market price."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        price = client._get_market_price("NEW_MARKET", "yes")

        assert price == 0.50  # Default price

    def test_update_market_price(self, tmp_path):
        """Test updating market price."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        client.update_market_price("TEST", "yes", 0.72)

        assert client.market_prices["TEST_yes"] == 0.72

    def test_update_market_prices_bulk(self, tmp_path):
        """Test bulk market price update."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        price_updates = {"MARKET1": {"yes": 0.6, "no": 0.4}, "MARKET2": {"yes": 0.55, "no": 0.45}}

        client.update_market_prices(price_updates)

        assert client.market_prices["MARKET1_yes"] == 0.6
        assert client.market_prices["MARKET1_no"] == 0.4
        assert client.market_prices["MARKET2_yes"] == 0.55
        assert client.market_prices["MARKET2_no"] == 0.45

    @pytest.mark.asyncio
    async def test_place_order_market_buy(self, tmp_path):
        """Test placing a market buy order."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        result = await client.place_order(
            market_id="TEST",
            side="yes",
            quantity=100,
            order_type="market",
            market_name="Test Market",
        )

        assert result["success"] is True
        assert "order_id" in result
        assert result["filled_price"] > 0
        assert client.portfolio.cash < 10000.0  # Capital was used

    @pytest.mark.asyncio
    async def test_place_order_insufficient_capital(self, tmp_path):
        """Test placing order with insufficient capital."""
        client = PaperTradingClient(initial_capital=100.0, data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.50)

        result = await client.place_order(
            market_id="TEST",
            side="yes",
            quantity=1000,
            order_type="market",  # Need $500
        )

        assert result["success"] == "error"
        assert "insufficient" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_place_order_limit(self, tmp_path):
        """Test placing a limit order."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        result = await client.place_order(
            market_id="TEST",
            side="yes",
            quantity=100,
            order_type="limit",
            price=0.60,
            market_name="Test Market",
        )

        assert result["success"] is True
        assert result["status"] == "pending"
        assert "order_id" in result

    @pytest.mark.asyncio
    async def test_place_order_with_metadata(self, tmp_path):
        """Test placing order with metadata."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        result = await client.place_order(
            market_id="TEST",
            side="yes",
            quantity=100,
            order_type="market",
            sentiment_score=0.8,
            confidence=0.9,
            strategy="mean_reversion",
        )

        assert result["success"] == "success"
        # Metadata should be stored in the trade

    @pytest.mark.asyncio
    async def test_cancel_order(self, tmp_path):
        """Test canceling an order."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        # Place a limit order first
        result = await client.place_order(
            market_id="TEST", side="yes", quantity=100, order_type="limit", price=0.60
        )
        order_id = result["order_id"]

        # Cancel it
        cancel_result = await client.cancel_order(order_id)

        assert cancel_result["success"] == "success"
        assert "cancelled" in cancel_result["message"].lower()

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self, tmp_path):
        """Test canceling non-existent order."""
        client = PaperTradingClient(data_dir=str(tmp_path))

        result = await client.cancel_order("NONEXISTENT")

        assert result["success"] == "error"

    @pytest.mark.asyncio
    async def test_get_order_status(self, tmp_path):
        """Test getting order status."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        # Place order
        result = await client.place_order(market_id="TEST", side="yes", quantity=100)
        order_id = result["order_id"]

        # Get status
        status = await client.get_order_status(order_id)

        assert "status" in status
        assert status["status"] in ["pending", "filled", "cancelled"]

    @pytest.mark.asyncio
    async def test_get_portfolio_value(self, tmp_path):
        """Test getting portfolio value."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))

        value = client.get_portfolio_value()

        assert value["cash"] == 10000.0
        assert value["total_value"] == 10000.0

    @pytest.mark.asyncio
    async def test_get_positions(self, tmp_path):
        """Test getting current positions."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        # Place order to create position
        await client.place_order(market_id="TEST", side="yes", quantity=100)

        # Get positions
        positions = client.get_positions()

        assert len(positions) > 0

    @pytest.mark.asyncio
    async def test_get_trade_history(self, tmp_path):
        """Test getting trade history."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        # Place order
        await client.place_order(market_id="TEST", side="yes", quantity=100)

        # Get history
        history = client.get_trade_history()

        assert len(history) > 0

    @pytest.mark.asyncio
    async def test_close_position(self, tmp_path):
        """Test closing a position."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        # Open position
        await client.place_order(market_id="TEST", side="yes", quantity=100)

        # Update price
        client.update_market_price("TEST", "yes", 0.60)

        # Close position
        result = await client.close_position("TEST_yes")

        assert result["success"] == "success"

    @pytest.mark.asyncio
    async def test_close_all_positions(self, tmp_path):
        """Test closing all positions."""
        client = PaperTradingClient(data_dir=str(tmp_path))
        client.update_market_price("TEST1", "yes", 0.55)
        client.update_market_price("TEST2", "no", 0.45)

        # Open multiple positions
        await client.place_order(market_id="TEST1", side="yes", quantity=100)
        await client.place_order(market_id="TEST2", side="no", quantity=50)

        # Close all
        result = await client.close_all_positions()

        assert result["success"] == "success"
        assert result["positions_closed"] >= 0

    @pytest.mark.asyncio
    async def test_get_performance_summary(self, tmp_path):
        """Test getting performance summary."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))
        client.update_market_price("TEST", "yes", 0.55)

        # Make some trades
        await client.place_order(market_id="TEST", side="yes", quantity=100)
        client.update_market_price("TEST", "yes", 0.60)
        await client.close_position("TEST_yes")

        # Get summary
        summary = await client.get_performance_summary()

        assert "total_trades" in summary
        assert "total_return" in summary
        assert "win_rate" in summary

    def test_save_and_load_state(self, tmp_path):
        """Test saving and loading client state."""
        data_dir = tmp_path / "save_test"
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(data_dir))

        # Make some changes
        client.update_market_price("TEST", "yes", 0.65)
        client.order_counter = 5

        # Save state
        client.save_state()

        # Create new client and load state
        client2 = PaperTradingClient(data_dir=str(data_dir))
        client2.load_state()

        assert client2.order_counter == 5

    def test_reset(self, tmp_path):
        """Test resetting client state."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))

        # Make changes
        client.portfolio.cash = 8000.0
        client.order_counter = 10

        # Reset
        client.reset()

        assert client.portfolio.cash == 10000.0
        assert client.order_counter == 0
        assert len(client.pending_orders) == 0


class TestPaperTradingClientIntegration:
    """Integration tests for paper trading workflow."""

    @pytest.mark.asyncio
    async def test_full_trading_cycle(self, tmp_path):
        """Test complete trading cycle: open, hold, close."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))

        # Set initial price
        client.update_market_price("TEST", "yes", 0.50)

        # Buy
        buy_result = await client.place_order(market_id="TEST", side="yes", quantity=100)
        assert buy_result["success"] == "success"

        initial_capital = client.portfolio.cash
        assert initial_capital < 10000.0  # Money was spent

        # Price goes up
        client.update_market_price("TEST", "yes", 0.60)

        # Sell
        sell_result = await client.close_position("TEST_yes")
        assert sell_result["success"] == "success"

        final_capital = client.portfolio.cash
        assert final_capital > initial_capital  # Made profit

    @pytest.mark.asyncio
    async def test_losing_trade(self, tmp_path):
        """Test a losing trade scenario."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))

        # Set initial price
        client.update_market_price("TEST", "yes", 0.60)

        # Buy
        await client.place_order(market_id="TEST", side="yes", quantity=100)

        # Price goes down
        client.update_market_price("TEST", "yes", 0.40)

        # Sell at loss
        result = await client.close_position("TEST_yes")
        assert result["success"] == "success"

        # Should have less capital
        assert client.portfolio.cash < 10000.0

    @pytest.mark.asyncio
    async def test_multiple_positions(self, tmp_path):
        """Test managing multiple positions."""
        client = PaperTradingClient(initial_capital=10000.0, data_dir=str(tmp_path))

        # Open multiple positions
        client.update_market_price("MARKET1", "yes", 0.50)
        client.update_market_price("MARKET2", "no", 0.45)
        client.update_market_price("MARKET3", "yes", 0.55)

        await client.place_order(market_id="MARKET1", side="yes", quantity=50)
        await client.place_order(market_id="MARKET2", side="no", quantity=75)
        await client.place_order(market_id="MARKET3", side="yes", quantity=100)

        # Get positions
        positions = client.get_positions()
        assert len(positions) >= 3

        # Close all
        result = await client.close_all_positions()
        assert result["success"] == "success"
