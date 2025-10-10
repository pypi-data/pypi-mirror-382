"""Tests for stream controller enums."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.stream import BufferOption, UpdateOption, StreamController


class TestBufferOption:
    """Test BufferOption enum."""

    def test_buffer_option_values(self):
        """Test that BufferOption has correct values."""
        assert BufferOption.DO_NOT_BUFFER.value == "DoNotBuffer"
        assert BufferOption.BUFFER_IF_POSSIBLE.value == "BufferIfPossible"
        assert BufferOption.BUFFER.value == "Buffer"

    def test_buffer_option_count(self):
        """Test that BufferOption has all expected options."""
        assert len(BufferOption) == 3


class TestUpdateOption:
    """Test UpdateOption enum."""

    def test_update_option_values(self):
        """Test that UpdateOption has correct values."""
        assert UpdateOption.REPLACE.value == "Replace"
        assert UpdateOption.INSERT.value == "Insert"
        assert UpdateOption.NO_REPLACE.value == "NoReplace"
        assert UpdateOption.REPLACE_ONLY.value == "ReplaceOnly"
        assert UpdateOption.INSERT_NO_COMPRESSION.value == "InsertNoCompression"
        assert UpdateOption.REMOVE.value == "Remove"

    def test_update_option_count(self):
        """Test that UpdateOption has all expected options."""
        assert len(UpdateOption) == 6


class TestStreamControllerWithEnums:
    """Test StreamController methods with enum parameters."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = MagicMock()
        client.put.return_value = {"WebId": "test-id", "Value": 42}
        client.post.return_value = {"Submitted": 2}
        return client

    def test_update_value_with_buffer_enum(self, mock_client):
        """Test update_value with BufferOption enum."""
        controller = StreamController(mock_client)

        result = controller.update_value(
            "test-web-id",
            {"Value": 42},
            buffer_option=BufferOption.BUFFER,
            update_option=UpdateOption.REPLACE
        )

        # Verify the client was called correctly
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args

        # Check the params
        assert call_args[1]["params"]["bufferOption"] == "Buffer"
        assert call_args[1]["params"]["updateOption"] == "Replace"

        # Check the result
        assert result["WebId"] == "test-id"

    def test_update_value_with_string_params(self, mock_client):
        """Test update_value with string parameters (backward compatibility)."""
        controller = StreamController(mock_client)

        result = controller.update_value(
            "test-web-id",
            {"Value": 42},
            buffer_option="DoNotBuffer",
            update_option="Insert"
        )

        # Verify the client was called correctly
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args

        # Check the params
        assert call_args[1]["params"]["bufferOption"] == "DoNotBuffer"
        assert call_args[1]["params"]["updateOption"] == "Insert"

    def test_update_values_with_enums(self, mock_client):
        """Test update_values with enum parameters."""
        controller = StreamController(mock_client)

        values = [
            {"Timestamp": "2024-01-01T00:00:00Z", "Value": 10},
            {"Timestamp": "2024-01-01T01:00:00Z", "Value": 20}
        ]

        result = controller.update_values(
            "test-web-id",
            values,
            buffer_option=BufferOption.BUFFER_IF_POSSIBLE,
            update_option=UpdateOption.NO_REPLACE
        )

        # Verify the client was called correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Check the params
        assert call_args[1]["params"]["bufferOption"] == "BufferIfPossible"
        assert call_args[1]["params"]["updateOption"] == "NoReplace"

        # Check the result
        assert result["Submitted"] == 2

    def test_update_value_no_options(self, mock_client):
        """Test update_value without buffer/update options."""
        controller = StreamController(mock_client)

        controller.update_value("test-web-id", {"Value": 42})

        # Verify the client was called with empty params
        call_args = mock_client.put.call_args
        assert call_args[1]["params"] == {}

    def test_all_buffer_options(self, mock_client):
        """Test all buffer option values."""
        controller = StreamController(mock_client)

        for option in BufferOption:
            controller.update_value(
                "test-web-id",
                {"Value": 42},
                buffer_option=option
            )

            call_args = mock_client.put.call_args
            assert call_args[1]["params"]["bufferOption"] == option.value

    def test_all_update_options(self, mock_client):
        """Test all update option values."""
        controller = StreamController(mock_client)

        for option in UpdateOption:
            controller.update_value(
                "test-web-id",
                {"Value": 42},
                update_option=option
            )

            call_args = mock_client.put.call_args
            assert call_args[1]["params"]["updateOption"] == option.value
