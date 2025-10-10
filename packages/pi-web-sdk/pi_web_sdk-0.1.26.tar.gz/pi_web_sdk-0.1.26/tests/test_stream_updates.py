"""Tests for Stream Updates functionality."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from pi_web_sdk.controllers.stream import StreamController, StreamSetController


@pytest.fixture
def mock_client():
    """Create a mock PI Web API client."""
    client = MagicMock()
    return client


class TestStreamUpdates:
    """Test Stream Updates for single streams."""

    def test_register_update(self, mock_client):
        """Test registering a stream for updates."""
        # Arrange
        mock_client.post.return_value = {
            "LatestMarker": "marker123",
            "Status": "Succeeded"
        }
        controller = StreamController(mock_client)
        web_id = "P1AbcDEFg"

        # Act
        result = controller.register_update(web_id)

        # Assert
        assert result["LatestMarker"] == "marker123"
        assert result["Status"] == "Succeeded"
        mock_client.post.assert_called_once_with(
            f"streams/{web_id}/updates",
            params={}
        )

    def test_register_update_with_selected_fields(self, mock_client):
        """Test registering a stream for updates with selected fields."""
        # Arrange
        mock_client.post.return_value = {
            "LatestMarker": "marker123",
            "Status": "Succeeded"
        }
        controller = StreamController(mock_client)
        web_id = "P1AbcDEFg"
        selected_fields = "Items.Timestamp;Items.Value"

        # Act
        result = controller.register_update(web_id, selected_fields=selected_fields)

        # Assert
        assert result["LatestMarker"] == "marker123"
        mock_client.post.assert_called_once_with(
            f"streams/{web_id}/updates",
            params={"selectedFields": selected_fields}
        )

    def test_retrieve_update(self, mock_client):
        """Test retrieving updates using a marker."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-01T00:00:00Z", "Value": 42.0},
                {"Timestamp": "2025-01-01T00:01:00Z", "Value": 43.0}
            ],
            "LatestMarker": "marker456"
        }
        controller = StreamController(mock_client)
        marker = "marker123"

        # Act
        result = controller.retrieve_update(marker)

        # Assert
        assert len(result["Items"]) == 2
        assert result["LatestMarker"] == "marker456"
        mock_client.get.assert_called_once_with(
            f"streams/updates/{marker}",
            params={}
        )

    def test_retrieve_update_with_options(self, mock_client):
        """Test retrieving updates with selected fields and desired units."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [],
            "LatestMarker": "marker456"
        }
        controller = StreamController(mock_client)
        marker = "marker123"
        selected_fields = "Items.Value"
        desired_units = "degF"

        # Act
        result = controller.retrieve_update(
            marker,
            selected_fields=selected_fields,
            desired_units=desired_units
        )

        # Assert
        assert result["LatestMarker"] == "marker456"
        mock_client.get.assert_called_once_with(
            f"streams/updates/{marker}",
            params={
                "selectedFields": selected_fields,
                "desiredUnits": desired_units
            }
        )


class TestStreamSetUpdates:
    """Test Stream Updates for multiple streams."""

    def test_register_updates(self, mock_client):
        """Test registering multiple streams for updates."""
        # Arrange
        mock_client.post.return_value = {
            "Items": [
                {"WebId": "P1AbcDEFg", "Status": "Succeeded"},
                {"WebId": "P1XyzABCd", "Status": "Succeeded"}
            ],
            "LatestMarker": "marker789"
        }
        controller = StreamSetController(mock_client)
        web_ids = ["P1AbcDEFg", "P1XyzABCd"]

        # Act
        result = controller.register_updates(web_ids)

        # Assert
        assert len(result["Items"]) == 2
        assert result["LatestMarker"] == "marker789"
        mock_client.post.assert_called_once_with(
            "streamsets/updates",
            params={"webId": web_ids}
        )

    def test_register_updates_with_selected_fields(self, mock_client):
        """Test registering multiple streams with selected fields."""
        # Arrange
        mock_client.post.return_value = {
            "Items": [{"WebId": "P1AbcDEFg", "Status": "Succeeded"}],
            "LatestMarker": "marker789"
        }
        controller = StreamSetController(mock_client)
        web_ids = ["P1AbcDEFg"]
        selected_fields = "Items.Timestamp;Items.Value"

        # Act
        result = controller.register_updates(web_ids, selected_fields=selected_fields)

        # Assert
        assert result["LatestMarker"] == "marker789"
        mock_client.post.assert_called_once_with(
            "streamsets/updates",
            params={
                "webId": web_ids,
                "selectedFields": selected_fields
            }
        )

    def test_retrieve_updates(self, mock_client):
        """Test retrieving updates for multiple streams."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "P1AbcDEFg",
                    "Items": [
                        {"Timestamp": "2025-01-01T00:00:00Z", "Value": 42.0}
                    ]
                },
                {
                    "WebId": "P1XyzABCd",
                    "Items": [
                        {"Timestamp": "2025-01-01T00:00:00Z", "Value": 100.0}
                    ]
                }
            ],
            "LatestMarker": "marker999"
        }
        controller = StreamSetController(mock_client)
        marker = "marker789"

        # Act
        result = controller.retrieve_updates(marker)

        # Assert
        assert len(result["Items"]) == 2
        assert result["LatestMarker"] == "marker999"
        mock_client.get.assert_called_once_with(
            "streamsets/updates",
            params={"marker": marker}
        )

    def test_retrieve_updates_with_options(self, mock_client):
        """Test retrieving updates with selected fields and desired units."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [],
            "LatestMarker": "marker999"
        }
        controller = StreamSetController(mock_client)
        marker = "marker789"
        selected_fields = "Items.Value"
        desired_units = "degF"

        # Act
        result = controller.retrieve_updates(
            marker,
            selected_fields=selected_fields,
            desired_units=desired_units
        )

        # Assert
        assert result["LatestMarker"] == "marker999"
        mock_client.get.assert_called_once_with(
            "streamsets/updates",
            params={
                "marker": marker,
                "selectedFields": selected_fields,
                "desiredUnits": desired_units
            }
        )


@pytest.mark.integration
class TestStreamUpdatesIntegration:
    """Integration tests for Stream Updates (requires live PI server)."""

    def test_stream_update_workflow(self, pi_web_api_client):
        """Test complete stream update workflow."""
        pytest.skip("Requires live PI server and valid stream WebID")

        # Example usage:
        # 1. Register for updates
        # registration = pi_web_api_client.stream.register_update(stream_web_id)
        # marker = registration["LatestMarker"]
        #
        # 2. Wait for data changes or poll for updates
        # import time
        # time.sleep(5)
        #
        # 3. Retrieve updates
        # updates = pi_web_api_client.stream.retrieve_update(marker)
        # new_marker = updates["LatestMarker"]
        #
        # 4. Continue polling with new marker
        # more_updates = pi_web_api_client.stream.retrieve_update(new_marker)

    def test_streamset_update_workflow(self, pi_web_api_client):
        """Test complete streamset update workflow."""
        pytest.skip("Requires live PI server and valid stream WebIDs")
        
        # Example usage:
        # 1. Register multiple streams for updates
        # registration = pi_web_api_client.streamset.register_updates([stream_web_id_1, stream_web_id_2])
        # marker = registration["LatestMarker"]
        #
        # 2. Retrieve updates for all streams
        # updates = pi_web_api_client.streamset.retrieve_updates(marker)
        # new_marker = updates["LatestMarker"]
        #
        # 3. Process updates for each stream
        # for stream_update in updates["Items"]:
        #     stream_web_id = stream_update["WebId"]
        #     values = stream_update["Items"]
