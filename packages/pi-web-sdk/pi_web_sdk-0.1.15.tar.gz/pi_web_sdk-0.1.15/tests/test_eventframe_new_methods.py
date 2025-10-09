"""Tests for new EventFrame controller methods."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.event import EventFrameController


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    return client


@pytest.fixture
def controller(mock_client):
    """Create an EventFrameController with mock client."""
    return EventFrameController(mock_client)


class TestEventFrameAcknowledge:
    """Tests for acknowledge method."""

    def test_acknowledge(self, controller, mock_client):
        """Test acknowledge event frame."""
        mock_client.patch.return_value = {}

        controller.acknowledge("F1EF123")

        mock_client.patch.assert_called_once_with("eventframes/F1EF123/acknowledge")


class TestEventFrameAnnotations:
    """Tests for annotation methods."""

    def test_get_annotations(self, controller, mock_client):
        """Test get annotations for event frame."""
        mock_client.get.return_value = {
            "Items": [
                {"Id": "1", "Value": "Note 1"},
                {"Id": "2", "Value": "Note 2"}
            ]
        }

        result = controller.get_annotations("F1EF123")

        mock_client.get.assert_called_once_with(
            "eventframes/F1EF123/annotations",
            params={}
        )
        assert len(result["Items"]) == 2

    def test_create_annotation(self, controller, mock_client):
        """Test create annotation."""
        annotation = {
            "Name": "MyNote",
            "Value": "Important observation",
            "CreationDate": "2025-01-01T00:00:00Z"
        }
        mock_client.post.return_value = {"Id": "123"}

        result = controller.create_annotation("F1EF123", annotation)

        mock_client.post.assert_called_once_with(
            "eventframes/F1EF123/annotations",
            data=annotation
        )
        assert result["Id"] == "123"

    def test_get_annotation_by_id(self, controller, mock_client):
        """Test get specific annotation by ID."""
        mock_client.get.return_value = {"Id": "123", "Value": "Note"}

        result = controller.get_annotation_by_id("F1EF123", "123")

        mock_client.get.assert_called_once_with(
            "eventframes/F1EF123/annotations/123",
            params={}
        )

    def test_update_annotation(self, controller, mock_client):
        """Test update annotation."""
        annotation = {"Value": "Updated note"}
        mock_client.patch.return_value = {}

        controller.update_annotation("F1EF123", "123", annotation)

        mock_client.patch.assert_called_once_with(
            "eventframes/F1EF123/annotations/123",
            data=annotation
        )

    def test_delete_annotation(self, controller, mock_client):
        """Test delete annotation."""
        mock_client.delete.return_value = {}

        controller.delete_annotation("F1EF123", "123")

        mock_client.delete.assert_called_once_with(
            "eventframes/F1EF123/annotations/123"
        )


class TestEventFrameOtherMethods:
    """Tests for other new methods."""

    def test_get_categories(self, controller, mock_client):
        """Test get categories for event frame."""
        mock_client.get.return_value = {"Items": [{"Name": "Production"}]}

        result = controller.get_categories("F1EF123")

        mock_client.get.assert_called_once_with(
            "eventframes/F1EF123/categories",
            params={}
        )

    def test_capture_values(self, controller, mock_client):
        """Test capture event frame values."""
        mock_client.post.return_value = {}

        controller.capture_values("F1EF123")

        mock_client.post.assert_called_once_with(
            "eventframes/F1EF123/capturevalues"
        )


class TestEventFrameSearch:
    """Tests for search methods."""

    def test_find_event_frame_attributes(self, controller, mock_client):
        """Test find event frame attributes with multiple filters."""
        mock_client.get.return_value = {"Items": []}

        result = controller.find_event_frame_attributes(
            "F1EF123",
            attribute_name_filter="Temp*",
            event_frame_name_filter="Batch*",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-02T00:00:00Z",
            search_full_hierarchy=True,
            max_count=500
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "eventframeattributes" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["attributeNameFilter"] == "Temp*"
        assert params["eventFrameNameFilter"] == "Batch*"
        assert params["startTime"] == "2025-01-01T00:00:00Z"
        assert params["searchFullHierarchy"] is True


class TestEventFrameReferences:
    """Tests for referenced elements."""

    def test_get_referenced_elements(self, controller, mock_client):
        """Test get referenced elements."""
        mock_client.get.return_value = {
            "Items": [{"Name": "Tank1"}, {"Name": "Pump1"}]
        }

        result = controller.get_referenced_elements("F1EF123")

        mock_client.get.assert_called_once_with(
            "eventframes/F1EF123/referencedelements",
            params={}
        )
        assert len(result["Items"]) == 2


class TestEventFrameSecurity:
    """Tests for security methods."""

    def test_get_security(self, controller, mock_client):
        """Test get security for event frame."""
        mock_client.get.return_value = {"CanRead": True, "CanWrite": True}

        result = controller.get_security(
            "F1EF123",
            user_identity="DOMAIN\\User",
            force_refresh=True
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "security" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["userIdentity"] == "DOMAIN\\User"
        assert params["forceRefresh"] is True

    def test_get_security_entries(self, controller, mock_client):
        """Test get security entries."""
        mock_client.get.return_value = {"Items": []}

        result = controller.get_security_entries("F1EF123", name_filter="Admin*")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "securityentries" in call_args[0][0]

    def test_get_security_entry_by_name(self, controller, mock_client):
        """Test get security entry by name."""
        mock_client.get.return_value = {"Name": "Admin"}

        result = controller.get_security_entry_by_name("F1EF123", "Admin")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "securityentries" in call_args[0][0]

    def test_create_security_entry_with_children(self, controller, mock_client):
        """Test create security entry with apply to children."""
        entry = {"Name": "Admin", "SecurityIdentityName": "DOMAIN\\Admin"}
        mock_client.post.return_value = {}

        controller.create_security_entry("F1EF123", entry, apply_to_children=True)

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["params"]["applyToChildren"] is True

    def test_update_security_entry_without_children(self, controller, mock_client):
        """Test update security entry without apply to children."""
        entry = {"AllowRead": True, "AllowWrite": False}
        mock_client.put.return_value = {}

        controller.update_security_entry("F1EF123", "Admin", entry, apply_to_children=False)

        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        assert "securityentries" in call_args[0][0]
        assert call_args[1]["params"] == {}

    def test_delete_security_entry(self, controller, mock_client):
        """Test delete security entry."""
        mock_client.delete.return_value = {}

        controller.delete_security_entry("F1EF123", "Admin", apply_to_children=True)

        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args
        assert "securityentries" in call_args[0][0]
        assert call_args[1]["params"]["applyToChildren"] is True
