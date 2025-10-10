"""Tests for create_pipoint_attribute method."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.asset import ElementController
from pi_web_sdk.models.attribute import Attribute, AttributeType
from pi_web_sdk.models.data import Point


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    return client


def test_create_pipoint_attribute_with_attribute_dataclass(mock_client):
    """Test create_pipoint_attribute with Attribute dataclass and Point dataclass."""
    controller = ElementController(mock_client)

    # Mock the response
    mock_client.post.return_value = {"WebId": "attr123", "Name": "Temperature"}

    # Create attribute and point instances
    attribute = Attribute(
        name="Temperature",
        description="Temperature sensor",
        type=AttributeType.DOUBLE.value,
    )

    point = Point(name="SensorTemp01")

    # Call the method
    result = controller.create_pipoint_attribute(
        element_web_id="elem123",
        attribute=attribute,
        point=point
    )

    # Verify the result
    assert result["WebId"] == "attr123"
    assert result["Name"] == "Temperature"

    # Verify the call was made with correct data
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "elements/elem123/attributes"

    # Check the data dict
    data = call_args[1]["data"]
    assert data["Name"] == "Temperature"
    assert data["Description"] == "Temperature sensor"
    assert data["Type"] == "Double"
    assert data["DataReferencePlugIn"] == "PI Point"
    assert data["ConfigString"] == "SensorTemp01"


def test_create_pipoint_attribute_with_point_string(mock_client):
    """Test create_pipoint_attribute with Attribute dataclass and point name string."""
    controller = ElementController(mock_client)

    # Mock the response
    mock_client.post.return_value = {"WebId": "attr123", "Name": "Pressure"}

    # Create attribute instance
    attribute = Attribute(
        name="Pressure",
        type=AttributeType.DOUBLE.value,
    )

    # Call the method with string point name
    result = controller.create_pipoint_attribute(
        element_web_id="elem123",
        attribute=attribute,
        point="SensorPressure01"
    )

    # Verify the result
    assert result["WebId"] == "attr123"

    # Verify the call
    call_args = mock_client.post.call_args
    data = call_args[1]["data"]
    assert data["DataReferencePlugIn"] == "PI Point"
    assert data["ConfigString"] == "SensorPressure01"


def test_create_pipoint_attribute_with_dicts(mock_client):
    """Test create_pipoint_attribute with dictionaries."""
    controller = ElementController(mock_client)

    # Mock the response
    mock_client.post.return_value = {"WebId": "attr123", "Name": "Flow"}

    # Create attribute and point dicts
    attribute = {
        "Name": "Flow",
        "Type": "Double",
    }

    point = {
        "Name": "FlowSensor01"
    }

    # Call the method
    result = controller.create_pipoint_attribute(
        element_web_id="elem123",
        attribute=attribute,
        point=point
    )

    # Verify the result
    assert result["WebId"] == "attr123"

    # Verify the call
    call_args = mock_client.post.call_args
    data = call_args[1]["data"]
    assert data["DataReferencePlugIn"] == "PI Point"
    assert data["ConfigString"] == "FlowSensor01"


def test_create_pipoint_attribute_with_point_dict_lowercase_name(mock_client):
    """Test create_pipoint_attribute with point dict using lowercase 'name' key."""
    controller = ElementController(mock_client)

    # Mock the response
    mock_client.post.return_value = {"WebId": "attr123", "Name": "Level"}

    # Create attribute and point with lowercase name
    attribute = Attribute(name="Level", type=AttributeType.DOUBLE.value)
    point = {"name": "LevelSensor01"}  # lowercase 'name'

    # Call the method
    result = controller.create_pipoint_attribute(
        element_web_id="elem123",
        attribute=attribute,
        point=point
    )

    # Verify the call
    call_args = mock_client.post.call_args
    data = call_args[1]["data"]
    assert data["ConfigString"] == "LevelSensor01"


def test_create_pipoint_attribute_with_initial_value(mock_client):
    """Test create_pipoint_attribute with initial value."""
    controller = ElementController(mock_client)

    # Mock the response
    mock_client.post.return_value = {"WebId": "attr123", "Name": "Temperature"}

    # Create attribute and point
    attribute = Attribute(name="Temperature", type=AttributeType.DOUBLE.value)
    point = "TempSensor01"

    # Call the method with initial value
    result = controller.create_pipoint_attribute(
        element_web_id="elem123",
        attribute=attribute,
        point=point,
        value=25.5
    )

    # Verify the attribute was created
    assert result["WebId"] == "attr123"

    # Verify post was called for attribute creation
    assert mock_client.post.called


def test_create_pipoint_attribute_point_dict_missing_name_raises_error(mock_client):
    """Test that point dict without 'Name' or 'name' raises ValueError."""
    controller = ElementController(mock_client)

    attribute = Attribute(name="Test", type=AttributeType.DOUBLE.value)
    point = {"invalid_key": "value"}  # Missing 'Name' or 'name'

    with pytest.raises(ValueError, match="Point dictionary must contain 'Name' or 'name' field"):
        controller.create_pipoint_attribute(
            element_web_id="elem123",
            attribute=attribute,
            point=point
        )


def test_create_pipoint_attribute_invalid_point_type_raises_error(mock_client):
    """Test that invalid point type raises TypeError."""
    controller = ElementController(mock_client)

    attribute = Attribute(name="Test", type=AttributeType.DOUBLE.value)

    with pytest.raises(TypeError, match="point must be Point, dict, or str"):
        controller.create_pipoint_attribute(
            element_web_id="elem123",
            attribute=attribute,
            point=123  # Invalid type
        )