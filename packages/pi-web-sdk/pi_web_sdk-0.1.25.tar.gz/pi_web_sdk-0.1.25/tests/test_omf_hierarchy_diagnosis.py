"""Diagnostic test to understand OMF hierarchy creation issue."""

import pytest
import time
from pi_web_sdk.models.omf import OMFManager


def test_diagnose_omf_element_names(pi_web_api_client):
    """Check what names are being created by OMF hierarchy methods."""
    # Get data server for OMF
    servers = pi_web_api_client.data_server.list()
    data_server_web_id = servers["Items"][0]["WebId"]

    # Create OMF manager
    manager = OMFManager(pi_web_api_client, data_server_web_id)

    test_id = f"diagnose_{int(time.time())}"
    paths = [
        f"{test_id}/Plant1/Unit1/Sensor1",
        f"{test_id}/Plant1/Unit2/Sensor2",
    ]

    print(f"\nTest ID: {test_id}")
    print(f"Paths to create: {paths}")
    print(f"Manager data_server_web_id: {manager.data_server_web_id}")

    try:
        # Try to create with use_af_elements=True (default)
        print("\n" + "="*60)
        print("TESTING WITH use_af_elements=True (should create nested)")
        print("="*60)

        results = manager.create_hierarchy_from_paths(
            paths=paths,
            root_type_id=f"RootType_{test_id}",
            leaf_type_id=f"LeafType_{test_id}",
            create_types=True,
            use_af_elements=True  # Explicit
        )

        print(f"\nResults: {results}")

        if "elements_created" in results:
            print("\n[OK] Used AF element method (proper nesting)")
            for elem in results["elements_created"]:
                print(f"  - Name: {elem['name']}")
                print(f"    Path: {elem['path']}")
                print(f"    WebId: {elem['web_id']}")
        elif "assets_created" in results:
            print("\n[WARN] Used OMF asset method (flat structure)")
            for asset in results["assets_created"]:
                print(f"  - Asset ID: {asset.get('asset_id', 'N/A')}")

        time.sleep(2)

        # Now search for what was created
        print("\n" + "="*60)
        print("SEARCHING FOR CREATED ELEMENTS")
        print("="*60)

        asset_servers = pi_web_api_client.asset_server.list()
        asset_server = asset_servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])

        for db in dbs.get("Items", []):
            print(f"\nSearching in database: {db['Name']}")
            elements = pi_web_api_client.asset_database.get_elements(
                db["WebId"],
                name_filter=f"{test_id}*",
                max_count=100
            )

            if elements.get("Items"):
                print(f"  Found {len(elements['Items'])} elements:")
                for elem in elements["Items"]:
                    print(f"    - {elem['Name']} (Path: {elem.get('Path', 'N/A')})")

                    # Check if it has children
                    try:
                        children = pi_web_api_client.element.get_elements(elem["WebId"])
                        if children.get("Items"):
                            print(f"      Children: {[c['Name'] for c in children['Items']]}")
                    except Exception as e:
                        print(f"      Error getting children: {e}")
            else:
                print(f"  No elements found matching '{test_id}*'")

        # Cleanup
        if "node_map" in results:
            print("\n" + "="*60)
            print("CLEANUP")
            print("="*60)
            # Delete in reverse order (children first)
            node_paths = list(results["node_map"].keys())
            node_paths.reverse()
            for path in node_paths:
                web_id = results["node_map"][path]
                try:
                    pi_web_api_client.element.delete(web_id)
                    print(f"  Deleted: {path}")
                except Exception as e:
                    print(f"  Failed to delete {path}: {e}")

    except Exception as e:
        pytest.fail(f"Test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
