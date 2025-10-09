"""Tests for OMF ORM system with dataclasses."""

import pytest
from datetime import datetime, timezone
from pi_web_sdk.models.omf import (
    OMFType, OMFProperty, OMFContainer, OMFAsset, OMFTimeSeriesData, OMFBatch,
    Classification, PropertyType, OMFAction, OMFMessageType,
    create_temperature_sensor_type, create_equipment_asset_type
)
from pi_web_sdk.controllers.omf import OMFManager


class TestOMFProperty:
    """Test OMF Property dataclass."""
    
    def test_basic_property_creation(self):
        """Test creating a basic property."""
        prop = OMFProperty(
            type=PropertyType.NUMBER,
            description="Temperature value"
        )
        
        result = prop.to_dict()
        assert result["type"] == "number"
        assert result["description"] == "Temperature value"
        assert "isindex" not in result
    
    def test_index_property(self):
        """Test creating an index property."""
        prop = OMFProperty(
            type=PropertyType.STRING,
            format="date-time",
            is_index=True
        )
        
        result = prop.to_dict()
        assert result["type"] == "string"
        assert result["format"] == "date-time"
        assert result["isindex"] is True


class TestOMFType:
    """Test OMF Type dataclass."""
    
    def test_dynamic_type_creation(self):
        """Test creating a dynamic type."""
        properties = {
            "timestamp": OMFProperty(
                type=PropertyType.STRING,
                format="date-time",
                is_index=True
            ),
            "value": OMFProperty(
                type=PropertyType.NUMBER,
                description="Sensor value"
            )
        }
        
        omf_type = OMFType(
            id="TestSensorType",
            classification=Classification.DYNAMIC,
            properties=properties,
            description="Test sensor type"
        )
        
        result = omf_type.to_dict()
        assert result["id"] == "TestSensorType"
        assert result["type"] == "object"
        assert result["classification"] == "dynamic"
        assert result["description"] == "Test sensor type"
        assert "timestamp" in result["properties"]
        assert "value" in result["properties"]
    
    def test_static_type_creation(self):
        """Test creating a static type."""
        properties = {
            "name": OMFProperty(
                type=PropertyType.STRING,
                is_index=True
            ),
            "location": OMFProperty(
                type=PropertyType.STRING,
                description="Asset location"
            )
        }
        
        omf_type = OMFType(
            id="TestAssetType",
            classification=Classification.STATIC,
            properties=properties
        )
        
        result = omf_type.to_dict()
        assert result["id"] == "TestAssetType"
        assert result["classification"] == "static"
        assert "name" in result["properties"]
        assert "location" in result["properties"]
    
    def test_create_dynamic_type_helper(self):
        """Test the create_dynamic_type helper method."""
        additional_props = {
            "temperature": OMFProperty(
                type=PropertyType.NUMBER,
                description="Temperature in Celsius"
            )
        }
        
        omf_type = OMFType.create_dynamic_type(
            id="SensorType",
            additional_properties=additional_props,
            description="Temperature sensor"
        )
        
        assert omf_type.id == "SensorType"
        assert omf_type.classification == Classification.DYNAMIC
        assert "timestamp" in omf_type.properties
        assert "temperature" in omf_type.properties
        assert omf_type.properties["timestamp"].is_index
    
    def test_create_static_type_helper(self):
        """Test the create_static_type helper method."""
        additional_props = {
            "model": OMFProperty(
                type=PropertyType.STRING,
                description="Equipment model"
            )
        }
        
        omf_type = OMFType.create_static_type(
            id="EquipmentType",
            additional_properties=additional_props,
            description="Equipment asset"
        )
        
        assert omf_type.id == "EquipmentType"
        assert omf_type.classification == Classification.STATIC
        assert "name" in omf_type.properties
        assert "model" in omf_type.properties
        assert omf_type.properties["name"].is_index
    
    def test_dynamic_type_validation(self):
        """Test validation for dynamic types."""
        # Should fail without index property
        properties = {
            "value": OMFProperty(type=PropertyType.NUMBER)
        }
        
        with pytest.raises(ValueError, match="Dynamic types must have at least one index property"):
            OMFType(
                id="InvalidType",
                classification=Classification.DYNAMIC,
                properties=properties
            )
    
    def test_static_type_validation(self):
        """Test validation for static types."""
        # Should fail without index or name property
        properties = {
            "value": OMFProperty(type=PropertyType.NUMBER)
        }
        
        with pytest.raises(ValueError, match="Static types must have at least one index or name property"):
            OMFType(
                id="InvalidType",
                classification=Classification.STATIC,
                properties=properties
            )


