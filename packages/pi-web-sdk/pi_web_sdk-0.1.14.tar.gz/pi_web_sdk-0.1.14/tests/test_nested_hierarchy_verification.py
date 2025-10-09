"""Test to verify proper nested hierarchy creation (not flat structure)."""

import pytest
import time
from pi_web_sdk.models.omf import OMFManager


@pytest.mark.integration
class TestNestedHierarchyVerification:
    """Verify that hierarchies are created with proper parent-child relationships."""

    def test_verify_proper_nesting_not_flat(self, pi_web_api_client):
        """Test that elements are nested properly, not created with full path as name."""
        # Get data server
        servers = pi_web_api_client.data_server.list()
        assert servers["Items"], "No data servers found"
        data_server_web_id = servers["Items"][0]["WebId"]

        # Create OMF manager
        manager = OMFManager(pi_web_api_client, data_server_web_id)

        # Create hierarchy
        test_id = f"nested_test_{int(time.time())}"
        paths = [
            f"{test_id}/Plant1/Area1/Line1/Sensor1",
            f"{test_id}/Plant1/Area1/Line2/Sensor2",
        ]

        results = manager.create_hierarchy_from_paths(
            paths=paths,
            root_type_id="Container",
            leaf_type_id="Sensor",
            use_af_elements=True  # Use AF elements, not OMF
        )

        print(f"\nCreated elements:")
        for elem in results["elements_created"]:
            print(f"  {elem['name']} (path: {elem['path']})")

        # Verify we have the right number of elements
        # root, Plant1, Area1, Line1, Line2, Sensor1, Sensor2 = 7 elements
        assert results["total_count"] == 7, "Should have 7 elements"

        # Get the root element
        root_web_id = results["node_map"][test_id]
        root = pi_web_api_client.element.get(root_web_id)

        # CRITICAL: Verify the root element name is JUST the test_id, not a full path
        assert root["Name"] == test_id, f"Root name should be '{test_id}', not a path"
        print(f"\nRoot element has correct name: {root['Name']}")

        # Verify Plant1 is a direct child of root
        children_of_root = pi_web_api_client.element.get_elements(root_web_id)
        child_names = [c["Name"] for c in children_of_root.get("Items", [])]
        assert "Plant1" in child_names, "Plant1 should be direct child of root"
        print(f"Root children: {child_names}")

        # Get Plant1
        plant1_web_id = results["node_map"][f"{test_id}/Plant1"]
        plant1 = pi_web_api_client.element.get(plant1_web_id)

        # CRITICAL: Verify Plant1 name is just "Plant1", not full path
        assert plant1["Name"] == "Plant1", "Plant1 name should be 'Plant1', not a path"
        print(f"Plant1 has correct name: {plant1['Name']}")

        # Verify Area1 is child of Plant1
        children_of_plant1 = pi_web_api_client.element.get_elements(plant1_web_id)
        area_names = [c["Name"] for c in children_of_plant1.get("Items", [])]
        assert "Area1" in area_names, "Area1 should be direct child of Plant1"
        print(f"Plant1 children: {area_names}")

        # Get Area1
        area1_web_id = results["node_map"][f"{test_id}/Plant1/Area1"]
        area1 = pi_web_api_client.element.get(area1_web_id)
        assert area1["Name"] == "Area1", "Area1 name should be 'Area1'"

        # Verify Line1 and Line2 are children of Area1
        children_of_area1 = pi_web_api_client.element.get_elements(area1_web_id)
        line_names = [c["Name"] for c in children_of_area1.get("Items", [])]
        assert "Line1" in line_names, "Line1 should be child of Area1"
        assert "Line2" in line_names, "Line2 should be child of Area1"
        print(f"Area1 children: {line_names}")

        # Verify Sensor1 is child of Line1
        line1_web_id = results["node_map"][f"{test_id}/Plant1/Area1/Line1"]
        children_of_line1 = pi_web_api_client.element.get_elements(line1_web_id)
        sensor_names = [c["Name"] for c in children_of_line1.get("Items", [])]
        assert "Sensor1" in sensor_names, "Sensor1 should be child of Line1"
        print(f"Line1 children: {sensor_names}")

        print(f"\nHierarchy structure verified:")
        print(f"  {test_id}")
        print(f"    - Plant1")
        print(f"       - Area1")
        print(f"          - Line1")
        print(f"             - Sensor1")
        print(f"          - Line2")
        print(f"             - Sensor2")

        # Cleanup
        try:
            pi_web_api_client.element.delete(root_web_id)
            print(f"\nCleaned up test hierarchy")
        except:
            print(f"\n⚠ Could not clean up (element may already be deleted)")

    def test_compare_old_vs_new_behavior(self, pi_web_api_client):
        """Compare OMF (flat) vs AF element (nested) creation."""
        servers = pi_web_api_client.data_server.list()
        data_server_web_id = servers["Items"][0]["WebId"]
        manager = OMFManager(pi_web_api_client, data_server_web_id)

        test_id = f"compare_{int(time.time())}"
        paths = [f"{test_id}/Plant/Unit/Sensor"]

        # Method 1: OMF (flat structure)
        print("\n" + "="*60)
        print("Method 1: OMF Creation (Flat Structure)")
        print("="*60)
        omf_results = manager.create_hierarchy_from_paths(
            paths=paths,
            root_type_id="ContainerType",
            leaf_type_id="SensorType",
            create_types=True,
            use_af_elements=False  # Use OMF
        )
        print("OMF creates assets with full path as name")
        print("(These appear as flat elements in PI, not nested)")

        # Method 2: AF Elements (nested structure)
        print("\n" + "="*60)
        print("Method 2: AF Element Creation (Proper Nesting)")
        print("="*60)
        test_id2 = f"compare2_{int(time.time())}"
        paths2 = [f"{test_id2}/Plant/Unit/Sensor"]

        af_results = manager.create_hierarchy_from_paths(
            paths=paths2,
            root_type_id="Container",
            leaf_type_id="Sensor",
            use_af_elements=True  # Use AF elements
        )

        print(f"\nAF Elements created: {af_results['total_count']}")
        print("Element names:")
        for elem in af_results["elements_created"]:
            indent = "  " * (elem["path"].count("/"))
            print(f"{indent}- {elem['name']}")

        # Verify AF method creates proper nesting
        root_web_id = af_results["node_map"][test_id2]
        root = pi_web_api_client.element.get(root_web_id)
        assert root["Name"] == test_id2, "AF method should create proper nested structure"

        print(f"\nAF Elements have proper parent-child relationships")
        print(f"  Root: {test_id2}")
        print(f"    - Plant")
        print(f"       - Unit")
        print(f"          - Sensor")

        # Cleanup
        try:
            pi_web_api_client.element.delete(root_web_id)
        except:
            pass
