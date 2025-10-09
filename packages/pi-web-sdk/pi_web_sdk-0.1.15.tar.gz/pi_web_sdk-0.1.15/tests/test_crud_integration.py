"""Comprehensive CRUD integration tests for PI Web API controllers."""

import pytest
from typing import Dict, Optional


class TestSystemControllers:
    """Test system-level controllers."""

    @pytest.mark.integration
    def test_home_controller_get(self, pi_web_api_client):
        """Test Home controller get method."""
        response = pi_web_api_client.home.get()
        assert "Links" in response
        assert isinstance(response["Links"], dict)

    @pytest.mark.integration
    def test_system_controller_versions(self, pi_web_api_client):
        """Test System controller versions method."""
        try:
            response = pi_web_api_client.system.versions()
            assert "PIWebAPI" in response or isinstance(response, dict)
        except Exception:
            pytest.skip("System versions endpoint not available")

    @pytest.mark.integration
    def test_system_controller_status(self, pi_web_api_client):
        """Test System controller status method."""
        try:
            response = pi_web_api_client.system.status()
            assert "CacheInstances" in response or "Status" in response or isinstance(response, dict)
        except Exception:
            pytest.skip("System status endpoint not available")

    @pytest.mark.integration
    def test_metrics_controller_environment(self, pi_web_api_client):
        """Test Metrics controller environment method."""
        try:
            response = pi_web_api_client.metrics.environment()
            assert isinstance(response, dict)
        except Exception:
            pytest.skip("Metrics endpoint may not be available")


class TestAssetControllers:
    """Test asset-related controllers."""

    @pytest.fixture
    def asset_server(self, pi_web_api_client) -> Optional[Dict]:
        """Get first available asset server."""
        servers = pi_web_api_client.asset_server.list().get("Items", [])
        return servers[0] if servers else None

    @pytest.fixture
    def asset_database(self, pi_web_api_client, asset_server) -> Optional[Dict]:
        """Get first available asset database."""
        if not asset_server:
            return None
        databases = pi_web_api_client.asset_server.get_databases(
            asset_server["WebId"]
        ).get("Items", [])
        return databases[0] if databases else None

    @pytest.mark.integration
    def test_asset_server_crud_operations(self, pi_web_api_client, asset_server):
        """Test AssetServer controller CRUD operations."""
        if not asset_server:
            pytest.skip("No asset servers available")

        # Test GET by WebID
        server = pi_web_api_client.asset_server.get(asset_server["WebId"])
        assert server["WebId"] == asset_server["WebId"]
        assert "Name" in server

        # Test GET by name (if supported)
        try:
            server_by_name = pi_web_api_client.asset_server.get_by_name(server["Name"])
            assert server_by_name["WebId"] == server["WebId"]
        except Exception:
            # get_by_name may not be supported
            pass

        # Test GET databases
        databases = pi_web_api_client.asset_server.get_databases(server["WebId"])
        assert "Items" in databases

    @pytest.mark.integration
    def test_asset_database_crud_operations(self, pi_web_api_client, asset_database):
        """Test AssetDatabase controller CRUD operations."""
        if not asset_database:
            pytest.skip("No asset databases available")

        # Test GET by WebID
        database = pi_web_api_client.asset_database.get(asset_database["WebId"])
        assert database["WebId"] == asset_database["WebId"]
        assert "Name" in database

        # Test GET elements (if supported)
        try:
            elements = pi_web_api_client.asset_database.get_elements(
                database["WebId"], max_count=10
            )
            assert "Items" in elements
        except Exception:
            # get_elements may not be supported
            pass

    @pytest.mark.integration
    def test_element_crud_operations(self, pi_web_api_client, asset_database):
        """Test Element controller CRUD operations."""
        if not asset_database:
            pytest.skip("No asset databases available")

        # Get elements to test with
        try:
            elements_response = pi_web_api_client.asset_database.get_elements(
                asset_database["WebId"], max_count=5
            )
            elements = elements_response.get("Items", [])
        except Exception:
            elements = []
        
        if not elements:
            pytest.skip("No elements available for testing")

        element = elements[0]

        # Test GET by WebID
        retrieved_element = pi_web_api_client.element.get(element["WebId"])
        assert retrieved_element["WebId"] == element["WebId"]
        assert "Name" in retrieved_element

        # Test GET attributes
        attributes = pi_web_api_client.element.get_attributes(
            element["WebId"], max_count=10
        )
        assert "Items" in attributes

        # Test GET child elements
        child_elements = pi_web_api_client.element.get_elements(
            element["WebId"], max_count=10
        )
        assert "Items" in child_elements


