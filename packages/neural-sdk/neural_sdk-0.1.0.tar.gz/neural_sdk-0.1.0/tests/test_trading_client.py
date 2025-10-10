"""Test TradingClient implementation and error handling."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from neural.trading.client import TradingClient, _ServiceProxy


class TestTradingClient:
    """Test TradingClient class."""

    @patch("neural.trading.client._default_client_factory")
    def test_init_default(self, mock_factory):
        """Test TradingClient initialization with default parameters."""
        mock_client = Mock()
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()

        assert client._client is mock_client
        assert isinstance(client.portfolio, _ServiceProxy)
        assert isinstance(client.markets, _ServiceProxy)
        assert isinstance(client.exchange, _ServiceProxy)

    @patch("neural.trading.client._default_client_factory")
    def test_init_with_credentials(self, mock_factory):
        """Test TradingClient initialization with provided credentials."""
        mock_client = Mock()
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient(
            api_key_id="test_key",
            private_key_pem=b"test_key_data",
            env="production",  # Use production instead of demo to avoid error
        )

        mock_factory.assert_called_once_with(
            base_url="https://api.elections.kalshi.com",
            api_key_id="test_key",
            private_key_pem=b"test_key_data",
            timeout=15,
        )
        assert client._client is mock_client

    @patch("neural.trading.client._default_client_factory")
    def test_get_balance_success(self, mock_factory):
        """Test successful balance retrieval through portfolio API."""
        mock_client = Mock()
        mock_balance_response = Mock()
        mock_balance_response.model_dump.return_value = {"balance": "1000.00", "currency": "USD"}
        mock_client.portfolio.get_balance.return_value = mock_balance_response
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.portfolio.get_balance()

        assert result == {"balance": "1000.00", "currency": "USD"}
        mock_client.portfolio.get_balance.assert_called_once()

    @patch("neural.trading.client._default_client_factory")
    def test_get_balance_missing_key(self, mock_factory):
        """Test balance retrieval when response is missing expected data."""
        mock_client = Mock()
        mock_balance_response = Mock()
        mock_balance_response.model_dump.return_value = {"other_data": "value"}
        mock_client.portfolio.get_balance.return_value = mock_balance_response
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.portfolio.get_balance()

        assert result == {"other_data": "value"}

    @patch("neural.trading.client._default_client_factory")
    def test_place_order_success(self, mock_factory):
        """Test successful order placement through exchange API."""
        mock_client = Mock()
        mock_order_response = Mock()
        mock_order_response.model_dump.return_value = {"order_id": "order_123", "status": "filled"}
        mock_client.exchange.create_order.return_value = mock_order_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.create_order(ticker="EVENT-YES", side="buy", count=10, price=75)

        assert result == {"order_id": "order_123", "status": "filled"}
        mock_client.exchange.create_order.assert_called_once_with(
            ticker="EVENT-YES", side="buy", count=10, price=75
        )

    @patch("neural.trading.client._default_client_factory")
    def test_place_order_with_type(self, mock_factory):
        """Test order placement with order type parameter."""
        mock_client = Mock()
        mock_order_response = Mock()
        mock_order_response.model_dump.return_value = {"order_id": "order_456", "status": "pending"}
        mock_client.exchange.create_order.return_value = mock_order_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.create_order(
            ticker="EVENT-NO", side="sell", count=5, price=25, type="limit"
        )

        assert result == {"order_id": "order_456", "status": "pending"}
        mock_client.exchange.create_order.assert_called_once_with(
            ticker="EVENT-NO", side="sell", count=5, price=25, type="limit"
        )

    @patch("neural.trading.client._default_client_factory")
    def test_get_order_success(self, mock_factory):
        """Test successful order retrieval through exchange API."""
        mock_client = Mock()
        mock_order_response = Mock()
        mock_order_response.model_dump.return_value = {
            "order_id": "order_789",
            "status": "filled",
            "price": 80,
        }
        mock_client.exchange.get_order.return_value = mock_order_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.get_order("order_789")

        assert result == {"order_id": "order_789", "status": "filled", "price": 80}
        mock_client.exchange.get_order.assert_called_once_with("order_789")

    @patch("neural.trading.client._default_client_factory")
    def test_get_order_missing_order(self, mock_factory):
        """Test order retrieval when order is not found."""
        mock_client = Mock()
        mock_order_response = Mock()
        mock_order_response.model_dump.return_value = {"error": "Order not found"}
        mock_client.exchange.get_order.return_value = mock_order_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.get_order("nonexistent_order")

        assert result == {"error": "Order not found"}

    @patch("neural.trading.client._default_client_factory")
    def test_cancel_order_success(self, mock_factory):
        """Test successful order cancellation through exchange API."""
        mock_client = Mock()
        mock_cancel_response = Mock()
        mock_cancel_response.model_dump.return_value = {
            "order_id": "order_123",
            "status": "cancelled",
        }
        mock_client.exchange.cancel_order.return_value = mock_cancel_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.cancel_order("order_123")

        assert result == {"order_id": "order_123", "status": "cancelled"}
        mock_client.exchange.cancel_order.assert_called_once_with("order_123")

    @patch("neural.trading.client._default_client_factory")
    def test_cancel_order_missing_response(self, mock_factory):
        """Test order cancellation when response is incomplete."""
        mock_client = Mock()
        mock_cancel_response = Mock()
        mock_cancel_response.model_dump.return_value = {"status": "cancelled"}
        mock_client.exchange.cancel_order.return_value = mock_cancel_response
        mock_client.portfolio = Mock()
        mock_client.markets = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.exchange.cancel_order("order_456")

        assert result == {"status": "cancelled"}

    @patch("neural.trading.client._default_client_factory")
    def test_get_positions_success(self, mock_factory):
        """Test successful positions retrieval through portfolio API."""
        mock_client = Mock()
        mock_positions_response = Mock()
        mock_positions_response.model_dump.return_value = {
            "positions": [
                {"ticker": "EVENT-YES", "count": 10, "side": "buy"},
                {"ticker": "EVENT-NO", "count": 5, "side": "sell"},
            ]
        }
        mock_client.portfolio.get_positions.return_value = mock_positions_response
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.portfolio.get_positions()

        assert result == {
            "positions": [
                {"ticker": "EVENT-YES", "count": 10, "side": "buy"},
                {"ticker": "EVENT-NO", "count": 5, "side": "sell"},
            ]
        }
        mock_client.portfolio.get_positions.assert_called_once()

    @patch("neural.trading.client._default_client_factory")
    def test_get_positions_empty(self, mock_factory):
        """Test positions retrieval when no positions exist."""
        mock_client = Mock()
        mock_positions_response = Mock()
        mock_positions_response.model_dump.return_value = {"positions": []}
        mock_client.portfolio.get_positions.return_value = mock_positions_response
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.portfolio.get_positions()

        assert result == {"positions": []}

    @patch("neural.trading.client._default_client_factory")
    def test_get_positions_missing_key(self, mock_factory):
        """Test positions retrieval when response structure is unexpected."""
        mock_client = Mock()
        mock_positions_response = Mock()
        mock_positions_response.model_dump.return_value = {"data": "other"}
        mock_client.portfolio.get_positions.return_value = mock_positions_response
        mock_client.markets = Mock()
        mock_client.exchange = Mock()
        mock_factory.return_value = mock_client

        client = TradingClient()
        result = client.portfolio.get_positions()

        assert result == {"data": "other"}
