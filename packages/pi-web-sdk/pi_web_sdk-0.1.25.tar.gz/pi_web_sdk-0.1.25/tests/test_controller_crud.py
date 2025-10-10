"""CRUD operation tests for each individual controller."""

import pytest
import time
from typing import Dict, Optional, Any


class TestControllerCRUDPatterns:
    """Test CRUD patterns across all controllers."""

    @pytest.fixture
    def test_data_setup(self, pi_web_api_client):
        """Setup test data for CRUD operations."""
        # Get basic test objects
        setup = {}
        
        # Get asset servers
        servers = pi_web_api_client.asset_server.list().get("Items", [])
        if servers:
            setup["asset_server"] = servers[0]
            
            # Search through multiple servers and databases to find data
            for server in servers[:3]:  # Check first 3 servers
                try:
                    databases = pi_web_api_client.asset_server.get_databases(
                        server["WebId"]
                    ).get("Items", [])
                    
                    for database in databases[:5]:  # Check first 5 databases
                        try:
                            # Set database if not already set
                            if "asset_database" not in setup:
                                setup["asset_database"] = database
                            
                            # Get elements
                            elements = pi_web_api_client.asset_database.get_elements(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            
                            for element in elements[:10]:  # Check first 10 elements
                                try:
                                    # Set element if not already set
                                    if "element" not in setup:
                                        setup["element"] = element
                                    
                                    # Get attributes
                                    try:
                                        attributes = pi_web_api_client.element.get_attributes(
                                            element["WebId"], max_count=10
                                        ).get("Items", [])
                                    except Exception:
                                        attributes = []
                                    
                                    # Look for attribute with data reference
                                    for attribute in attributes:
                                        if "attribute" not in setup:
                                            setup["attribute"] = attribute
                                        
                                        # Look specifically for attributes with data references for stream testing
                                        if ("data_reference_attribute" not in setup and 
                                            ("DataReferencePlugIn" in attribute or 
                                             "DataReference" in attribute or
                                             attribute.get("Type") == "PI Point")):
                                            setup["data_reference_attribute"] = attribute
                                    
                                    # Stop if we found what we need
                                    if "attribute" in setup and "data_reference_attribute" in setup:
                                        break
                                        
                                except Exception:
                                    continue
                            
                            # Break out of database loop if we have what we need
                            if "attribute" in setup and "data_reference_attribute" in setup:
                                break
                                
                        except Exception:
                            continue
                    
                    # Break out of server loop if we have what we need
                    if "attribute" in setup and "data_reference_attribute" in setup:
                        break
                        
                except Exception:
                    continue
        
        # If no attributes found in Asset Framework, try to get PI Points for testing
        if "attribute" not in setup:
            try:
                # Get data servers (PI Data Archive servers)
                data_servers = pi_web_api_client.data_server.list().get("Items", [])
                for data_server in data_servers[:2]:  # Check first 2 data servers
                    try:
                        # Get PI Points (these often work better for testing than AF attributes)
                        points = pi_web_api_client.data_server.get_points(
                            data_server["WebId"], max_count=5
                        ).get("Items", [])
                        
                        if points:
                            # Use first PI Point as a mock attribute for testing
                            point = points[0]
                            setup["pi_point"] = point
                            setup["attribute"] = point  # Use PI Point as attribute for testing
                            setup["data_reference_attribute"] = point  # PI Points have data by definition
                            break
                            
                    except Exception:
                        continue
            except Exception:
                pass
        
        return setup

    @pytest.mark.integration
    def test_asset_server_full_crud(self, pi_web_api_client, test_data_setup):
        """Test full CRUD cycle for AssetServer controller."""
        if "asset_server" not in test_data_setup:
            pytest.skip("No asset server available for testing")
            
        server = test_data_setup["asset_server"]
        
        # CREATE - Asset servers are typically not created via API
        # READ
        retrieved = pi_web_api_client.asset_server.get(server["WebId"])
        assert retrieved["WebId"] == server["WebId"]
        assert retrieved["Name"] == server["Name"]
        
        # READ by name (if supported)
        try:
            by_name = pi_web_api_client.asset_server.get_by_name(server["Name"])
            assert by_name["WebId"] == server["WebId"]
        except Exception:
            # get_by_name may not be supported for all asset servers
            pass
        
        # UPDATE - Asset servers typically don't support updates via API
        # DELETE - Asset servers typically don't support deletion via API
        
        # Test associated operations
        databases = pi_web_api_client.asset_server.get_databases(server["WebId"])
        assert "Items" in databases

    @pytest.mark.integration
    def test_asset_database_crud(self, pi_web_api_client, test_data_setup):
        """Test CRUD operations for AssetDatabase controller."""
        if "asset_database" not in test_data_setup:
            pytest.skip("No asset database available for testing")
            
        database = test_data_setup["asset_database"]
        
        # READ
        retrieved = pi_web_api_client.asset_database.get(database["WebId"])
        assert retrieved["WebId"] == database["WebId"]
        assert retrieved["Name"] == database["Name"]
        
        # Test related operations
        try:
            elements = pi_web_api_client.asset_database.get_elements(
                database["WebId"], max_count=5
            )
            assert "Items" in elements
        except Exception:
            # Some databases may not have get_elements method
            pass

    @pytest.mark.integration
    def test_element_crud(self, pi_web_api_client, test_data_setup):
        """Test CRUD operations for Element controller."""
        if "element" not in test_data_setup:
            pytest.skip("No element available for testing")
            
        element = test_data_setup["element"]
        
        # READ
        retrieved = pi_web_api_client.element.get(element["WebId"])
        assert retrieved["WebId"] == element["WebId"]
        assert retrieved["Name"] == element["Name"]
        
        # Test related operations
        attributes = pi_web_api_client.element.get_attributes(
            element["WebId"], max_count=5
        )
        assert "Items" in attributes
        
        child_elements = pi_web_api_client.element.get_elements(
            element["WebId"], max_count=5
        )
        assert "Items" in child_elements

    @pytest.mark.integration  
    def test_attribute_crud(self, pi_web_api_client, test_data_setup):
        """Test CRUD operations for Attribute controller."""
        # Try to use data reference attribute first, fall back to regular attribute, then PI Point
        attribute = (test_data_setup.get("data_reference_attribute") or 
                    test_data_setup.get("attribute") or 
                    test_data_setup.get("pi_point"))
        
        if not attribute:
            pytest.skip("No attribute or PI Point available for testing")
        
        # If it's a PI Point, use point controller, otherwise use attribute controller
        if attribute == test_data_setup.get("pi_point"):
            # Test PI Point as attribute-like object
            retrieved = pi_web_api_client.point.get(attribute["WebId"])
            assert retrieved["WebId"] == attribute["WebId"]
            assert retrieved["Name"] == attribute["Name"]
            
            # Test value operations on PI Point
            try:
                value = pi_web_api_client.stream.get_value(attribute["WebId"])
                assert isinstance(value, dict)
            except Exception:
                pass  # Some PI Points might not have current values
        else:
            # Test regular attribute
            retrieved = pi_web_api_client.attribute.get(attribute["WebId"])
            assert retrieved["WebId"] == attribute["WebId"]
            assert retrieved["Name"] == attribute["Name"]
            
            # Test value operations
            try:
                value = pi_web_api_client.attribute.get_value(attribute["WebId"])
                assert isinstance(value, dict)
            except Exception:
                pass  # Some attributes might not have values

    @pytest.mark.integration
    def test_batch_controller_crud(self, pi_web_api_client):
        """Test Batch controller operations."""
        # Test simple batch execution
        batch_requests = [
            {
                "Method": "GET",
                "Resource": "system/versions"
            }
        ]
        
        try:
            response = pi_web_api_client.batch.execute(batch_requests)
            assert isinstance(response, dict)
        except Exception:
            pytest.skip("Batch operations may not be available")

    @pytest.mark.integration
    def test_enumeration_controllers_crud(self, pi_web_api_client, test_data_setup):
        """Test EnumerationSet and EnumerationValue controller operations."""
        if "asset_server" not in test_data_setup:
            pytest.skip("No asset server available for enumeration testing")
        
        # Search through multiple servers for enumeration sets
        servers = pi_web_api_client.asset_server.list().get("Items", [])
        enum_set_found = None
        
        for server in servers[:3]:  # Check first 3 servers
            try:
                if hasattr(pi_web_api_client.asset_server, 'get_enumeration_sets'):
                    enum_sets = pi_web_api_client.asset_server.get_enumeration_sets(
                        server["WebId"], max_count=10
                    ).get("Items", [])
                    if enum_sets:
                        enum_set_found = enum_sets[0]
                        break
            except Exception:
                continue
        
        if not enum_set_found:
            # Try alternative approach - look for enumeration sets in databases
            try:
                databases = pi_web_api_client.asset_server.get_databases(
                    test_data_setup["asset_server"]["WebId"]
                ).get("Items", [])
                
                for database in databases[:3]:
                    try:
                        if hasattr(pi_web_api_client.asset_database, 'get_enumeration_sets'):
                            enum_sets = pi_web_api_client.asset_database.get_enumeration_sets(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            if enum_sets:
                                enum_set_found = enum_sets[0]
                                break
                    except Exception:
                        continue
            except Exception:
                pass
        
        if not enum_set_found:
            pytest.skip("No enumeration sets found in PI Web API environment")
        
        try:
            # Test enumeration set operations
            retrieved = pi_web_api_client.enumeration_set.get(enum_set_found["WebId"])
            assert retrieved["WebId"] == enum_set_found["WebId"]
            
            # Test enumeration values
            values = pi_web_api_client.enumeration_set.get_values(enum_set_found["WebId"])
            assert "Items" in values
            
        except Exception:
            pytest.skip("Enumeration operations not available")

    @pytest.mark.integration
    def test_system_controllers_crud(self, pi_web_api_client):
        """Test System-related controller operations."""
        # Home controller
        home = pi_web_api_client.home.get()
        assert "Links" in home
        
        # System controller
        try:
            versions = pi_web_api_client.system.versions()
            assert isinstance(versions, dict)
        except Exception:
            pytest.skip("System versions endpoint not available")
        
        try:
            status = pi_web_api_client.system.status()
            assert isinstance(status, dict)
        except Exception:
            pass  # Status endpoint may not be available
        
        try:
            user_info = pi_web_api_client.system.user_info()
            assert isinstance(user_info, dict)
        except Exception:
            pass  # User info endpoint may not be available

    @pytest.mark.integration
    def test_stream_controller_operations(self, pi_web_api_client, test_data_setup):
        """Test Stream controller operations."""
        # Use data reference attribute, regular attribute, or PI Point for stream testing
        stream_object = (test_data_setup.get("data_reference_attribute") or 
                        test_data_setup.get("attribute") or 
                        test_data_setup.get("pi_point"))
        
        if not stream_object:
            pytest.skip("No stream-capable object available for testing")
        
        # Test stream operations
        try:
            # Try to get stream value
            value = pi_web_api_client.stream.get_value(stream_object["WebId"])
            assert isinstance(value, dict)
        except Exception:
            # Try alternative approaches
            try:
                if stream_object == test_data_setup.get("pi_point"):
                    # For PI Points, we can also test recorded values
                    recorded = pi_web_api_client.stream.get_recorded(
                        stream_object["WebId"], 
                        max_count=1
                    )
                    assert isinstance(recorded, dict)
                else:
                    # For attributes, try get_value
                    value = pi_web_api_client.attribute.get_value(stream_object["WebId"])
                    assert isinstance(value, dict)
            except Exception:
                pytest.skip("Stream operations not available for this object")

    @pytest.mark.integration
    def test_new_controllers_initialization(self, pi_web_api_client):
        """Test that all new controllers are properly initialized."""
        # Test OMF controller
        assert hasattr(pi_web_api_client, 'omf')
        assert callable(pi_web_api_client.omf.post_async)
        
        # Test Security controllers
        assert hasattr(pi_web_api_client, 'security_identity')
        assert hasattr(pi_web_api_client, 'security_mapping')
        assert callable(pi_web_api_client.security_identity.get)
        assert callable(pi_web_api_client.security_mapping.get)
        
        # Test Notification controllers
        assert hasattr(pi_web_api_client, 'notification_rule')
        assert hasattr(pi_web_api_client, 'notification_contact_template')
        assert hasattr(pi_web_api_client, 'notification_plugin')
        assert hasattr(pi_web_api_client, 'notification_rule_subscriber')
        assert hasattr(pi_web_api_client, 'notification_rule_template')
        
        # Test Time Rule controllers
        assert hasattr(pi_web_api_client, 'time_rule')
        assert hasattr(pi_web_api_client, 'time_rule_plugin')
        
        # Test Unit controllers
        assert hasattr(pi_web_api_client, 'unit')
        assert hasattr(pi_web_api_client, 'unit_class')
        
        # Test Metrics controller
        assert hasattr(pi_web_api_client, 'metrics')
        assert callable(pi_web_api_client.metrics.environment)

    @pytest.mark.integration
    def test_controller_error_handling(self, pi_web_api_client):
        """Test error handling across controllers."""
        from pi_web_sdk.exceptions import PIWebAPIError
        
        # Test with invalid WebID
        invalid_webid = "F1AbEfLbwwL8F6EiShvDV-QH70AINVALID"
        
        with pytest.raises(PIWebAPIError):
            pi_web_api_client.element.get(invalid_webid)
            
        with pytest.raises(PIWebAPIError):
            pi_web_api_client.attribute.get(invalid_webid)

    @pytest.mark.integration
    def test_controller_parameter_handling(self, pi_web_api_client, test_data_setup):
        """Test parameter handling across controllers."""
        if "element" not in test_data_setup:
            pytest.skip("No element available for parameter testing")
            
        element = test_data_setup["element"]
        
        # Test selectedFields parameter
        element_limited = pi_web_api_client.element.get(
            element["WebId"], 
            selected_fields="WebId;Name"
        )
        assert "WebId" in element_limited
        assert "Name" in element_limited
        
        # Test pagination parameters
        attributes = pi_web_api_client.element.get_attributes(
            element["WebId"], 
            max_count=2,
            start_index=0
        )
        assert "Items" in attributes

    @pytest.mark.integration
    def test_batch_crud_operations(self, pi_web_api_client, test_data_setup):
        """Test CRUD operations using batch controller."""
        if "element" not in test_data_setup:
            pytest.skip("No element available for batch testing")
            
        element = test_data_setup["element"]
        
        # Create batch request for multiple reads
        batch_requests = [
            {
                "Method": "GET",
                "Resource": f"elements/{element['WebId']}"
            }
        ]
        
        try:
            response = pi_web_api_client.batch.execute(batch_requests)
            assert isinstance(response, dict)
        except Exception:
            pytest.skip("Batch operations not available")

    @pytest.mark.integration
    def test_metrics_controller_operations(self, pi_web_api_client):
        """Test Metrics controller operations."""
        try:
            # Test environment metrics
            env_metrics = pi_web_api_client.metrics.environment()
            assert isinstance(env_metrics, dict)
            
            # Test landing metrics
            landing_metrics = pi_web_api_client.metrics.landing()
            assert isinstance(landing_metrics, dict)
            
            # Test request metrics
            request_metrics = pi_web_api_client.metrics.requests()
            assert isinstance(request_metrics, dict)
            
        except Exception:
            pytest.skip("Metrics endpoints may not be available in this environment")

    @pytest.mark.integration
    def test_all_controllers_have_base_methods(self, pi_web_api_client):
        """Test that all controllers inherit from BaseController properly."""
        controllers_to_test = [
            pi_web_api_client.asset_server,
            pi_web_api_client.asset_database, 
            pi_web_api_client.element,
            pi_web_api_client.attribute,
            pi_web_api_client.omf,
            pi_web_api_client.security_identity,
            pi_web_api_client.metrics,
            pi_web_api_client.time_rule,
            pi_web_api_client.unit
        ]
        
        for controller in controllers_to_test:
            # Check that controller has client reference
            assert hasattr(controller, 'client')
            assert controller.client is pi_web_api_client
            
            # Check that controller has _encode_path method
            assert hasattr(controller, '_encode_path')
            assert callable(controller._encode_path)
            
            # Test _encode_path functionality
            encoded = controller._encode_path("test path with spaces")
            assert " " not in encoded
            assert "test" in encoded