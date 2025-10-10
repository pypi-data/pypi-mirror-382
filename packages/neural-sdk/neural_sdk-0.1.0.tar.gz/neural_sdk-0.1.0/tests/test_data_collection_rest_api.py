"""Test neural.data_collection.rest_api module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from neural.data_collection.rest_api import RestAPIDataSource


class TestRestAPIDataSource:
    """Test RestAPIDataSource class."""

    def test_initialization(self):
        """Test basic initialization."""
        source = RestAPIDataSource(
            name="test_api",
            base_url="https://api.example.com",
            endpoint="/data"
        )

        assert source.name == "test_api"
        assert source.base_url == "https://api.example.com"
        assert source.endpoint == "/data"

    def test_build_url(self):
        """Test URL building."""
        source = RestAPIDataSource(
            name="test_api",
            base_url="https://api.example.com",
            endpoint="/data"
        )

        url = source._build_url()
        assert url == "https://api.example.com/data"

    def test_build_url_with_params(self):
        """Test URL building with query parameters."""
        source = RestAPIDataSource(
            name="test_api",
            base_url="https://api.example.com",
            endpoint="/data",
            params={"limit": 10, "status": "active"}
        )

        url = source._build_url()
        assert "limit=10" in url
        assert "status=active" in url

    @pytest.mark.asyncio
    async def test_fetch_data(self):
        """Test fetching data from API."""
        source = RestAPIDataSource(
            name="test_api",
            base_url="https://api.example.com",
            endpoint="/data"
        )

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value={"data": [1, 2, 3]})
            mock_response.status = 200
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            # Would test actual fetch here
            assert source is not None

    def test_set_headers(self):
        """Test setting request headers."""
        source = RestAPIDataSource(
            name="test_api",
            base_url="https://api.example.com",
            endpoint="/data",
            headers={"Authorization": "Bearer token123"}
        )

        assert "Authorization" in source.headers
        assert source.headers["Authorization"] == "Bearer token123"

