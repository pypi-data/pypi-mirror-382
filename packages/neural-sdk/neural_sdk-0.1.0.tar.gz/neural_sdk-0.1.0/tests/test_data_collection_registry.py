"""Test neural.data_collection.registry module."""

import pytest
from neural.data_collection.registry import DataSourceRegistry, register_source, registry
from neural.data_collection.base import DataSource
from neural.data_collection.transformer import DataTransformer


class TestDataSourceRegistry:
    """Test data source registry functions."""

    def test_registry_init(self):
        """Test registry initialization."""
        reg = DataSourceRegistry()
        assert reg.sources == {}
        assert reg.transformers == {}

    def test_register_source_decorator(self):
        """Test registering a data source using decorator."""

        @register_source()
        class TestSource(DataSource):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def fetch_data(self):
                pass

        # The decorator registers with the global registry
        assert "TestSource" in registry.sources
        assert registry.sources["TestSource"] == TestSource

    def test_register_source_with_transformer(self):
        """Test registering a data source with transformer."""
        reg = DataSourceRegistry()
        transformer = DataTransformer()

        class TestSourceWithTransformer(DataSource):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def fetch_data(self):
                pass

        reg.register_source(TestSourceWithTransformer, transformer)

        assert "TestSourceWithTransformer" in reg.sources
        assert reg.sources["TestSourceWithTransformer"] == TestSourceWithTransformer
        assert reg.transformers["TestSourceWithTransformer"] == transformer

    def test_get_source_existing(self):
        """Test getting an existing source."""
        reg = DataSourceRegistry()

        class TestExistingSource(DataSource):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def fetch_data(self):
                pass

            async def collect(self):
                pass

        reg.register_source(TestExistingSource)

        # Get instance
        instance = reg.get_source("TestExistingSource", "test_source")
        assert isinstance(instance, TestExistingSource)

    def test_get_source_nonexistent(self):
        """Test getting a nonexistent source."""
        reg = DataSourceRegistry()

        with pytest.raises(ValueError, match="Source NonExistent not registered"):
            reg.get_source("NonExistent")

    def test_get_transformer_existing(self):
        """Test getting an existing transformer."""
        reg = DataSourceRegistry()
        transformer = DataTransformer()

        class TestSourceWithTransformer(DataSource):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def fetch_data(self):
                pass

        reg.register_source(TestSourceWithTransformer, transformer)

        retrieved = reg.get_transformer("TestSourceWithTransformer")
        assert retrieved is transformer

    def test_get_transformer_default(self):
        """Test getting default transformer when none registered."""
        reg = DataSourceRegistry()

        retrieved = reg.get_transformer("NonExistent")
        assert isinstance(retrieved, DataTransformer)

    def test_global_registry(self):
        """Test the global registry instance."""
        assert isinstance(registry, DataSourceRegistry)
        assert hasattr(registry, "sources")
        assert hasattr(registry, "transformers")
