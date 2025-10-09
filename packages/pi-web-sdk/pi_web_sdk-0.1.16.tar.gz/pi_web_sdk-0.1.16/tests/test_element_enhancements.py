"""Tests for Element controller enhanced methods."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pi_web_sdk.controllers.asset import ElementController


@pytest.fixture
def mock_client():
    """Create a mock PIWebAPIClient."""
    return MagicMock()


@pytest.fixture
def element_controller(mock_client):
    """Create ElementController instance."""
    return ElementController(mock_client)


class TestElementControllerEnhancements:
    """Test Element controller new methods."""

    def test_add_referenced_element(self, element_controller, mock_client):
        """Test add referenced elements."""
        mock_client.post.return_value = {}

        result = element_controller.add_referenced_element(
            "E1",
            ["E2", "E3", "E4"]
        )

        assert result == {}
        mock_client.post.assert_called_once_with(
            "elements/E1/referencedelements",
            data=["E2", "E3", "E4"]
        )

    def test_add_referenced_element_single(self, element_controller, mock_client):
        """Test add single referenced element."""
        mock_client.post.return_value = {}

        result = element_controller.add_referenced_element("E1", ["E2"])

        assert result == {}
        mock_client.post.assert_called_once_with(
            "elements/E1/referencedelements",
            data=["E2"]
        )

    def test_remove_referenced_element(self, element_controller, mock_client):
        """Test remove referenced elements."""
        mock_client.delete.return_value = {}

        result = element_controller.remove_referenced_element(
            "E1",
            ["E2", "E3"]
        )

        assert result == {}
        mock_client.delete.assert_called_once_with(
            "elements/E1/referencedelements",
            data=["E2", "E3"]
        )

    def test_get_notification_rules(self, element_controller, mock_client):
        """Test get notification rules for element."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "NR1", "Name": "Rule1"},
                {"WebId": "NR2", "Name": "Rule2"},
            ]
        }

        result = element_controller.get_notification_rules("E1")

        assert len(result["Items"]) == 2
        assert result["Items"][0]["Name"] == "Rule1"
        mock_client.get.assert_called_once_with(
            "elements/E1/notificationrules",
            params={}
        )

    def test_get_notification_rules_with_fields(self, element_controller, mock_client):
        """Test get notification rules with selected fields."""
        mock_client.get.return_value = {
            "Items": [{"WebId": "NR1", "Name": "Rule1"}]
        }

        result = element_controller.get_notification_rules(
            "E1",
            selected_fields="WebId;Name"
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once_with(
            "elements/E1/notificationrules",
            params={"selectedFields": "WebId;Name"}
        )

    def test_create_notification_rule(self, element_controller, mock_client):
        """Test create notification rule."""
        mock_client.post.return_value = {"WebId": "NR1", "Name": "NewRule"}

        result = element_controller.create_notification_rule(
            "E1",
            {
                "Name": "NewRule",
                "Criteria": "Temperature > 100",
                "ContactTemplateWebId": "CT1"
            }
        )

        assert result["WebId"] == "NR1"
        assert result["Name"] == "NewRule"
        mock_client.post.assert_called_once_with(
            "elements/E1/notificationrules",
            data={
                "Name": "NewRule",
                "Criteria": "Temperature > 100",
                "ContactTemplateWebId": "CT1"
            }
        )

    def test_get_multiple(self, element_controller, mock_client):
        """Test get multiple elements."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E1", "Name": "Element1"},
                {"WebId": "E2", "Name": "Element2"},
                {"WebId": "E3", "Name": "Element3"},
            ]
        }

        result = element_controller.get_multiple(["E1", "E2", "E3"])

        assert len(result["Items"]) == 3
        assert result["Items"][0]["Name"] == "Element1"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "elements/multiple"
        assert call_args[1]["params"]["webId"] == ["E1", "E2", "E3"]

    def test_get_multiple_with_fields(self, element_controller, mock_client):
        """Test get multiple elements with selected fields."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E1", "Name": "Element1"},
                {"WebId": "E2", "Name": "Element2"},
            ]
        }

        result = element_controller.get_multiple(
            ["E1", "E2"],
            selected_fields="WebId;Name;Description"
        )

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["selectedFields"] == "WebId;Name;Description"

    def test_create_search_by_attribute(self, element_controller, mock_client):
        """Test create attribute search."""
        mock_client.post.return_value = {
            "SearchId": "S123",
            "Items": [
                {"WebId": "A1", "Name": "Attribute1"},
            ]
        }

        result = element_controller.create_search_by_attribute(
            "E1",
            "Name:='Temperature' Type:='Float64'"
        )

        assert result["SearchId"] == "S123"
        assert len(result["Items"]) == 1
        mock_client.post.assert_called_once_with(
            "elements/E1/searchattributes",
            params={"query": "Name:='Temperature' Type:='Float64'"}
        )

    def test_create_search_by_attribute_no_results(self, element_controller, mock_client):
        """Test create attribute search without results."""
        mock_client.post.return_value = {"SearchId": "S123"}

        result = element_controller.create_search_by_attribute(
            "E1",
            "Name:='Temperature'",
            no_results=True
        )

        assert result["SearchId"] == "S123"
        assert "Items" not in result
        mock_client.post.assert_called_once_with(
            "elements/E1/searchattributes",
            params={"query": "Name:='Temperature'", "noResults": True}
        )

    def test_execute_search_by_attribute(self, element_controller, mock_client):
        """Test execute attribute search."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "A1", "Name": "Temperature"},
                {"WebId": "A2", "Name": "Temp2"},
            ]
        }

        result = element_controller.execute_search_by_attribute("S123")

        assert len(result["Items"]) == 2
        assert result["Items"][0]["Name"] == "Temperature"
        mock_client.get.assert_called_once_with(
            "elements/searchattributes/S123",
            params={}
        )

    def test_execute_search_by_attribute_with_fields(self, element_controller, mock_client):
        """Test execute attribute search with selected fields."""
        mock_client.get.return_value = {
            "Items": [{"WebId": "A1", "Name": "Temperature"}]
        }

        result = element_controller.execute_search_by_attribute(
            "S123",
            selected_fields="WebId;Name;Type"
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once_with(
            "elements/searchattributes/S123",
            params={"selectedFields": "WebId;Name;Type"}
        )

    def test_get_elements_query(self, element_controller, mock_client):
        """Test query for child elements."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E2", "Name": "Pump1"},
                {"WebId": "E3", "Name": "Pump2"},
            ]
        }

        result = element_controller.get_elements_query(
            "E1",
            query="Name:='Pump*'"
        )

        assert len(result["Items"]) == 2
        assert result["Items"][0]["Name"] == "Pump1"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "elements/E1/elementsquery"
        assert call_args[1]["params"]["query"] == "Name:='Pump*'"
        assert call_args[1]["params"]["maxCount"] == 1000

    def test_get_elements_query_with_max_count(self, element_controller, mock_client):
        """Test query for child elements with max count."""
        mock_client.get.return_value = {
            "Items": [{"WebId": "E2", "Name": "Pump1"}]
        }

        result = element_controller.get_elements_query(
            "E1",
            query="Name:='Pump*'",
            max_count=50
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["maxCount"] == 50

    def test_get_elements_query_no_query(self, element_controller, mock_client):
        """Test query for child elements without query string."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E2", "Name": "Element2"},
                {"WebId": "E3", "Name": "Element3"},
            ]
        }

        result = element_controller.get_elements_query("E1")

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "query" not in call_args[1]["params"]
        assert call_args[1]["params"]["maxCount"] == 1000

    def test_get_elements_query_with_fields(self, element_controller, mock_client):
        """Test query for child elements with selected fields."""
        mock_client.get.return_value = {
            "Items": [{"WebId": "E2", "Name": "Pump1"}]
        }

        result = element_controller.get_elements_query(
            "E1",
            query="Name:='Pump*'",
            selected_fields="WebId;Name;Description"
        )

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["selectedFields"] == "WebId;Name;Description"


class TestElementReferencedElementsIntegration:
    """Test referenced elements add/remove workflow."""

    def test_add_and_remove_referenced_elements(self, element_controller, mock_client):
        """Test complete workflow of adding and removing referenced elements."""
        # Add references
        mock_client.post.return_value = {}
        element_controller.add_referenced_element("E1", ["E2", "E3"])
        
        # Get referenced elements
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E2", "Name": "RefElement2"},
                {"WebId": "E3", "Name": "RefElement3"},
            ]
        }
        result = element_controller.get_referenced_elements("E1")
        assert len(result["Items"]) == 2
        
        # Remove references
        mock_client.delete.return_value = {}
        element_controller.remove_referenced_element("E1", ["E2"])
        
        # Verify calls
        assert mock_client.post.call_count == 1
        assert mock_client.get.call_count == 1
        assert mock_client.delete.call_count == 1


class TestElementSearchWorkflow:
    """Test element search workflow."""

    def test_search_workflow(self, element_controller, mock_client):
        """Test complete search workflow."""
        # Create search
        mock_client.post.return_value = {"SearchId": "S123"}
        search = element_controller.create_search_by_attribute(
            "E1",
            "Name:='Temperature' Type:='Float64'",
            no_results=True
        )
        
        assert search["SearchId"] == "S123"
        
        # Execute search
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "A1", "Name": "Temperature", "Type": "Float64"},
                {"WebId": "A2", "Name": "Temperature2", "Type": "Float64"},
            ]
        }
        results = element_controller.execute_search_by_attribute("S123")
        
        assert len(results["Items"]) == 2
        assert all(attr["Type"] == "Float64" for attr in results["Items"])


class TestElementBulkOperations:
    """Test bulk element operations."""

    def test_get_multiple_large_set(self, element_controller, mock_client):
        """Test getting multiple elements with large set."""
        web_ids = [f"E{i}" for i in range(100)]
        mock_client.get.return_value = {
            "Items": [{"WebId": web_id, "Name": f"Element{i}"} 
                      for i, web_id in enumerate(web_ids)]
        }

        result = element_controller.get_multiple(web_ids)

        assert len(result["Items"]) == 100
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert len(call_args[1]["params"]["webId"]) == 100

    def test_get_multiple_with_optimization(self, element_controller, mock_client):
        """Test getting multiple elements with field optimization."""
        web_ids = ["E1", "E2", "E3"]
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "E1", "Name": "E1"},
                {"WebId": "E2", "Name": "E2"},
                {"WebId": "E3", "Name": "E3"},
            ]
        }

        # Only request needed fields to optimize response size
        result = element_controller.get_multiple(
            web_ids,
            selected_fields="WebId;Name"
        )

        assert len(result["Items"]) == 3
        mock_client.get.assert_called_once()
