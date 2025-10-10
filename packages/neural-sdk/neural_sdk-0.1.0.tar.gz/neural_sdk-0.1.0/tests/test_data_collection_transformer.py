"""Test neural.data_collection.transformer module."""

import pytest
from neural.data_collection.transformer import DataTransformer


class TestDataTransformer:
    """Test data transformer functionality."""

    def test_transformer_init_default(self):
        """Test transformer initialization with default transformations."""
        transformer = DataTransformer()
        assert transformer.transformations == []

    def test_transformer_init_with_transformations(self):
        """Test transformer initialization with transformations."""

        def test_transform(data):
            return data

        transformer = DataTransformer([test_transform])
        assert len(transformer.transformations) == 1
        assert transformer.transformations[0] == test_transform

    def test_add_transformation(self):
        """Test adding a transformation function."""
        transformer = DataTransformer()

        def test_transform(data):
            return data

        transformer.add_transformation(test_transform)
        assert len(transformer.transformations) == 1
        assert transformer.transformations[0] == test_transform

    def test_transform_no_transformations(self):
        """Test transforming data with no transformations."""
        transformer = DataTransformer()
        data = {"key": "value"}
        result = transformer.transform(data)

        assert result["key"] == "value"
        assert "timestamp" in result

    def test_transform_with_transformations(self):
        """Test transforming data with transformations."""

        def add_prefix(data):
            return {"prefixed_" + k: v for k, v in data.items()}

        transformer = DataTransformer([add_prefix])
        data = {"key": "value"}
        result = transformer.transform(data)

        assert "prefixed_key" in result
        assert result["prefixed_key"] == "value"
        assert "timestamp" in result

    def test_transform_multiple_transformations(self):
        """Test transforming data with multiple transformations."""

        def add_prefix(data):
            return {"prefixed_" + k: v for k, v in data.items()}

        def uppercase_keys(data):
            return {k.upper(): v for k, v in data.items()}

        transformer = DataTransformer([add_prefix, uppercase_keys])
        data = {"key": "value"}
        result = transformer.transform(data)

        assert "PREFIXED_KEY" in result
        assert result["PREFIXED_KEY"] == "value"
        assert "timestamp" in result

    def test_transform_preserves_existing_timestamp(self):
        """Test that existing timestamp is preserved."""
        transformer = DataTransformer()
        data = {"key": "value", "timestamp": "existing_time"}
        result = transformer.transform(data)

        assert result["timestamp"] == "existing_time"

    def test_flatten_keys_simple(self):
        """Test flattening simple dict keys."""
        data = {"key1": "value1", "key2": "value2"}
        result = DataTransformer.flatten_keys(data)
        assert result == data

    def test_flatten_keys_nested(self):
        """Test flattening nested dict keys."""
        data = {"key1": "value1", "nested": {"key2": "value2", "deep": {"key3": "value3"}}}
        result = DataTransformer.flatten_keys(data)
        expected = {"key1": "value1", "nested.key2": "value2", "nested.deep.key3": "value3"}
        assert result == expected

    def test_flatten_keys_with_prefix(self):
        """Test flattening keys with prefix."""
        data = {"key1": "value1", "nested": {"key2": "value2"}}
        result = DataTransformer.flatten_keys(data, prefix="prefix")
        expected = {"prefix.key1": "value1", "prefix.nested.key2": "value2"}
        assert result == expected

    def test_normalize_types_strings_to_numbers(self):
        """Test normalizing string numbers to actual numbers."""
        data = {
            "int_str": "42",
            "float_str": "3.14",
            "non_numeric": "hello",
            "already_int": 10,
            "already_float": 2.71,
        }
        result = DataTransformer.normalize_types(data)
        expected = {
            "int_str": 42,
            "float_str": 3.14,
            "non_numeric": "hello",
            "already_int": 10,
            "already_float": 2.71,
        }
        assert result == expected

    def test_normalize_types_empty_dict(self):
        """Test normalizing empty dictionary."""
        data = {}
        result = DataTransformer.normalize_types(data)
        assert result == {}

    def test_normalize_types_no_strings(self):
        """Test normalizing dict with no strings."""
        data = {"int": 42, "float": 3.14, "bool": True, "none": None}
        result = DataTransformer.normalize_types(data)
        assert result == data
