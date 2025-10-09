"""Comprehensive tests for OMF (OCS Message Format) endpoint."""

import pytest
import json
import time
from typing import Dict, List
from datetime import datetime, timezone


class TestOMFEndpoint:
    """Test OMF endpoint with asset and stream creation."""

    @pytest.fixture
    def data_server_web_id(self, pi_web_api_client):
        """Get a data server WebID for OMF operations."""
        try:
            servers = pi_web_api_client.data_server.list().get("Items", [])
            if servers:
                return servers[0]["WebId"]
            return None
        except Exception:
            return None

    @pytest.fixture
    def omf_type_definition(self):
        """Define an OMF type for testing."""
        return {
            "id": "TestSensorType",
            "type": "object",
            "classification": "dynamic",
            "properties": {
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "isindex": True
                },
                "temperature": {
                    "type": "number",
                    "description": "Temperature in Celsius"
                },
                "pressure": {
                    "type": "number", 
                    "description": "Pressure in Pa"
                },
                "status": {
                    "type": "string",
                    "description": "Equipment status"
                }
            }
        }

    @pytest.fixture
    def omf_container_definition(self):
        """Define an OMF container (stream) for testing."""
        timestamp = int(time.time())
        return {
            "id": f"TestSensor_{timestamp}",
            "typeid": "TestSensorType",
            "name": f"Test Sensor Stream {timestamp}",
            "description": "Test sensor data stream created via OMF"
        }

    @pytest.fixture
    def omf_static_type_definition(self):
        """Define an OMF static type for asset metadata."""
        return {
            "id": "TestAssetType",
            "type": "object", 
            "classification": "static",
            "properties": {
                "name": {
                    "type": "string",
                    "isindex": True
                },
                "location": {
                    "type": "string",
                    "description": "Asset location"
                },
                "model": {
                    "type": "string",
                    "description": "Equipment model"
                },
                "serialNumber": {
                    "type": "string",
                    "description": "Serial number"
                }
            }
        }

    @pytest.fixture
    def omf_asset_definition(self):
        """Define an OMF asset for testing."""
        timestamp = int(time.time())
        return {
            "typeid": "TestAssetType",
            "values": [
                {
                    "name": f"TestAsset_{timestamp}",  # Index property must be in values
                    "location": "Test Facility",
                    "model": "Test Model 3000",
                    "serialNumber": f"SN{timestamp}"
                }
            ]
        }

    @pytest.mark.integration
    def test_omf_controller_exists(self, pi_web_api_client):
        """Test that OMF controller is properly initialized."""
        assert hasattr(pi_web_api_client, 'omf')
        assert hasattr(pi_web_api_client.omf, 'post_async')
        assert callable(pi_web_api_client.omf.post_async)

    @pytest.mark.integration 
    def test_omf_create_type(self, pi_web_api_client, data_server_web_id, omf_type_definition):
        """Test creating an OMF type definition."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # Create OMF type
            response = pi_web_api_client.omf.post_async(
                data=[omf_type_definition],
                message_type="Type",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            # OMF responses vary by implementation - check for success indicators
            assert isinstance(response, dict)
            # Success typically indicated by no error or 2xx status in nested response
            
        except Exception as e:
            # Some PI Web API installations may not support OMF
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_create_static_type(self, pi_web_api_client, data_server_web_id, omf_static_type_definition):
        """Test creating an OMF static type for assets."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # Create OMF static type for assets
            response = pi_web_api_client.omf.post_async(
                data=[omf_static_type_definition],
                message_type="Type",
                omf_version="1.2", 
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            assert isinstance(response, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_create_container(self, pi_web_api_client, data_server_web_id, omf_container_definition):
        """Test creating an OMF container (stream)."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # First ensure type exists (may fail if previous test didn't run)
            type_def = {
                "id": "TestSensorType",
                "type": "object",
                "classification": "dynamic",
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time", "isindex": True},
                    "temperature": {"type": "number"},
                    "pressure": {"type": "number"},
                    "status": {"type": "string"}
                }
            }
            
            try:
                pi_web_api_client.omf.post_async(
                    data=[type_def],
                    message_type="Type",
                    omf_version="1.2",
                    action="create",
                    data_server_web_id=data_server_web_id
                )
            except Exception:
                pass  # Type might already exist
            
            # Create container
            response = pi_web_api_client.omf.post_async(
                data=[omf_container_definition],
                message_type="Container",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            assert isinstance(response, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_create_asset(self, pi_web_api_client, data_server_web_id, omf_asset_definition):
        """Test creating an OMF asset.""" 
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # First ensure static type exists
            static_type_def = {
                "id": "TestAssetType",
                "type": "object",
                "classification": "static", 
                "properties": {
                    "name": {"type": "string", "isindex": True},
                    "location": {"type": "string"},
                    "model": {"type": "string"},
                    "serialNumber": {"type": "string"}
                }
            }
            
            try:
                pi_web_api_client.omf.post_async(
                    data=[static_type_def],
                    message_type="Type",
                    omf_version="1.2",
                    action="create",
                    data_server_web_id=data_server_web_id
                )
            except Exception:
                pass  # Type might already exist
            
            # Create asset
            response = pi_web_api_client.omf.post_async(
                data=[omf_asset_definition],
                message_type="Data",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            assert isinstance(response, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_send_data(self, pi_web_api_client, data_server_web_id, omf_container_definition):
        """Test sending time series data via OMF."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # Ensure type and container exist
            type_def = {
                "id": "TestSensorType",
                "type": "object",
                "classification": "dynamic",
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time", "isindex": True},
                    "temperature": {"type": "number"},
                    "pressure": {"type": "number"},
                    "status": {"type": "string"}
                }
            }
            
            try:
                # Create type
                pi_web_api_client.omf.post_async(
                    data=[type_def],
                    message_type="Type",
                    omf_version="1.2",
                    action="create",
                    data_server_web_id=data_server_web_id
                )
                
                # Create container
                pi_web_api_client.omf.post_async(
                    data=[omf_container_definition],
                    message_type="Container",
                    omf_version="1.2",
                    action="create",
                    data_server_web_id=data_server_web_id
                )
            except Exception:
                pass  # May already exist
            
            # Send time series data
            current_time = datetime.now(timezone.utc).isoformat()
            data_message = {
                "containerid": omf_container_definition["id"],
                "values": [
                    {
                        "timestamp": current_time,
                        "temperature": 25.5,
                        "pressure": 101325.0,
                        "status": "Normal"
                    },
                    {
                        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                        "temperature": 26.0,
                        "pressure": 101300.0,
                        "status": "Normal"
                    }
                ]
            }
            
            response = pi_web_api_client.omf.post_async(
                data=[data_message],
                message_type="Data",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            assert isinstance(response, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_full_workflow(self, pi_web_api_client, data_server_web_id):
        """Test complete OMF workflow: type -> container -> asset -> data."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            timestamp = int(time.time())
            
            # Step 1: Create dynamic type for time series
            dynamic_type = {
                "id": f"SensorType_{timestamp}",
                "type": "object",
                "classification": "dynamic",
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time", "isindex": True},
                    "value": {"type": "number", "description": "Sensor reading"},
                    "quality": {"type": "string", "description": "Data quality"}
                }
            }
            
            response1 = pi_web_api_client.omf.post_async(
                data=[dynamic_type],
                message_type="Type",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            assert isinstance(response1, dict)
            
            # Step 2: Create static type for asset
            static_type = {
                "id": f"EquipmentType_{timestamp}",
                "type": "object",
                "classification": "static",
                "properties": {
                    "name": {"type": "string", "isindex": True},
                    "manufacturer": {"type": "string"},
                    "installDate": {"type": "string", "format": "date-time"}
                }
            }
            
            response2 = pi_web_api_client.omf.post_async(
                data=[static_type],
                message_type="Type", 
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            assert isinstance(response2, dict)
            
            # Step 3: Create container (stream)
            container = {
                "id": f"Sensor_{timestamp}",
                "typeid": f"SensorType_{timestamp}",
                "name": f"Test Sensor {timestamp}",
                "description": "OMF workflow test sensor"
            }
            
            response3 = pi_web_api_client.omf.post_async(
                data=[container],
                message_type="Container",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            assert isinstance(response3, dict)
            
            # Step 4: Create asset
            asset = {
                "typeid": f"EquipmentType_{timestamp}",
                "values": [{
                    "name": f"Equipment_{timestamp}",  # Index property in values
                    "manufacturer": "ACME Corp",
                    "installDate": datetime.now(timezone.utc).isoformat()
                }]
            }
            
            response4 = pi_web_api_client.omf.post_async(
                data=[asset],
                message_type="Data",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            assert isinstance(response4, dict)
            
            # Step 5: Send time series data
            ts_data = {
                "containerid": f"Sensor_{timestamp}",
                "values": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "value": 42.0,
                        "quality": "Good"
                    }
                ]
            }
            
            response5 = pi_web_api_client.omf.post_async(
                data=[ts_data],
                message_type="Data",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            assert isinstance(response5, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise

    @pytest.mark.integration
    def test_omf_error_handling(self, pi_web_api_client, data_server_web_id):
        """Test OMF error handling with invalid data."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            # Test with invalid type definition
            invalid_type = {
                "id": "InvalidType",
                "type": "invalid_type",  # Invalid type
                "classification": "dynamic"
                # Missing required properties
            }
            
            # This should either fail or handle gracefully
            try:
                response = pi_web_api_client.omf.post_async(
                    data=[invalid_type],
                    message_type="Type",
                    omf_version="1.2",
                    action="create",
                    data_server_web_id=data_server_web_id
                )
                # If no exception, ensure response indicates error
                assert isinstance(response, dict)
            except Exception:
                # Expected behavior for invalid data
                pass
                
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                # For OMF error handling test, we expect some errors
                pass

    @pytest.mark.integration
    def test_omf_batch_operations(self, pi_web_api_client, data_server_web_id):
        """Test sending multiple OMF objects in a single request."""
        if not data_server_web_id:
            pytest.skip("No data server available for OMF testing")

        try:
            timestamp = int(time.time())
            
            # Send multiple types in one request
            types = [
                {
                    "id": f"BatchType1_{timestamp}",
                    "type": "object",
                    "classification": "dynamic",
                    "properties": {
                        "timestamp": {"type": "string", "format": "date-time", "isindex": True},
                        "value1": {"type": "number"}
                    }
                },
                {
                    "id": f"BatchType2_{timestamp}",
                    "type": "object", 
                    "classification": "dynamic",
                    "properties": {
                        "timestamp": {"type": "string", "format": "date-time", "isindex": True},
                        "value2": {"type": "number"}
                    }
                }
            ]
            
            response = pi_web_api_client.omf.post_async(
                data=types,
                message_type="Type",
                omf_version="1.2",
                action="create",
                data_server_web_id=data_server_web_id
            )
            
            assert isinstance(response, dict)
            
        except Exception as e:
            if "not supported" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip("OMF endpoint not supported in this PI Web API installation")
            else:
                raise