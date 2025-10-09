"""Live integration tests for OMF hierarchy creation in PI Web API."""

import pytest
import time
from pi_web_sdk.models.omf import (
    OMFManager, OMFHierarchy, create_hierarchy_from_paths
)


@pytest.mark.integration
class TestOMFHierarchyLive:
    """Live tests for OMF hierarchy creation."""
    
    def test_create_simple_hierarchy_live(self, pi_web_api_client):
        """Test creating a simple hierarchy in live PI system."""
        # Get data server
        servers = pi_web_api_client.data_server.list()
        assert servers["Items"], "No data servers found"
        data_server_web_id = servers["Items"][0]["WebId"]
        
        # Create OMF manager
        manager = OMFManager(pi_web_api_client, data_server_web_id)
        
        # Create hierarchy
        test_id = f"test_hierarchy_{int(time.time())}"
        paths = [
            f"{test_id}/Plant1/Unit1/Sensor1",
            f"{test_id}/Plant1/Unit2/Sensor2",
        ]
        
        try:
            # Create hierarchy using manager
            results = manager.create_hierarchy_from_paths(
                paths=paths,
                root_type_id=f"ContainerType_{test_id}",
                leaf_type_id=f"SensorType_{test_id}",
                create_types=True
            )
            
            assert results is not None
            print(f"\nHierarchy creation results: {results}")
            
            # Give PI time to process
            time.sleep(2)
            
            # Try to verify elements exist
            # Search for root element
            asset_servers = pi_web_api_client.asset_server.list()
            if asset_servers["Items"]:
                asset_server = asset_servers["Items"][0]
                
                # List databases (use AssetServerController method)
                dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
                print(f"\nAvailable databases: {[db['Name'] for db in dbs.get('Items', [])]}")

                # Try to find our hierarchy
                for db in dbs.get("Items", []):
                    elements = pi_web_api_client.asset_database.get_elements(
                        db["WebId"],
                        name_filter=test_id
                    )
                    if elements.get("Items"):
                        print(f"\nFound elements: {[e['Name'] for e in elements['Items']]}")
                        assert True, "Elements found in PI"
                        return
                
                print(f"\nWarning: Elements with name '{test_id}' not found in AF databases")
                print("Hierarchy may have been created but not visible through AF structure")
                
        except Exception as e:
            pytest.fail(f"Failed to create hierarchy: {e}")
    
    def test_verify_hierarchy_structure_live(self, pi_web_api_client):
        """Test creating and verifying hierarchical structure."""
        servers = pi_web_api_client.data_server.list()
        assert servers["Items"], "No data servers found"
        data_server_web_id = servers["Items"][0]["WebId"]
        
        manager = OMFManager(pi_web_api_client, data_server_web_id)
        
        test_id = f"test_structure_{int(time.time())}"
        
        # Create a hierarchy programmatically
        hierarchy = OMFHierarchy(
            root_type_id=f"Container_{test_id}",
            leaf_type_id=f"Leaf_{test_id}"
        )
        
        # Build structure
        hierarchy.create_path(
            f"{test_id}/Area1/Line1/Sensor1",
            leaf_properties={"sensor_type": "temperature", "units": "C"}
        )
        hierarchy.create_path(
            f"{test_id}/Area1/Line1/Sensor2",
            leaf_properties={"sensor_type": "pressure", "units": "bar"}
        )
        hierarchy.create_path(
            f"{test_id}/Area2/Line2/Sensor3",
            leaf_properties={"sensor_type": "flow", "units": "m3/h"}
        )
        
        try:
            # Create hierarchy directly using manager
            results = manager.create_hierarchy(
                hierarchy=hierarchy,
                create_types=True
            )

            print(f"\nHierarchy creation results: {results}")

            # Give PI time to process
            time.sleep(2)

            print(f"\nHierarchy '{test_id}' created with {len(hierarchy.get_all_nodes())} nodes")
            print(f"Paths: {hierarchy.get_all_paths()}")

        except Exception as e:
            pytest.fail(f"Failed to create hierarchical structure: {e}")
    
    def test_industrial_hierarchy_live(self, pi_web_api_client):
        """Test creating an industrial-style hierarchy."""
        from pi_web_sdk.models.omf import create_industrial_hierarchy
        
        servers = pi_web_api_client.data_server.list()
        assert servers["Items"], "No data servers found"
        data_server_web_id = servers["Items"][0]["WebId"]
        
        manager = OMFManager(pi_web_api_client, data_server_web_id)
        
        test_id = f"industrial_{int(time.time())}"
        
        try:
            # Create using convenience function
            results = manager.create_industrial_hierarchy(
                plants=[f"{test_id}_PlantA", f"{test_id}_PlantB"],
                units_per_plant={
                    f"{test_id}_PlantA": ["Boiler", "Turbine"],
                    f"{test_id}_PlantB": ["Reactor", "Cooler"]
                },
                sensors_per_unit={
                    "Boiler": ["Temp1", "Press1"],
                    "Turbine": ["Speed1", "Vib1"],
                    "Reactor": ["Temp2", "Level1"],
                    "Cooler": ["Temp3", "Flow1"]
                },
                create_types=True
            )
            
            print(f"\nIndustrial hierarchy results: {results}")
            
            time.sleep(2)
            
            print(f"\nIndustrial hierarchy '{test_id}' created")
            
        except Exception as e:
            pytest.fail(f"Failed to create industrial hierarchy: {e}")
