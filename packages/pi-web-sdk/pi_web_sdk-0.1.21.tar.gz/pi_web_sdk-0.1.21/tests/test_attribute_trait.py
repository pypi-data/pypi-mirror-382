"""Tests for AttributeTrait controller."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.attribute_trait import AttributeTraitController


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    return client


@pytest.fixture
def controller(mock_client):
    """Create an AttributeTraitController with mock client."""
    return AttributeTraitController(mock_client)


def test_get(controller, mock_client):
    """Test get attribute trait by WebID."""
    mock_client.get.return_value = {
        "WebId": "F1AbTr123",
        "Name": "Limit",
        "Description": "Limit trait"
    }

    result = controller.get("F1AbTr123", selected_fields="Name;Description")

    mock_client.get.assert_called_once_with(
        "attributetraits/F1AbTr123",
        params={"selectedFields": "Name;Description"}
    )
    assert result["WebId"] == "F1AbTr123"
    assert result["Name"] == "Limit"


def test_get_without_selected_fields(controller, mock_client):
    """Test get without selected fields."""
    mock_client.get.return_value = {"WebId": "F1AbTr123"}

    result = controller.get("F1AbTr123")

    mock_client.get.assert_called_once_with("attributetraits/F1AbTr123", params={})
    assert result["WebId"] == "F1AbTr123"


def test_get_by_name(controller, mock_client):
    """Test get attribute trait by name."""
    mock_client.get.return_value = {
        "WebId": "F1AbTr123",
        "Name": "Limit"
    }

    result = controller.get_by_name("Limit")

    mock_client.get.assert_called_once_with(
        "attributetraits",
        params={"name": "Limit"}
    )
    assert result["Name"] == "Limit"


def test_get_by_name_with_selected_fields(controller, mock_client):
    """Test get by name with selected fields."""
    mock_client.get.return_value = {"WebId": "F1AbTr123", "Name": "Limit"}

    result = controller.get_by_name("Limit", selected_fields="WebId;Name")

    mock_client.get.assert_called_once_with(
        "attributetraits",
        params={"name": "Limit", "selectedFields": "WebId;Name"}
    )


def test_get_categories(controller, mock_client):
    """Test get categories for attribute trait."""
    mock_client.get.return_value = {
        "Items": [
            {"Name": "Category1"},
            {"Name": "Category2"}
        ]
    }

    result = controller.get_categories("F1AbTr123")

    mock_client.get.assert_called_once_with(
        "attributetraits/F1AbTr123/categories",
        params={}
    )
    assert len(result["Items"]) == 2


def test_get_categories_with_selected_fields(controller, mock_client):
    """Test get categories with selected fields."""
    mock_client.get.return_value = {"Items": []}

    result = controller.get_categories("F1AbTr123", selected_fields="Name;Description")

    mock_client.get.assert_called_once_with(
        "attributetraits/F1AbTr123/categories",
        params={"selectedFields": "Name;Description"}
    )
