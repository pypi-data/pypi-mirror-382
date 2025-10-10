"""Test neural.trading.websocket module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
from neural.trading.websocket import KalshiWebSocketClient


class TestKalshiWebSocketClient:
    """Test KalshiWebSocketClient functionality."""

    def test_init_default(self):
        """Test WebSocket client initialization with default parameters."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                assert client.path == "/trade-api/ws/v2"
                assert client.ping_interval == 25.0
                assert client.ping_timeout == 10.0
                assert client._connect_timeout == 10.0
                assert client._request_id == 1
                assert client._ws_app is None
                assert client._thread is None
                assert not client._ready.is_set()
                assert not client._closing.is_set()

    def test_init_custom_params(self):
        """Test WebSocket client initialization with custom parameters."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                custom_path = "/custom/ws/path"
                custom_ping = 30.0
                custom_timeout = 15.0

                client = KalshiWebSocketClient(
                    path=custom_path,
                    ping_interval=custom_ping,
                    ping_timeout=custom_timeout,
                    _connect_timeout=custom_timeout,
                )

                assert client.path == custom_path
                assert client.ping_interval == custom_ping
                assert client.ping_timeout == custom_timeout
                assert client._connect_timeout == custom_timeout

    def test_init_with_signer(self):
        """Test WebSocket client initialization with provided signer."""
        mock_signer = Mock()

        client = KalshiWebSocketClient(signer=mock_signer)
        assert client.signer == mock_signer

    def test_init_with_credentials(self):
        """Test WebSocket client initialization with credentials."""
        api_key = "custom_key"
        private_key = b"custom_private_key"

        with patch("neural.trading.websocket.KalshiSigner") as mock_signer_class:
            client = KalshiWebSocketClient(api_key_id=api_key, private_key_pem=private_key)

            mock_signer_class.assert_called_once_with(api_key, private_key)

    def test_get_next_request_id(self):
        """Test getting next request ID."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()

                initial_id = client._request_id
                next_id = client._get_next_request_id()

                assert next_id == initial_id + 1
                assert client._request_id == next_id

    def test_build_url_default(self):
        """Test building URL with default base URL."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                with patch(
                    "neural.trading.websocket.get_base_url",
                    return_value="https://api.elections.kalshi.com",
                ):
                    client = KalshiWebSocketClient()
                    url = client._build_url()

                    assert url == "wss://api.elections.kalshi.com/trade-api/ws/v2"

    def test_build_url_custom_env(self):
        """Test building URL with custom environment."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient(env="demo")
                url = client._build_url()

                assert url == "wss://demo.elections.kalshi.com/trade-api/ws/v2"

    def test_build_url_custom_url(self):
        """Test building URL with custom URL."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                custom_url = "https://custom.kalshi.com"
                client = KalshiWebSocketClient(url=custom_url)
                url = client._build_url()

                assert url == "wss://custom.kalshi.com/trade-api/ws/v2"

    def test_on_ws_open(self):
        """Test WebSocket open handler."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                mock_ws = Mock()

                client._on_ws_open(mock_ws)

                assert client._ready.is_set()

    def test_on_ws_message_json(self):
        """Test WebSocket message handler with JSON message."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                on_message_mock = Mock()
                client = KalshiWebSocketClient(on_message=on_message_mock)

                test_message = '{"type": "test", "data": "value"}'
                mock_ws = Mock()

                client._on_ws_message(mock_ws, test_message)

                on_message_mock.assert_called_once_with({"type": "test", "data": "value"})

    def test_on_ws_message_invalid_json(self):
        """Test WebSocket message handler with invalid JSON."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()

                invalid_message = "invalid json"
                mock_ws = Mock()

                # Should not raise exception
                client._on_ws_message(mock_ws, invalid_message)

    def test_on_ws_error(self):
        """Test WebSocket error handler."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                mock_ws = Mock()
                error = Exception("Test error")

                # Should not raise exception
                client._on_ws_error(mock_ws, error)

    def test_on_ws_close(self):
        """Test WebSocket close handler."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                mock_ws = Mock()

                client._on_ws_close(mock_ws, 1000, "Normal closure")

                assert client._closing.is_set()

    def test_is_connected_false(self):
        """Test connection status when not connected."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                assert not client.is_connected()

    def test_is_connected_true(self):
        """Test connection status when connected."""
        with patch("neural.trading.websocket.get_api_key_id", return_value="test_key"):
            with patch(
                "neural.trading.websocket.get_private_key_material", return_value=b"test_key"
            ):
                client = KalshiWebSocketClient()
                mock_ws = Mock()
                client._ws_app = mock_ws
                client._ready.set()

                assert client.is_connected()
