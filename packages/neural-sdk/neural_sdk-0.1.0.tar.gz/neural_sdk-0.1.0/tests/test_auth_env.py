"""Test neural.auth.env module."""

import os
import pytest
from unittest.mock import patch, mock_open
from neural.auth.env import get_api_key_id, get_private_key_material, get_base_url


class TestGetAPIKeyId:
    """Test get_api_key_id function."""

    def test_get_api_key_id_from_env(self, monkeypatch):
        """Test getting API key ID from environment variable."""
        monkeypatch.setenv("KALSHI_API_KEY_ID", "test_key_from_env")

        result = get_api_key_id()
        assert result == "test_key_from_env"

    @patch("builtins.open", new_callable=mock_open, read_data="test_api_key_id\n")
    @patch("os.path.exists")
    @patch("os.getcwd")
    def test_get_api_key_id_from_file(self, mock_getcwd, mock_exists, mock_file, monkeypatch):
        """Test getting API key ID from file."""
        monkeypatch.delenv("KALSHI_API_KEY_ID", raising=False)
        mock_exists.return_value = True
        mock_getcwd.return_value = "/mock/project/root"

        result = get_api_key_id()
        assert result == "test_api_key_id"
        # Should open the file regardless of actual path
        assert mock_file.called

    @patch("os.path.exists")
    def test_get_api_key_id_file_not_found(self, mock_exists, monkeypatch):
        """Test FileNotFoundError when file doesn't exist."""
        monkeypatch.delenv("KALSHI_API_KEY_ID", raising=False)
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="Kalshi API key not found"):
            get_api_key_id()


class TestGetPrivateKeyMaterial:
    """Test get_private_key_material function."""

    def test_get_private_key_material_from_base64_env(self, monkeypatch):
        """Test getting private key from base64 environment variable."""
        import base64

        test_key = (
            "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
        )
        test_key_b64 = base64.b64encode(test_key.encode()).decode()
        monkeypatch.setenv("KALSHI_PRIVATE_KEY_BASE64", test_key_b64)

        result = get_private_key_material()
        assert result == test_key.encode()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=b"-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----\n",
    )
    def test_get_private_key_material_from_file(self, mock_file, monkeypatch):
        """Test getting private key from file."""
        monkeypatch.delenv("KALSHI_PRIVATE_KEY_BASE64", raising=False)

        result = get_private_key_material()
        assert isinstance(result, bytes)
        assert b"-----BEGIN RSA PRIVATE KEY-----" in result
        mock_file.assert_called_once_with(
            "/tmp/test_private_key.pem",
            "rb",
        )

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_private_key_material_file_not_found(self, mock_file, monkeypatch):
        """Test FileNotFoundError when file doesn't exist."""
        monkeypatch.delenv("KALSHI_PRIVATE_KEY_BASE64", raising=False)

        with pytest.raises(FileNotFoundError, match="Kalshi private key not found"):
            get_private_key_material()


class TestGetBaseUrl:
    """Test get_base_url function."""

    def test_get_base_url_prod_default(self, monkeypatch):
        """Test getting production URL as default."""
        result = get_base_url()
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_prod_explicit(self, monkeypatch):
        """Test getting production URL explicitly."""
        result = get_base_url("prod")
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_production(self, monkeypatch):
        """Test getting production URL with 'production'."""
        result = get_base_url("production")
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_live(self, monkeypatch):
        """Test getting production URL with 'live'."""
        result = get_base_url("live")
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_empty(self, monkeypatch):
        """Test getting production URL with empty string."""
        result = get_base_url("")
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_from_env(self, monkeypatch):
        """Test getting URL from environment variable."""
        monkeypatch.setenv("KALSHI_ENV", "prod")
        result = get_base_url()
        assert result == "https://api.elections.kalshi.com"

    def test_get_base_url_demo_unsupported(self, monkeypatch):
        """Test that demo environment raises ValueError."""
        with pytest.raises(ValueError, match="Kalshi demo environment is unsupported"):
            get_base_url("demo")

    def test_get_base_url_staging_unsupported(self, monkeypatch):
        """Test that staging environment raises ValueError."""
        with pytest.raises(ValueError, match="Kalshi demo environment is unsupported"):
            get_base_url("staging")
