"""Tests for new Element controller methods."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.asset import ElementController


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    return client


@pytest.fixture
def controller(mock_client):
    """Create an ElementController with mock client."""
    return ElementController(mock_client)


class TestElementAnalyses:
    """Tests for analysis-related methods."""

    def test_get_analyses(self, controller, mock_client):
        """Test get analyses for element."""
        mock_client.get.return_value = {
            "Items": [{"Name": "Analysis1"}, {"Name": "Analysis2"}]
        }

        result = controller.get_analyses("F1Elem123", name_filter="*Temp*")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "elements/F1Elem123/analyses"
        assert call_args[1]["params"]["nameFilter"] == "*Temp*"

    def test_create_analysis(self, controller, mock_client):
        """Test create analysis on element."""
        analysis = {"Name": "NewAnalysis", "AnalysisRuleName": "Rule1"}
        mock_client.post.return_value = {"WebId": "F1Ana123"}

        result = controller.create_analysis("F1Elem123", analysis)

        mock_client.post.assert_called_once_with(
            "elements/F1Elem123/analyses",
            data=analysis
        )
        assert result["WebId"] == "F1Ana123"


class TestElementConfiguration:
    """Tests for configuration methods."""

    def test_create_config(self, controller, mock_client):
        """Test create element configuration."""
        mock_client.post.return_value = {}

        controller.create_config("F1Elem123", include_child_elements=True)

        mock_client.post.assert_called_once_with(
            "elements/F1Elem123/config",
            params={"includeChildElements": True}
        )

    def test_delete_config(self, controller, mock_client):
        """Test delete element configuration."""
        mock_client.delete.return_value = {}

        controller.delete_config("F1Elem123", include_child_elements=False)

        mock_client.delete.assert_called_once_with(
            "elements/F1Elem123/config",
            params={}
        )


class TestElementSearch:
    """Tests for search methods."""

    def test_find_element_attributes(self, controller, mock_client):
        """Test find element attributes with multiple filters."""
        mock_client.get.return_value = {"Items": []}

        result = controller.find_element_attributes(
            "F1Elem123",
            attribute_name_filter="Temp*",
            attribute_category="Process",
            element_name_filter="Tank*",
            search_full_hierarchy=True,
            max_count=500
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "elementattributes" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["attributeNameFilter"] == "Temp*"
        assert params["attributeCategory"] == "Process"
        assert params["searchFullHierarchy"] is True
        assert params["maxCount"] == 500


class TestElementEventFrames:
    """Tests for event frame methods."""

    def test_get_event_frames(self, controller, mock_client):
        """Test get event frames for element."""
        mock_client.get.return_value = {"Items": [{"Name": "Batch1"}]}

        result = controller.get_event_frames(
            "F1Elem123",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-02T00:00:00Z",
            category_name="Production",
            search_full_hierarchy=True
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "eventframes" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["startTime"] == "2025-01-01T00:00:00Z"
        assert params["endTime"] == "2025-01-02T00:00:00Z"
        assert params["categoryName"] == "Production"


class TestElementReferences:
    """Tests for referenced elements."""

    def test_get_referenced_elements(self, controller, mock_client):
        """Test get referenced elements."""
        mock_client.get.return_value = {
            "Items": [{"Name": "RefElement1"}, {"Name": "RefElement2"}]
        }

        result = controller.get_referenced_elements(
            "F1Elem123",
            category_name="Equipment",
            name_filter="Pump*",
            max_count=100
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "referencedelements" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["categoryName"] == "Equipment"
        assert params["nameFilter"] == "Pump*"
        assert params["maxCount"] == 100


class TestElementOtherMethods:
    """Tests for other new methods."""

    def test_get_categories(self, controller, mock_client):
        """Test get categories for element."""
        mock_client.get.return_value = {"Items": [{"Name": "Cat1"}]}

        result = controller.get_categories("F1Elem123")

        mock_client.get.assert_called_once_with(
            "elements/F1Elem123/categories",
            params={}
        )

    def test_get_notification_rule_subscribers(self, controller, mock_client):
        """Test get notification rule subscribers."""
        mock_client.get.return_value = {"Items": []}

        result = controller.get_notification_rule_subscribers("F1Elem123")

        mock_client.get.assert_called_once_with(
            "elements/F1Elem123/notificationrulesubscribers",
            params={}
        )

    def test_get_paths(self, controller, mock_client):
        """Test get element paths."""
        mock_client.get.return_value = {"Paths": ["Path1", "Path2"]}

        result = controller.get_paths("F1Elem123", relative_path="..\\Sibling")

        mock_client.get.assert_called_once_with(
            "elements/F1Elem123/paths",
            params={"relativePath": "..\\Sibling"}
        )


class TestElementSecurity:
    """Tests for security methods."""

    def test_get_security(self, controller, mock_client):
        """Test get security for element."""
        mock_client.get.return_value = {"CanRead": True, "CanWrite": False}

        result = controller.get_security(
            "F1Elem123",
            user_identity="DOMAIN\\User",
            force_refresh=True
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["userIdentity"] == "DOMAIN\\User"
        assert params["forceRefresh"] is True

    def test_get_security_entries(self, controller, mock_client):
        """Test get security entries."""
        mock_client.get.return_value = {"Items": []}

        result = controller.get_security_entries("F1Elem123", name_filter="Admin*")

        mock_client.get.assert_called_once()

    def test_create_security_entry_with_children(self, controller, mock_client):
        """Test create security entry with apply to children."""
        entry = {"Name": "Admin", "SecurityIdentityName": "DOMAIN\\Admin"}
        mock_client.post.return_value = {}

        controller.create_security_entry("F1Elem123", entry, apply_to_children=True)

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["params"]["applyToChildren"] is True

    def test_update_security_entry(self, controller, mock_client):
        """Test update security entry."""
        entry = {"AllowRead": True}
        mock_client.put.return_value = {}

        controller.update_security_entry(
            "F1Elem123",
            "Admin",
            entry,
            apply_to_children=False
        )

        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        assert "securityentries" in call_args[0][0]

    def test_delete_security_entry(self, controller, mock_client):
        """Test delete security entry."""
        mock_client.delete.return_value = {}

        controller.delete_security_entry("F1Elem123", "Admin", apply_to_children=True)

        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args
        assert call_args[1]["params"]["applyToChildren"] is True
