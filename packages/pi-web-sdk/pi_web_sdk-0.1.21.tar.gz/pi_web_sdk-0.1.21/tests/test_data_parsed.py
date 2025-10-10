"""Tests for parsed data controller methods."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pi_web_sdk.controllers.data import DataServerController, PointController
from pi_web_sdk.models.data import DataServer, Point
from pi_web_sdk.models.responses import ItemsResponse


@pytest.fixture
def mock_client():
    """Create a mock PIWebAPIClient."""
    return MagicMock()


@pytest.fixture
def data_server_controller(mock_client):
    """Create DataServerController instance."""
    return DataServerController(mock_client)


@pytest.fixture
def point_controller(mock_client):
    """Create PointController instance."""
    return PointController(mock_client)


class TestDataServerControllerParsed:
    """Test DataServerController parsed methods."""

    def test_list_parsed(self, data_server_controller, mock_client):
        """Test list_parsed returns ItemsResponse with DataServer objects."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "F1DSw123",
                    "Id": "abc-123",
                    "Name": "PISERVER1",
                    "Description": "Production PI Server",
                    "Path": r"\\PISERVER1",
                    "ServerVersion": "3.4.450.1",
                    "IsConnected": True,
                },
                {
                    "WebId": "F1DSw456",
                    "Id": "def-456",
                    "Name": "PISERVER2",
                    "Description": "Development PI Server",
                    "Path": r"\\PISERVER2",
                    "ServerVersion": "3.4.450.1",
                    "IsConnected": False,
                },
            ],
            "Links": {},
        }

        # Act
        result = data_server_controller.list_parsed()

        # Assert
        assert isinstance(result, ItemsResponse)
        assert len(result) == 2
        assert all(isinstance(item, DataServer) for item in result)
        assert result[0].name == "PISERVER1"
        assert result[0].server_version == "3.4.450.1"
        assert result[0].is_connected is True
        assert result[1].name == "PISERVER2"
        assert result[1].is_connected is False

    def test_get_parsed(self, data_server_controller, mock_client):
        """Test get_parsed returns DataServer object."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DSw123",
            "Id": "abc-123",
            "Name": "PISERVER1",
            "Description": "Production PI Server",
            "Path": r"\\PISERVER1",
            "ServerVersion": "3.4.450.1",
            "IsConnected": True,
            "ServerTime": "2024-01-15T10:30:00Z",
        }

        # Act
        result = data_server_controller.get_parsed("F1DSw123")

        # Assert
        assert isinstance(result, DataServer)
        assert result.web_id == "F1DSw123"
        assert result.name == "PISERVER1"
        assert result.server_version == "3.4.450.1"
        assert result.is_connected is True
        assert result.server_time == "2024-01-15T10:30:00Z"
        mock_client.get.assert_called_once_with("dataservers/F1DSw123", params={})

    def test_get_by_name_parsed(self, data_server_controller, mock_client):
        """Test get_by_name_parsed returns DataServer object."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DSw123",
            "Name": "PISERVER1",
            "Path": r"\\PISERVER1",
            "ServerVersion": "3.4.450.1",
            "IsConnected": True,
        }

        # Act
        result = data_server_controller.get_by_name_parsed("PISERVER1")

        # Assert
        assert isinstance(result, DataServer)
        assert result.name == "PISERVER1"
        assert result.server_version == "3.4.450.1"

    def test_get_by_path_parsed(self, data_server_controller, mock_client):
        """Test get_by_path_parsed returns DataServer object."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DSw123",
            "Name": "PISERVER1",
            "Path": r"\\PISERVER1",
            "ServerVersion": "3.4.450.1",
            "IsConnected": True,
        }

        # Act
        result = data_server_controller.get_by_path_parsed(r"\\PISERVER1")

        # Assert
        assert isinstance(result, DataServer)
        assert result.path == r"\\PISERVER1"
        assert result.name == "PISERVER1"

    def test_get_points_parsed(self, data_server_controller, mock_client):
        """Test get_points_parsed returns ItemsResponse with Point objects."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [
                {
                    "WebId": "F1DPw111",
                    "Name": "sinusoid",
                    "Path": r"\\PISERVER1\sinusoid",
                    "PointClass": "classic",
                    "PointType": "Float32",
                    "EngineeringUnits": "degC",
                    "Step": False,
                    "DisplayDigits": 2,
                },
                {
                    "WebId": "F1DPw222",
                    "Name": "temperature",
                    "Path": r"\\PISERVER1\temperature",
                    "PointClass": "classic",
                    "PointType": "Float64",
                    "EngineeringUnits": "degF",
                    "Step": True,
                    "DisplayDigits": 1,
                },
            ],
            "Links": {},
        }

        # Act
        result = data_server_controller.get_points_parsed("F1DSw123", name_filter="*temp*")

        # Assert
        assert isinstance(result, ItemsResponse)
        assert len(result) == 2
        assert all(isinstance(item, Point) for item in result)
        assert result[0].name == "sinusoid"
        assert result[0].engineering_units == "degC"
        assert result[0].point_type == "Float32"
        assert result[0].step is False
        assert result[1].name == "temperature"
        assert result[1].engineering_units == "degF"

    def test_get_points_parsed_iteration(self, data_server_controller, mock_client):
        """Test ItemsResponse can be iterated."""
        # Arrange
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "P1", "Name": "Point1", "PointType": "Float32"},
                {"WebId": "P2", "Name": "Point2", "PointType": "Float64"},
                {"WebId": "P3", "Name": "Point3", "PointType": "Int32"},
            ],
        }

        # Act
        result = data_server_controller.get_points_parsed("F1DSw123")
        names = [point.name for point in result]

        # Assert
        assert names == ["Point1", "Point2", "Point3"]


