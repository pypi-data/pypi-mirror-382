"""Test neural.auth.http_client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from neural.auth.http_client import KalshiHTTPClient


class TestKalshiHTTPClient:
    """Test KalshiHTTPClient class."""

    @patch("neural.auth.http_client.KalshiSigner")
    def test_init_with_credentials(self, mock_signer):
        """Test initialization with provided credentials."""
        client = KalshiHTTPClient(api_key_id="custom_key", private_key_pem=b"custom_key")
        assert client.api_key_id == "custom_key"
        assert client.private_key_pem == b"custom_key"
        assert client.base_url == "https://api.elections.kalshi.com"
        mock_signer.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_init_without_credentials(self, mock_signer):
        """Test initialization without credentials (uses env)."""
        client = KalshiHTTPClient()
        assert client.api_key_id == "test_api_key_id"
        assert isinstance(client.private_key_pem, bytes)
        assert client.base_url == "https://api.elections.kalshi.com"
        mock_signer.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_init_with_custom_base_url(self, mock_signer):
        """Test initialization with custom base URL."""
        client = KalshiHTTPClient(base_url="https://custom.kalshi.com")
        assert client.base_url == "https://custom.kalshi.com"
        mock_signer.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_get_success(self, mock_signer):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        client = KalshiHTTPClient()
        client.session.request = Mock(return_value=mock_response)

        result = client.get("/test")

        assert result == {"data": "test"}
        client.session.request.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_get_with_params(self, mock_signer):
        """Test successful GET request with params."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        client = KalshiHTTPClient()
        client.session.request = Mock(return_value=mock_response)

        result = client.get("/test", params={"key": "value"})

        assert result == {"data": "test"}
        client.session.request.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_post_success(self, mock_signer):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "created"}
        mock_response.raise_for_status.return_value = None

        client = KalshiHTTPClient()
        client.session.request = Mock(return_value=mock_response)

        result = client.post("/test", json_data={"key": "value"})

        assert result == {"data": "created"}
        client.session.request.assert_called_once()

    @patch("neural.auth.http_client.KalshiSigner")
    def test_get_http_error(self, mock_signer):
        """Test GET request with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_response.text = "404 page not found"

        client = KalshiHTTPClient()
        client.session.request = Mock(return_value=mock_response)

        with pytest.raises(requests.HTTPError):
            client.get("/notfound")

    @patch("neural.auth.http_client.KalshiSigner")
    def test_close(self, mock_signer):
        """Test closing the HTTP client."""
        client = KalshiHTTPClient()
        client.close()
        # Should not raise any exceptions
