"""Tests for Stream controller enhanced methods."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from pi_web_sdk.controllers.stream import StreamController, StreamSetController


@pytest.fixture
def mock_client():
    """Create a mock PIWebAPIClient."""
    return MagicMock()


@pytest.fixture
def stream_controller(mock_client):
    """Create StreamController instance."""
    return StreamController(mock_client)


@pytest.fixture
def streamset_controller(mock_client):
    """Create StreamSetController instance."""
    return StreamSetController(mock_client)


class TestStreamControllerEnhancements:
    """Test Stream controller new methods."""

    def test_get_end(self, stream_controller, mock_client):
        """Test get end value."""
        mock_client.get.return_value = {
            "Timestamp": "2025-01-15T10:30:00Z",
            "Value": 98.5,
            "Good": True
        }

        result = stream_controller.get_end("S1")

        assert result["Value"] == 98.5
        assert result["Good"] is True
        mock_client.get.assert_called_once_with(
            "streams/S1/end",
            params={}
        )

    def test_get_end_with_units(self, stream_controller, mock_client):
        """Test get end value with desired units."""
        mock_client.get.return_value = {
            "Timestamp": "2025-01-15T10:30:00Z",
            "Value": 37.0,
            "UnitsAbbreviation": "degC"
        }

        result = stream_controller.get_end("S1", desired_units="degC")

        assert result["Value"] == 37.0
        assert result["UnitsAbbreviation"] == "degC"
        mock_client.get.assert_called_once_with(
            "streams/S1/end",
            params={"desiredUnits": "degC"}
        )

    def test_get_end_with_fields(self, stream_controller, mock_client):
        """Test get end value with selected fields."""
        mock_client.get.return_value = {"Value": 98.5}

        result = stream_controller.get_end("S1", selected_fields="Value")

        assert result["Value"] == 98.5
        mock_client.get.assert_called_once_with(
            "streams/S1/end",
            params={"selectedFields": "Value"}
        )

    def test_get_recorded_at_time_string(self, stream_controller, mock_client):
        """Test get recorded at time with string timestamp."""
        mock_client.get.return_value = {
            "Timestamp": "2025-01-15T10:00:00Z",
            "Value": 95.0
        }

        result = stream_controller.get_recorded_at_time("S1", "2025-01-15T10:00:00Z")

        assert result["Value"] == 95.0
        mock_client.get.assert_called_once_with(
            "streams/S1/recordedattime",
            params={"time": "2025-01-15T10:00:00Z"}
        )

    def test_get_recorded_at_time_datetime(self, stream_controller, mock_client):
        """Test get recorded at time with datetime object."""
        mock_client.get.return_value = {
            "Timestamp": "2025-01-15T10:00:00Z",
            "Value": 95.0
        }

        dt = datetime(2025, 1, 15, 10, 0, 0)
        result = stream_controller.get_recorded_at_time("S1", dt)

        assert result["Value"] == 95.0
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streams/S1/recordedattime"
        assert "time" in call_args[1]["params"]

    def test_get_recorded_at_time_with_retrieval_mode(self, stream_controller, mock_client):
        """Test get recorded at time with retrieval mode."""
        mock_client.get.return_value = {
            "Timestamp": "2025-01-15T10:00:00Z",
            "Value": 95.0
        }

        result = stream_controller.get_recorded_at_time(
            "S1",
            "2025-01-15T10:00:00Z",
            retrieval_mode="Exact"
        )

        assert result["Value"] == 95.0
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["retrievalMode"] == "Exact"

    def test_get_recorded_at_times_strings(self, stream_controller, mock_client):
        """Test get recorded at times with string timestamps."""
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5},
                {"Timestamp": "2025-01-15T12:00:00Z", "Value": 98.0}
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T11:00:00Z", "2025-01-15T12:00:00Z"]
        result = stream_controller.get_recorded_at_times("S1", times)

        assert len(result["Items"]) == 3
        assert result["Items"][0]["Value"] == 95.0
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streams/S1/recordedattimes"
        assert call_args[1]["params"]["time"] == times

    def test_get_recorded_at_times_datetimes(self, stream_controller, mock_client):
        """Test get recorded at times with datetime objects."""
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5}
            ]
        }

        times = [
            datetime(2025, 1, 15, 10, 0, 0),
            datetime(2025, 1, 15, 11, 0, 0)
        ]
        result = stream_controller.get_recorded_at_times("S1", times)

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert len(call_args[1]["params"]["time"]) == 2

    def test_get_interpolated_at_times_strings(self, stream_controller, mock_client):
        """Test get interpolated at times with string timestamps."""
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                {"Timestamp": "2025-01-15T10:30:00Z", "Value": 95.75},
                {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5}
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T10:30:00Z", "2025-01-15T11:00:00Z"]
        result = stream_controller.get_interpolated_at_times("S1", times)

        assert len(result["Items"]) == 3
        assert result["Items"][1]["Value"] == 95.75
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streams/S1/interpolatedattimes"
        assert call_args[1]["params"]["time"] == times

    def test_get_interpolated_at_times_with_filter(self, stream_controller, mock_client):
        """Test get interpolated at times with filter expression."""
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0, "Good": True},
                {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5, "Good": True}
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T11:00:00Z"]
        result = stream_controller.get_interpolated_at_times(
            "S1",
            times,
            filter_expression="'%value%' > 90"
        )

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["filterExpression"] == "'%value%' > 90"

    def test_get_channel_default(self, stream_controller, mock_client):
        """Test get channel with default parameters."""
        mock_client.get.return_value = {
            "WebId": "C1",
            "Items": []
        }

        result = stream_controller.get_channel("S1")

        assert result["WebId"] == "C1"
        mock_client.get.assert_called_once_with(
            "streams/S1/channel",
            params={"includeInitialValues": False}
        )

    def test_get_channel_with_initial_values(self, stream_controller, mock_client):
        """Test get channel with initial values."""
        mock_client.get.return_value = {
            "WebId": "C1",
            "Items": [{"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0}]
        }

        result = stream_controller.get_channel("S1", include_initial_values=True)

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["includeInitialValues"] is True

    def test_get_channel_with_heartbeat(self, stream_controller, mock_client):
        """Test get channel with heartbeat rate."""
        mock_client.get.return_value = {"WebId": "C1"}

        result = stream_controller.get_channel("S1", heartbeat_rate=30)

        assert result["WebId"] == "C1"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["heartbeatRate"] == 30


class TestStreamSetControllerEnhancements:
    """Test StreamSet controller new methods."""

    def test_get_end(self, streamset_controller, mock_client):
        """Test get end values for multiple streams."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "S1", "Value": 98.5},
                {"WebId": "S2", "Value": 102.3},
                {"WebId": "S3", "Value": 95.7}
            ]
        }

        result = streamset_controller.get_end(["S1", "S2", "S3"])

        assert len(result["Items"]) == 3
        assert result["Items"][0]["Value"] == 98.5
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streamsets/end"
        assert call_args[1]["params"]["webId"] == ["S1", "S2", "S3"]

    def test_get_end_with_units(self, streamset_controller, mock_client):
        """Test get end values with desired units."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "S1", "Value": 37.0, "UnitsAbbreviation": "degC"},
                {"WebId": "S2", "Value": 45.5, "UnitsAbbreviation": "degC"}
            ]
        }

        result = streamset_controller.get_end(["S1", "S2"], desired_units="degC")

        assert len(result["Items"]) == 2
        assert result["Items"][0]["UnitsAbbreviation"] == "degC"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["desiredUnits"] == "degC"

    def test_get_recorded_at_time(self, streamset_controller, mock_client):
        """Test get recorded at time for multiple streams."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "S1", "Value": 95.0},
                {"WebId": "S2", "Value": 100.5}
            ]
        }

        result = streamset_controller.get_recorded_at_time(
            ["S1", "S2"],
            "2025-01-15T10:00:00Z"
        )

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streamsets/recordedattime"
        assert call_args[1]["params"]["time"] == "2025-01-15T10:00:00Z"

    def test_get_recorded_at_time_with_retrieval_mode(self, streamset_controller, mock_client):
        """Test get recorded at time with retrieval mode."""
        mock_client.get.return_value = {
            "Items": [{"WebId": "S1", "Value": 95.0}]
        }

        result = streamset_controller.get_recorded_at_time(
            ["S1"],
            "2025-01-15T10:00:00Z",
            retrieval_mode="Before"
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["retrievalMode"] == "Before"

    def test_get_recorded_at_times(self, streamset_controller, mock_client):
        """Test get recorded at times for multiple streams."""
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "S1",
                    "Items": [
                        {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                        {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5}
                    ]
                },
                {
                    "WebId": "S2",
                    "Items": [
                        {"Timestamp": "2025-01-15T10:00:00Z", "Value": 100.0},
                        {"Timestamp": "2025-01-15T11:00:00Z", "Value": 101.5}
                    ]
                }
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T11:00:00Z"]
        result = streamset_controller.get_recorded_at_times(["S1", "S2"], times)

        assert len(result["Items"]) == 2
        assert len(result["Items"][0]["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streamsets/recordedattimes"
        assert call_args[1]["params"]["time"] == times

    def test_get_interpolated_at_times(self, streamset_controller, mock_client):
        """Test get interpolated at times for multiple streams."""
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "S1",
                    "Items": [
                        {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                        {"Timestamp": "2025-01-15T10:30:00Z", "Value": 95.75}
                    ]
                }
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T10:30:00Z"]
        result = streamset_controller.get_interpolated_at_times(["S1"], times)

        assert len(result["Items"]) == 1
        assert len(result["Items"][0]["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streamsets/interpolatedattimes"

    def test_get_interpolated_at_times_with_filter(self, streamset_controller, mock_client):
        """Test get interpolated at times with filter expression."""
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "S1",
                    "Items": [
                        {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0, "Good": True}
                    ]
                }
            ]
        }

        times = ["2025-01-15T10:00:00Z"]
        result = streamset_controller.get_interpolated_at_times(
            ["S1"],
            times,
            filter_expression="'%value%' > 90"
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["filterExpression"] == "'%value%' > 90"

    def test_get_channel_default(self, streamset_controller, mock_client):
        """Test get channel for multiple streams."""
        mock_client.get.return_value = {
            "WebId": "C1",
            "Items": []
        }

        result = streamset_controller.get_channel(["S1", "S2"])

        assert result["WebId"] == "C1"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "streamsets/channel"
        assert call_args[1]["params"]["webId"] == ["S1", "S2"]
        assert call_args[1]["params"]["includeInitialValues"] is False

    def test_get_channel_with_initial_values(self, streamset_controller, mock_client):
        """Test get channel with initial values."""
        mock_client.get.return_value = {
            "WebId": "C1",
            "Items": [
                {"WebId": "S1", "Value": 95.0},
                {"WebId": "S2", "Value": 100.0}
            ]
        }

        result = streamset_controller.get_channel(["S1", "S2"], include_initial_values=True)

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["includeInitialValues"] is True

    def test_get_channel_with_heartbeat(self, streamset_controller, mock_client):
        """Test get channel with heartbeat rate."""
        mock_client.get.return_value = {"WebId": "C1"}

        result = streamset_controller.get_channel(["S1", "S2"], heartbeat_rate=60)

        assert result["WebId"] == "C1"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["heartbeatRate"] == 60


class TestStreamWorkflows:
    """Test stream operation workflows."""

    def test_historical_query_workflow(self, stream_controller, mock_client):
        """Test workflow for querying historical data at specific times."""
        # Get recorded values at specific times
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:00:00Z", "Value": 95.0},
                {"Timestamp": "2025-01-15T11:00:00Z", "Value": 96.5},
                {"Timestamp": "2025-01-15T12:00:00Z", "Value": 98.0}
            ]
        }

        times = ["2025-01-15T10:00:00Z", "2025-01-15T11:00:00Z", "2025-01-15T12:00:00Z"]
        recorded = stream_controller.get_recorded_at_times("S1", times)

        assert len(recorded["Items"]) == 3
        assert recorded["Items"][0]["Value"] == 95.0

        # Get interpolated values between recorded times
        mock_client.get.return_value = {
            "Items": [
                {"Timestamp": "2025-01-15T10:30:00Z", "Value": 95.75},
                {"Timestamp": "2025-01-15T11:30:00Z", "Value": 97.25}
            ]
        }

        interpolated_times = ["2025-01-15T10:30:00Z", "2025-01-15T11:30:00Z"]
        interpolated = stream_controller.get_interpolated_at_times("S1", interpolated_times)

        assert len(interpolated["Items"]) == 2
        assert interpolated["Items"][0]["Value"] == 95.75

    def test_multi_stream_comparison_workflow(self, streamset_controller, mock_client):
        """Test workflow for comparing multiple streams."""
        # Get latest values for all streams
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "S1", "Value": 98.5, "Timestamp": "2025-01-15T12:00:00Z"},
                {"WebId": "S2", "Value": 102.3, "Timestamp": "2025-01-15T12:00:00Z"},
                {"WebId": "S3", "Value": 95.7, "Timestamp": "2025-01-15T12:00:00Z"}
            ]
        }

        latest = streamset_controller.get_end(["S1", "S2", "S3"])
        assert len(latest["Items"]) == 3

        # Get historical comparison at same time
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "S1", "Value": 90.0},
                {"WebId": "S2", "Value": 95.0},
                {"WebId": "S3", "Value": 88.0}
            ]
        }

        historical = streamset_controller.get_recorded_at_time(
            ["S1", "S2", "S3"],
            "2025-01-15T08:00:00Z"
        )
        assert len(historical["Items"]) == 3