class TestOMFContainer:
    """Test OMF Container dataclass."""
    
    def test_basic_container(self):
        """Test creating a basic container."""
        container = OMFContainer(
            id="TestContainer",
            type_id="TestType",
            name="Test Container",
            description="Test container description"
        )
        
        result = container.to_dict()
        assert result["id"] == "TestContainer"
        assert result["typeid"] == "TestType"
        assert result["name"] == "Test Container"
        assert result["description"] == "Test container description"
    
    def test_container_with_metadata(self):
        """Test container with tags and metadata."""
        container = OMFContainer(
            id="TestContainer",
            type_id="TestType",
            tags={"location": "Building A", "floor": "2"},
            metadata={"sensor_model": "TH-3000"}
        )
        
        result = container.to_dict()
        assert result["tags"]["location"] == "Building A"
        assert result["metadata"]["sensor_model"] == "TH-3000"


class TestOMFAsset:
    """Test OMF Asset dataclass."""
    
    def test_basic_asset(self):
        """Test creating a basic asset."""
        asset = OMFAsset(
            type_id="EquipmentType",
            values=[
                {
                    "name": "Pump001",
                    "location": "Building A",
                    "model": "XYZ-123"
                }
            ]
        )
        
        result = asset.to_dict()
        assert result["typeid"] == "EquipmentType"
        assert len(result["values"]) == 1
        assert result["values"][0]["name"] == "Pump001"
    
    def test_create_single_asset_helper(self):
        """Test the create_single_asset helper method."""
        asset = OMFAsset.create_single_asset(
            type_id="EquipmentType",
            name="Sensor001",
            location="Room 101",
            manufacturer="ACME Corp"
        )
        
        result = asset.to_dict()
        assert result["typeid"] == "EquipmentType"
        assert len(result["values"]) == 1
        assert result["values"][0]["name"] == "Sensor001"
        assert result["values"][0]["location"] == "Room 101"
        assert result["values"][0]["manufacturer"] == "ACME Corp"


class TestOMFTimeSeriesData:
    """Test OMF Time Series Data dataclass."""
    
    def test_basic_time_series(self):
        """Test creating basic time series data."""
        ts_data = OMFTimeSeriesData(
            container_id="Sensor001",
            values=[
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "temperature": 25.5,
                    "humidity": 60.0
                }
            ]
        )
        
        result = ts_data.to_dict()
        assert result["containerid"] == "Sensor001"
        assert len(result["values"]) == 1
        assert result["values"][0]["temperature"] == 25.5
    
    def test_add_data_point(self):
        """Test adding data points."""
        ts_data = OMFTimeSeriesData(
            container_id="Sensor001",
            values=[]
        )
        
        ts_data.add_data_point(temperature=25.5, humidity=60.0)
        
        assert len(ts_data.values) == 1
        assert "timestamp" in ts_data.values[0]
        assert ts_data.values[0]["temperature"] == 25.5
    
    def test_add_data_points(self):
        """Test adding multiple data points."""
        ts_data = OMFTimeSeriesData(
            container_id="Sensor001",
            values=[]
        )
        
        data_points = [
            {"temperature": 25.5, "humidity": 60.0},
            {"temperature": 26.0, "humidity": 58.0}
        ]
        
        ts_data.add_data_points(data_points)
        
        assert len(ts_data.values) == 2
        assert "timestamp" in ts_data.values[0]
        assert "timestamp" in ts_data.values[1]


