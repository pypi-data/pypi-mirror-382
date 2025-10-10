"""Test neural.data_collection.base module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from neural.data_collection.base import DataSource, DataSourceConfig, BaseDataSource


class TestDataSourceConfig:
    """Test DataSourceConfig class."""

    def test_data_source_config_init(self):
        """Test DataSourceConfig initialization."""
        config = DataSourceConfig(
            name="test_source", config={"ticker": "TEST_TICKER", "interval": 60}
        )

        assert config.name == "test_source"
        assert config.config == {"ticker": "TEST_TICKER", "interval": 60}

    def test_data_source_config_default(self):
        """Test DataSourceConfig with default config."""
        config = DataSourceConfig(name="test_source")

        assert config.name == "test_source"
        assert config.config is None


class TestBaseDataSource:
    """Test BaseDataSource class."""

    def test_base_data_source_init(self):
        """Test BaseDataSource initialization."""
        config = DataSourceConfig(name="test_source")

        # Create a concrete implementation for testing
        class TestDataSource(BaseDataSource):
            async def _connect_impl(self) -> bool:
                return True

            async def _disconnect_impl(self) -> None:
                pass

            async def _subscribe_impl(self, channels) -> bool:
                return True

        data_source = TestDataSource(config)

        assert data_source.config == config
        assert data_source.name == "test_source"
        assert data_source._connected is False

    @pytest.mark.asyncio
    async def test_base_data_source_connect(self):
        """Test BaseDataSource connect method."""
        config = DataSourceConfig(name="test_source")

        class TestDataSource(BaseDataSource):
            async def _connect_impl(self) -> bool:
                return True

            async def _disconnect_impl(self) -> None:
                pass

            async def _subscribe_impl(self, channels) -> bool:
                return True

        data_source = TestDataSource(config)

        # First connection
        result = await data_source.connect()
        assert result is True
        assert data_source._connected is True

        # Second connection should return cached result
        result = await data_source.connect()
        assert result is True

    @pytest.mark.asyncio
    async def test_base_data_source_disconnect(self):
        """Test BaseDataSource disconnect method."""
        config = DataSourceConfig(name="test_source")

        class TestDataSource(BaseDataSource):
            async def _connect_impl(self) -> bool:
                return True

            async def _disconnect_impl(self) -> None:
                pass

            async def _subscribe_impl(self, channels) -> bool:
                return True

        data_source = TestDataSource(config)
        await data_source.connect()
        assert data_source._connected is True

        await data_source.disconnect()
        assert data_source._connected is False

        # Disconnect when not connected should not call _disconnect_impl
        await data_source.disconnect()
        assert data_source._connected is False


class TestDataSource:
    """Test DataSource class."""

    def test_data_source_init(self):
        """Test DataSource initialization - should raise error for abstract class."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            DataSource("test_source", {"ticker": "TEST_TICKER"})

    def test_data_source_init_default_config(self):
        """Test DataSource initialization with default config - should raise error for abstract class."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            DataSource("test_source")

    @pytest.mark.asyncio
    async def test_data_source_context_manager(self):
        """Test DataSource as async context manager."""

        class TestDataSource(DataSource):
            def __init__(self, name, config=None):
                super().__init__(name, config)
                self.connect_called = False
                self.disconnect_called = False

            async def connect(self):
                self.connect_called = True
                self._connected = True

            async def disconnect(self):
                self.disconnect_called = True
                self._connected = False

            async def collect(self):
                self.collected_data = [{"data": "test"}]

        data_source = TestDataSource("test_source")

        async with data_source as ds:
            assert ds.connect_called is True
            assert ds._connected is True

        assert ds.disconnect_called is True
        assert ds._connected is False
