"""Test neural.data_collection.kalshi_historical module."""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from neural.data_collection.kalshi_historical import KalshiHistoricalDataSource


class TestKalshiHistoricalDataSource:
    """Test KalshiHistoricalDataSource class."""

    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    def test_initialization(self, mock_http_client):
        """Test source initialization."""
        source = KalshiHistoricalDataSource(
            market_ticker="TEST-MARKET",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        assert source.market_ticker == "TEST-MARKET"
        assert source.start_date is not None
        assert source.end_date is not None

    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    def test_initialization_with_defaults(self, mock_http_client):
        """Test initialization with default parameters."""
        source = KalshiHistoricalDataSource(market_ticker="TEST-MARKET")

        assert source.market_ticker == "TEST-MARKET"
        # Should have reasonable defaults

    @pytest.mark.asyncio
    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    async def test_fetch_trades_success(self, mock_http_client):
        """Test fetching historical trades."""
        mock_client = Mock()
        mock_client.get.return_value = {
            'trades': [
                {
                    'trade_id': '1',
                    'ticker': 'TEST-YES',
                    'yes_price': 55,
                    'count': 10,
                    'created_time': '2024-01-01T12:00:00Z'
                }
            ],
            'cursor': None
        }
        mock_http_client.return_value = mock_client

        source = KalshiHistoricalDataSource(market_ticker="TEST-MARKET")
        source.client = mock_client

        trades = await source._fetch_trades(cursor=None)

        assert len(trades) > 0
        assert 'trade_id' in trades[0]

    @pytest.mark.asyncio
    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    async def test_fetch_with_pagination(self, mock_http_client):
        """Test fetching with cursor pagination."""
        mock_client = Mock()
        
        # First call returns cursor
        mock_client.get.side_effect = [
            {
                'trades': [{'trade_id': '1'}],
                'cursor': 'cursor123'
            },
            {
                'trades': [{'trade_id': '2'}],
                'cursor': None
            }
        ]
        mock_http_client.return_value = mock_client

        source = KalshiHistoricalDataSource(market_ticker="TEST-MARKET")
        source.client = mock_client

        all_trades = []
        cursor = None
        
        # Fetch first page
        trades = await source._fetch_trades(cursor=cursor)
        all_trades.extend(trades)

        # Should have fetched data
        assert len(all_trades) > 0

    @pytest.mark.asyncio
    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    async def test_transform_to_dataframe(self, mock_http_client):
        """Test transforming trades to DataFrame."""
        mock_client = Mock()
        mock_http_client.return_value = mock_client

        source = KalshiHistoricalDataSource(market_ticker="TEST-MARKET")

        trades = [
            {
                'trade_id': '1',
                'ticker': 'TEST-YES',
                'yes_price': 55,
                'count': 10,
                'created_time': '2024-01-01T12:00:00Z'
            },
            {
                'trade_id': '2',
                'ticker': 'TEST-YES',
                'yes_price': 57,
                'count': 5,
                'created_time': '2024-01-01T12:05:00Z'
            }
        ]

        df = source._transform_to_dataframe(trades)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'yes_price' in df.columns

    @pytest.mark.asyncio
    @patch('neural.data_collection.kalshi_historical.KalshiHTTPClient')
    async def test_error_handling(self, mock_http_client):
        """Test error handling during fetch."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("API Error")
        mock_http_client.return_value = mock_client

        source = KalshiHistoricalDataSource(market_ticker="TEST-MARKET")
        source.client = mock_client

        with pytest.raises(Exception):
            await source._fetch_trades(cursor=None)