class TestOMFBatch:
    """Test OMF Batch dataclass."""
    
    def test_empty_batch(self):
        """Test creating an empty batch."""
        batch = OMFBatch()
        
        assert len(batch.types) == 0
        assert len(batch.containers) == 0
        assert len(batch.assets) == 0
        assert len(batch.time_series) == 0
    
    def test_batch_operations(self):
        """Test batch operations."""
        batch = OMFBatch()
        
        # Add type
        omf_type = OMFType.create_dynamic_type("TestType")
        batch.add_type(omf_type)
        
        # Add container
        container = OMFContainer("TestContainer", "TestType")
        batch.add_container(container)
        
        # Add asset
        asset = OMFAsset.create_single_asset("AssetType", name="Asset001")
        batch.add_asset(asset)
        
        # Add time series
        ts_data = OMFTimeSeriesData("TestContainer", [])
        batch.add_time_series(ts_data)
        
        assert len(batch.types) == 1
        assert len(batch.containers) == 1
        assert len(batch.assets) == 1
        assert len(batch.time_series) == 1
    
    def test_batch_message_generation(self):
        """Test generating messages from batch."""
        batch = OMFBatch()
        
        # Add items
        omf_type = OMFType.create_dynamic_type("TestType")
        batch.add_type(omf_type)
        
        container = OMFContainer("TestContainer", "TestType")
        batch.add_container(container)
        
        asset = OMFAsset.create_single_asset("AssetType", name="Asset001")
        batch.add_asset(asset)
        
        ts_data = OMFTimeSeriesData("TestContainer", [{"value": 42}])
        batch.add_time_series(ts_data)
        
        # Test message generation
        type_messages = batch.get_type_messages()
        container_messages = batch.get_container_messages()
        data_messages = batch.get_data_messages()
        
        assert len(type_messages) == 1
        assert len(container_messages) == 1
        assert len(data_messages) == 2  # Asset + time series
        
        assert type_messages[0]["id"] == "TestType"
        assert container_messages[0]["id"] == "TestContainer"
    
    def test_batch_clear(self):
        """Test clearing batch."""
        batch = OMFBatch()
        
        # Add items
        batch.add_type(OMFType.create_dynamic_type("TestType"))
        batch.add_container(OMFContainer("TestContainer", "TestType"))
        
        assert len(batch.types) == 1
        assert len(batch.containers) == 1
        
        batch.clear()
        
        assert len(batch.types) == 0
        assert len(batch.containers) == 0


class TestConvenienceFunctions:
    """Test convenience factory functions."""
    
    def test_create_temperature_sensor_type(self):
        """Test temperature sensor type creation."""
        sensor_type = create_temperature_sensor_type("TempSensor001")
        
        assert sensor_type.id == "TempSensor001"
        assert sensor_type.classification == Classification.DYNAMIC
        assert "timestamp" in sensor_type.properties
        assert "temperature" in sensor_type.properties
        assert "humidity" in sensor_type.properties
        assert "quality" in sensor_type.properties
    
    def test_create_equipment_asset_type(self):
        """Test equipment asset type creation."""
        asset_type = create_equipment_asset_type("Equipment001")
        
        assert asset_type.id == "Equipment001"
        assert asset_type.classification == Classification.STATIC
        assert "name" in asset_type.properties
        assert "location" in asset_type.properties
        assert "manufacturer" in asset_type.properties
        assert "model" in asset_type.properties
        assert "serialNumber" in asset_type.properties
        assert "installDate" in asset_type.properties


class TestOMFManager:
    """Test OMF Manager integration."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        class MockOMFController:
            def post_async(self, **kwargs):
                return {"status": "success", "kwargs": kwargs}
        
        class MockDataServerController:
            def list(self):
                return {
                    "Items": [
                        {"WebId": "test-server-id", "Name": "Test Server"}
                    ]
                }
            
            def get(self, web_id):
                return {"WebId": web_id, "Name": "Test Server"}
        
        class MockClient:
            def __init__(self):
                self.omf = MockOMFController()
                self.data_server = MockDataServerController()
        
        return MockClient()
    
    def test_omf_manager_creation(self, mock_client):
        """Test creating OMF manager."""
        manager = OMFManager(mock_client)
        
        assert manager.client is mock_client
        assert manager.data_server_web_id == "test-server-id"
        assert manager.omf_version == "1.2"
    
    def test_create_type_with_manager(self, mock_client):
        """Test creating type with manager."""
        manager = OMFManager(mock_client)
        
        omf_type = create_temperature_sensor_type("TempSensor")
        result = manager.create_type(omf_type)
        
        assert result["status"] == "success"
        assert result["kwargs"]["message_type"] == "Type"
        assert result["kwargs"]["action"] == "create"
    
    def test_send_single_data_point(self, mock_client):
        """Test sending single data point."""
        manager = OMFManager(mock_client)
        
        result = manager.send_single_data_point(
            "TestSensor",
            temperature=25.5,
            humidity=60.0
        )
        
        assert result["status"] == "success"
        assert result["kwargs"]["message_type"] == "Data"
    
    def test_complete_sensor_setup(self, mock_client):
        """Test complete sensor setup."""
        manager = OMFManager(mock_client)
        
        sensor_type = create_temperature_sensor_type("TempSensor")
        
        results = manager.create_complete_sensor_setup(
            sensor_id="Sensor001",
            sensor_name="Room Temperature Sensor",
            sensor_type=sensor_type,
            initial_data=[{"temperature": 25.5, "humidity": 60.0}]
        )
        
        assert "type" in results
        assert "container" in results
        assert "initial_data" in results
        assert results["type"]["status"] == "success"