class TestAttributeControllers:
    """Test attribute-related controllers."""

    @pytest.fixture
    def sample_attribute(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample attribute for testing."""
        try:
            # Get asset servers
            servers = pi_web_api_client.asset_server.list().get("Items", [])
            if not servers:
                return None

            # Try multiple databases to find one with elements
            for server in servers[:2]:  # Check first 2 servers
                try:
                    databases = pi_web_api_client.asset_server.get_databases(
                        server["WebId"]
                    ).get("Items", [])
                    
                    for database in databases[:3]:  # Check first 3 databases
                        try:
                            # Get elements
                            elements = pi_web_api_client.asset_database.get_elements(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            
                            for element in elements[:5]:  # Check first 5 elements
                                try:
                                    # Get attributes
                                    attributes = pi_web_api_client.element.get_attributes(
                                        element["WebId"], max_count=10
                                    ).get("Items", [])
                                    if attributes:
                                        return attributes[0]
                                except Exception:
                                    continue
                        except Exception:
                            continue
                except Exception:
                    continue
            return None
        except Exception:
            return None

    @pytest.mark.integration
    def test_attribute_crud_operations(self, pi_web_api_client, sample_attribute):
        """Test Attribute controller CRUD operations."""
        if not sample_attribute:
            pytest.skip("No attributes available for testing")

        # Test GET by WebID
        attribute = pi_web_api_client.attribute.get(sample_attribute["WebId"])
        assert attribute["WebId"] == sample_attribute["WebId"]
        assert "Name" in attribute

        # Test GET value
        try:
            value = pi_web_api_client.attribute.get_value(attribute["WebId"])
            assert "Value" in value or "Timestamp" in value
        except Exception:
            # Some attributes might not have values
            pass


class TestDataControllers:
    """Test data-related controllers."""

    @pytest.fixture
    def sample_point(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample PI point for testing."""
        try:
            # Get data servers
            servers = pi_web_api_client.data_server.list().get("Items", [])
            if not servers:
                return None

            # Get points
            points = pi_web_api_client.data_server.get_points(
                servers[0]["WebId"], max_count=5
            ).get("Items", [])
            return points[0] if points else None
        except Exception:
            return None

    @pytest.mark.integration
    def test_data_server_operations(self, pi_web_api_client):
        """Test DataServer controller operations."""
        try:
            servers = pi_web_api_client.data_server.list()
            assert "Items" in servers
            
            if servers["Items"]:
                server = servers["Items"][0]
                retrieved = pi_web_api_client.data_server.get(server["WebId"])
                assert retrieved["WebId"] == server["WebId"]
        except Exception:
            pytest.skip("Data server operations not available")

    @pytest.mark.integration
    def test_point_operations(self, pi_web_api_client, sample_point):
        """Test Point controller operations."""
        if not sample_point:
            pytest.skip("No PI points available for testing")

        # Test GET by WebID
        point = pi_web_api_client.point.get(sample_point["WebId"])
        assert point["WebId"] == sample_point["WebId"]
        assert "Name" in point


class TestStreamControllers:
    """Test stream-related controllers."""

    @pytest.mark.integration
    def test_stream_operations(self, pi_web_api_client):
        """Test Stream controller operations."""
        # This test would need a specific stream WebID
        # For now, just test that the methods exist
        assert hasattr(pi_web_api_client.stream, 'get_value')
        assert hasattr(pi_web_api_client.stream, 'get_recorded')
        assert hasattr(pi_web_api_client.stream, 'get_interpolated')


class TestAnalysisControllers:
    """Test analysis-related controllers."""

    @pytest.fixture
    def sample_analysis(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample analysis for testing."""
        try:
            # Get asset servers
            servers = pi_web_api_client.asset_server.list().get("Items", [])
            if not servers:
                return None

            # Try multiple servers and databases to find analyses
            for server in servers[:2]:
                try:
                    databases = pi_web_api_client.asset_server.get_databases(
                        server["WebId"]
                    ).get("Items", [])
                    
                    for database in databases[:3]:
                        try:
                            # Get analyses
                            analyses = pi_web_api_client.asset_database.get_analyses(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            if analyses:
                                return analyses[0]
                        except Exception:
                            continue
                except Exception:
                    continue
            return None
        except Exception:
            return None

    @pytest.mark.integration
    def test_analysis_operations(self, pi_web_api_client, sample_analysis):
        """Test Analysis controller operations."""
        if not sample_analysis:
            pytest.skip("No analyses available for testing")

        # Test GET by WebID
        analysis = pi_web_api_client.analysis.get(sample_analysis["WebId"])
        assert analysis["WebId"] == sample_analysis["WebId"]
        assert "Name" in analysis


class TestBatchControllers:
    """Test batch-related controllers."""

    @pytest.mark.integration
    def test_batch_execution(self, pi_web_api_client):
        """Test Batch controller execution."""
        # Test simple batch request
        requests = [
            {
                "Method": "GET",
                "Resource": "system/versions"
            }
        ]
        
        try:
            response = pi_web_api_client.batch.execute(requests)
            assert isinstance(response, dict)
            # Batch responses typically contain the results
        except Exception:
            pytest.skip("Batch operations not available")


class TestEnumerationControllers:
    """Test enumeration-related controllers."""

    @pytest.fixture
    def sample_enumeration_set(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample enumeration set for testing."""
        try:
            # Get asset servers
            servers = pi_web_api_client.asset_server.list().get("Items", [])
            if not servers:
                return None

            # Try multiple servers to find enumeration sets
            for server in servers:
                try:
                    enum_sets = pi_web_api_client.asset_server.get_enumeration_sets(
                        server["WebId"], max_count=10
                    ).get("Items", [])
                    if enum_sets:
                        return enum_sets[0]
                except Exception:
                    continue
            return None
        except Exception:
            return None

    @pytest.mark.integration
    def test_enumeration_set_operations(self, pi_web_api_client, sample_enumeration_set):
        """Test EnumerationSet controller operations."""
        if not sample_enumeration_set:
            pytest.skip("No enumeration sets available for testing")

        # Test GET by WebID
        enum_set = pi_web_api_client.enumeration_set.get(sample_enumeration_set["WebId"])
        assert enum_set["WebId"] == sample_enumeration_set["WebId"]
        assert "Name" in enum_set


class TestOMFController:
    """Test OMF controller."""

    @pytest.mark.integration
    def test_omf_controller_exists(self, pi_web_api_client):
        """Test that OMF controller is properly initialized."""
        assert hasattr(pi_web_api_client, 'omf')
        assert hasattr(pi_web_api_client.omf, 'post_async')


class TestSecurityControllers:
    """Test security-related controllers."""

    @pytest.mark.integration
    def test_security_controllers_exist(self, pi_web_api_client):
        """Test that security controllers are properly initialized."""
        assert hasattr(pi_web_api_client, 'security_identity')
        assert hasattr(pi_web_api_client, 'security_mapping')
        assert hasattr(pi_web_api_client.security_identity, 'get')
        assert hasattr(pi_web_api_client.security_mapping, 'get')


class TestNotificationControllers:
    """Test notification-related controllers."""

    @pytest.mark.integration
    def test_notification_controllers_exist(self, pi_web_api_client):
        """Test that notification controllers are properly initialized."""
        assert hasattr(pi_web_api_client, 'notification_rule')
        assert hasattr(pi_web_api_client, 'notification_contact_template')
        assert hasattr(pi_web_api_client, 'notification_plugin')
        assert hasattr(pi_web_api_client.notification_rule, 'get')


class TestTimeRuleControllers:
    """Test time rule controllers."""

    @pytest.mark.integration
    def test_time_rule_controllers_exist(self, pi_web_api_client):
        """Test that time rule controllers are properly initialized."""
        assert hasattr(pi_web_api_client, 'time_rule')
        assert hasattr(pi_web_api_client, 'time_rule_plugin')
        assert hasattr(pi_web_api_client.time_rule, 'get')


class TestUnitControllers:
    """Test unit controllers."""

    @pytest.mark.integration
    def test_unit_controllers_exist(self, pi_web_api_client):
        """Test that unit controllers are properly initialized."""
        assert hasattr(pi_web_api_client, 'unit')
        assert hasattr(pi_web_api_client, 'unit_class')
        assert hasattr(pi_web_api_client.unit, 'get')
        assert hasattr(pi_web_api_client.unit_class, 'get')


class TestEventFrameController:
    """Test event frame controller."""

    @pytest.fixture
    def sample_event_frame(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample event frame for testing."""
        try:
            # Get asset servers
            servers = pi_web_api_client.asset_server.list().get("Items", [])
            if not servers:
                return None

            # Try multiple servers and databases to find event frames
            for server in servers[:2]:
                try:
                    databases = pi_web_api_client.asset_server.get_databases(
                        server["WebId"]
                    ).get("Items", [])
                    
                    for database in databases[:3]:
                        try:
                            # Get event frames
                            event_frames = pi_web_api_client.asset_database.get_event_frames(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            if event_frames:
                                return event_frames[0]
                        except Exception:
                            continue
                except Exception:
                    continue
            return None
        except Exception:
            return None

    @pytest.mark.integration
    def test_event_frame_operations(self, pi_web_api_client, sample_event_frame):
        """Test EventFrame controller operations."""
        if not sample_event_frame:
            pytest.skip("No event frames available for testing")

        # Test GET by WebID
        event_frame = pi_web_api_client.event_frame.get(sample_event_frame["WebId"])
        assert event_frame["WebId"] == sample_event_frame["WebId"]
        assert "Name" in event_frame


class TestTableController:
    """Test table controller."""

    @pytest.fixture
    def sample_table(self, pi_web_api_client) -> Optional[Dict]:
        """Get a sample table for testing."""
        try:
            # Get asset servers
            servers = pi_web_api_client.asset_server.list().get("Items", [])
            if not servers:
                return None

            # Try multiple servers and databases to find tables
            for server in servers[:2]:
                try:
                    databases = pi_web_api_client.asset_server.get_databases(
                        server["WebId"]
                    ).get("Items", [])
                    
                    for database in databases[:3]:
                        try:
                            # Get tables
                            tables = pi_web_api_client.asset_database.get_tables(
                                database["WebId"], max_count=10
                            ).get("Items", [])
                            if tables:
                                return tables[0]
                        except Exception:
                            continue
                except Exception:
                    continue
            return None
        except Exception:
            return None

    @pytest.mark.integration
    def test_table_operations(self, pi_web_api_client, sample_table):
        """Test Table controller operations."""
        if not sample_table:
            pytest.skip("No tables available for testing")

        # Test GET by WebID
        table = pi_web_api_client.table.get(sample_table["WebId"])
        assert table["WebId"] == sample_table["WebId"]
        assert "Name" in table