class TestPointControllerParsed:
    """Test PointController parsed methods."""

    def test_get_parsed(self, point_controller, mock_client):
        """Test get_parsed returns Point object."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DPw111",
            "Id": "123",
            "Name": "sinusoid",
            "Description": "Sine wave test point",
            "Path": r"\\PISERVER1\sinusoid",
            "PointClass": "classic",
            "PointType": "Float32",
            "EngineeringUnits": "degC",
            "Step": False,
            "Future": False,
            "DisplayDigits": 2,
        }

        # Act
        result = point_controller.get_parsed("F1DPw111")

        # Assert
        assert isinstance(result, Point)
        assert result.web_id == "F1DPw111"
        assert result.name == "sinusoid"
        assert result.description == "Sine wave test point"
        assert result.point_type == "Float32"
        assert result.engineering_units == "degC"
        assert result.step is False
        assert result.display_digits == 2
        mock_client.get.assert_called_once_with("points/F1DPw111", params={})

    def test_get_by_path_parsed(self, point_controller, mock_client):
        """Test get_by_path_parsed returns Point object."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DPw111",
            "Name": "sinusoid",
            "Path": r"\\PISERVER1\sinusoid",
            "PointType": "Float32",
            "EngineeringUnits": "degC",
        }

        # Act
        result = point_controller.get_by_path_parsed(r"\\PISERVER1\sinusoid")

        # Assert
        assert isinstance(result, Point)
        assert result.name == "sinusoid"
        assert result.path == r"\\PISERVER1\sinusoid"
        assert result.point_type == "Float32"

    def test_get_parsed_with_selected_fields(self, point_controller, mock_client):
        """Test get_parsed with selected_fields parameter."""
        # Arrange
        mock_client.get.return_value = {
            "WebId": "F1DPw111",
            "Name": "sinusoid",
            "PointType": "Float32",
        }

        # Act
        result = point_controller.get_parsed("F1DPw111", selected_fields="WebId;Name;PointType")

        # Assert
        assert isinstance(result, Point)
        assert result.name == "sinusoid"
        mock_client.get.assert_called_once_with(
            "points/F1DPw111",
            params={"selectedFields": "WebId;Name;PointType"}
        )


class TestItemsResponse:
    """Test ItemsResponse functionality."""

    def test_items_response_indexing(self):
        """Test ItemsResponse supports indexing."""
        # Arrange
        items = [
            DataServer(web_id="S1", name="Server1"),
            DataServer(web_id="S2", name="Server2"),
            DataServer(web_id="S3", name="Server3"),
        ]
        response = ItemsResponse(items=items)

        # Act & Assert
        assert response[0].name == "Server1"
        assert response[1].name == "Server2"
        assert response[2].name == "Server3"

    def test_items_response_length(self):
        """Test ItemsResponse supports len()."""
        # Arrange
        items = [DataServer(web_id=f"S{i}", name=f"Server{i}") for i in range(5)]
        response = ItemsResponse(items=items)

        # Act & Assert
        assert len(response) == 5

    def test_items_response_iteration(self):
        """Test ItemsResponse is iterable."""
        # Arrange
        items = [
            DataServer(web_id="S1", name="Server1"),
            DataServer(web_id="S2", name="Server2"),
        ]
        response = ItemsResponse(items=items)

        # Act
        names = [server.name for server in response]

        # Assert
        assert names == ["Server1", "Server2"]

    def test_items_response_empty(self):
        """Test ItemsResponse with empty items list."""
        # Arrange
        response = ItemsResponse(items=[])

        # Act & Assert
        assert len(response) == 0
        assert list(response) == []
