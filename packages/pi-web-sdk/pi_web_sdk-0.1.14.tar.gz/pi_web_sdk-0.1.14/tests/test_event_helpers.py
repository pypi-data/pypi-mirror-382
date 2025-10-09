"""Tests for EventFrameHelpers convenience methods."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from pi_web_sdk.controllers.event_helpers import EventFrameHelpers


@pytest.fixture
def mock_client():
    """Create a mock PIWebAPIClient."""
    client = MagicMock()
    client.event_frame = MagicMock()
    client.attribute = MagicMock()
    return client


@pytest.fixture
def helpers(mock_client):
    """Create EventFrameHelpers instance with mock client."""
    return EventFrameHelpers(mock_client)


class TestEventFrameHelpers:
    """Test EventFrameHelpers convenience methods."""

    def test_create_event_frame_with_attributes(self, helpers, mock_client):
        """Test creating event frame with attributes in one call."""
        # Arrange
        mock_client.event_frame.create.return_value = {
            "WebId": "F1AbC123",
            "Name": "Batch001",
        }
        mock_client.event_frame.create_attribute.return_value = {
            "WebId": "A1DeF456",
            "Name": "Operator",
        }

        # Act
        result = helpers.create_event_frame_with_attributes(
            database_web_id="D1XyZ789",
            name="Batch001",
            description="Production batch",
            start_time=datetime.now(),
            attributes={"Operator": "John", "Product": "Widget"},
        )

        # Assert
        assert result["WebId"] == "F1AbC123"
        mock_client.event_frame.create.assert_called_once()
        assert mock_client.event_frame.create_attribute.call_count == 2
        assert mock_client.attribute.set_value.call_count == 2

    def test_create_event_frame_without_attributes(self, helpers, mock_client):
        """Test creating event frame without attributes."""
        # Arrange
        mock_client.event_frame.create.return_value = {
            "WebId": "F1AbC123",
            "Name": "Batch001",
        }

        # Act
        result = helpers.create_event_frame_with_attributes(
            database_web_id="D1XyZ789",
            name="Batch001",
            description="Production batch",
            start_time=datetime.now(),
        )

        # Assert
        assert result["WebId"] == "F1AbC123"
        mock_client.event_frame.create.assert_called_once()
        mock_client.event_frame.create_attribute.assert_not_called()

    def test_create_child_event_frame_with_attributes(self, helpers, mock_client):
        """Test creating child event frame with attributes."""
        # Arrange
        mock_client.event_frame.create_child_event_frame.return_value = {
            "WebId": "F2BcD234",
            "Name": "Step1",
        }
        mock_client.event_frame.create_attribute.return_value = {
            "WebId": "A2EfG567",
            "Name": "Duration",
        }

        # Act
        result = helpers.create_child_event_frame_with_attributes(
            parent_web_id="F1AbC123",
            name="Step1",
            description="Mixing step",
            start_time=datetime.now(),
            attributes={"Duration": "30", "Temperature": "75"},
        )

        # Assert
        assert result["WebId"] == "F2BcD234"
        mock_client.event_frame.create_child_event_frame.assert_called_once()
        assert mock_client.event_frame.create_attribute.call_count == 2

    def test_update_event_frame_attributes(self, helpers, mock_client):
        """Test updating multiple attributes."""
        # Arrange
        mock_client.event_frame.get_attributes.return_value = {
            "Items": [
                {"Name": "Status", "WebId": "A1"},
                {"Name": "Temperature", "WebId": "A2"},
            ]
        }

        # Act
        results = helpers.update_event_frame_attributes(
            event_web_id="F1AbC123",
            attributes={"Status": "Complete", "Temperature": "80"},
        )

        # Assert
        assert len(results) == 2
        assert "Status" in results
        assert "Temperature" in results
        assert mock_client.attribute.set_value.call_count == 2

    def test_update_event_frame_attributes_missing(self, helpers, mock_client):
        """Test updating attributes when some don't exist."""
        # Arrange
        mock_client.event_frame.get_attributes.return_value = {
            "Items": [{"Name": "Status", "WebId": "A1"}]
        }

        # Act
        results = helpers.update_event_frame_attributes(
            event_web_id="F1AbC123",
            attributes={"Status": "Complete", "NonExistent": "Value"},
        )

        # Assert
        assert len(results) == 2
        assert "error" in results["NonExistent"]
        mock_client.attribute.set_value.call_count == 1

    def test_create_event_frame_hierarchy(self, helpers, mock_client):
        """Test creating hierarchical event frame structure."""
        # Arrange
        mock_client.event_frame.create.return_value = {
            "WebId": "F1Root",
            "Name": "Batch001",
        }
        mock_client.event_frame.create_child_event_frame.side_effect = [
            {"WebId": "F2Child1", "Name": "Mix"},
            {"WebId": "F3Child2", "Name": "Package"},
        ]
        mock_client.event_frame.create_attribute.return_value = {"WebId": "A1"}

        # Act
        result = helpers.create_event_frame_hierarchy(
            database_web_id="D1",
            root_name="Batch001",
            root_description="Production batch",
            start_time=datetime.now(),
            root_attributes={"Operator": "John"},
            children=[
                {
                    "name": "Mix",
                    "description": "Mixing step",
                    "start_time": datetime.now(),
                    "attributes": {"Duration": "30"},
                },
                {
                    "name": "Package",
                    "description": "Packaging step",
                    "start_time": datetime.now() + timedelta(minutes=30),
                },
            ],
        )

        # Assert
        assert result["root"]["WebId"] == "F1Root"
        assert len(result["children"]) == 2
        assert result["children"][0]["WebId"] == "F2Child1"
        assert result["children"][1]["WebId"] == "F3Child2"

    def test_get_event_frame_with_attributes(self, helpers, mock_client):
        """Test getting event frame with attributes and values."""
        # Arrange
        mock_client.event_frame.get.return_value = {
            "WebId": "F1",
            "Name": "Batch001",
        }
        mock_client.event_frame.get_attributes.return_value = {
            "Items": [
                {"WebId": "A1", "Name": "Status"},
                {"WebId": "A2", "Name": "Operator"},
            ]
        }
        mock_client.attribute.get_value.side_effect = [
            {"Value": "Running", "Timestamp": "2024-01-01T12:00:00Z"},
            {"Value": "John", "Timestamp": "2024-01-01T12:00:00Z"},
        ]

        # Act
        result = helpers.get_event_frame_with_attributes("F1", include_values=True)

        # Assert
        assert result["WebId"] == "F1"
        assert len(result["attributes"]) == 2
        assert result["attributes"][0]["Value"] == "Running"
        assert result["attributes"][1]["Value"] == "John"

    def test_get_event_frame_without_values(self, helpers, mock_client):
        """Test getting event frame without fetching values."""
        # Arrange
        mock_client.event_frame.get.return_value = {"WebId": "F1", "Name": "Batch001"}
        mock_client.event_frame.get_attributes.return_value = {
            "Items": [{"WebId": "A1", "Name": "Status"}]
        }

        # Act
        result = helpers.get_event_frame_with_attributes("F1", include_values=False)

        # Assert
        assert result["WebId"] == "F1"
        assert len(result["attributes"]) == 1
        mock_client.attribute.get_value.assert_not_called()

    def test_close_event_frame(self, helpers, mock_client):
        """Test closing an event frame."""
        # Arrange
        end_time = datetime.now()
        mock_client.event_frame.get.return_value = {
            "WebId": "F1",
            "Name": "Batch001",
            "EndTime": end_time.isoformat(),
        }

        # Act
        result = helpers.close_event_frame(
            event_web_id="F1",
            end_time=end_time,
            capture_values=True,
        )

        # Assert
        mock_client.event_frame.update.assert_called_once()
        mock_client.event_frame.capture_values.assert_called_once_with("F1")
        assert result["WebId"] == "F1"

    def test_close_event_frame_without_capture(self, helpers, mock_client):
        """Test closing event frame without capturing values."""
        # Arrange
        end_time = datetime.now()
        mock_client.event_frame.get.return_value = {"WebId": "F1"}

        # Act
        result = helpers.close_event_frame(
            event_web_id="F1",
            end_time=end_time,
            capture_values=False,
        )

        # Assert
        mock_client.event_frame.update.assert_called_once()
        mock_client.event_frame.capture_values.assert_not_called()
