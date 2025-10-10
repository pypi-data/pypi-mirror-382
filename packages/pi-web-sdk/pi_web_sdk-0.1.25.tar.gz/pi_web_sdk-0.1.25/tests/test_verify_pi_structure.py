"""Test to show actual element structure in PI System Explorer."""

import pytest
import time
from pi_web_sdk.models.omf import OMFManager


@pytest.mark.integration
def test_show_pi_structure(pi_web_api_client):
    """Create hierarchy and show actual PI structure."""

    # Get data server
    servers = pi_web_api_client.data_server.list()
    data_server_web_id = servers["Items"][0]["WebId"]

    # Create OMF manager
    manager = OMFManager(pi_web_api_client, data_server_web_id)

    # Create hierarchy
    test_id = f"verify_{int(time.time())}"
    paths = [
        f"{test_id}/Plant1/Unit1/Sensor1",
        f"{test_id}/Plant1/Unit2/Sensor2",
    ]

    print(f"\n{'='*80}")
    print(f"Creating hierarchy: {test_id}")
    print(f"{'='*80}")

    results = manager.create_hierarchy_from_paths(
        paths=paths,
        root_type_id="Container",
        leaf_type_id="Sensor",
        use_af_elements=True  # This creates proper AF elements
    )

    print(f"\nCreated {results['total_count']} elements")
    print(f"\nElements created:")
    for elem in results["elements_created"]:
        indent = "  " * elem["path"].count("/")
        print(f"{indent}[{elem['name']}]")

    # Now let's verify by reading back from PI
    print(f"\n{'='*80}")
    print("Verifying structure in PI System Explorer:")
    print(f"{'='*80}")

    root_web_id = results["node_map"][test_id]

    # Get root element
    root = pi_web_api_client.element.get(root_web_id)
    print(f"\nRoot Element:")
    print(f"  Name: {root['Name']}")
    print(f"  Path: {root.get('Path', 'N/A')}")
    print(f"  WebId: {root['WebId']}")

    # Get children of root
    children = pi_web_api_client.element.get_elements(root_web_id)
    print(f"\n  Children of '{root['Name']}':")
    for child in children.get("Items", []):
        print(f"    - {child['Name']} (WebId: {child['WebId']})")

        # Get grandchildren
        grandchildren = pi_web_api_client.element.get_elements(child["WebId"])
        if grandchildren.get("Items"):
            print(f"      Children of '{child['Name']}':")
            for gc in grandchildren["Items"]:
                print(f"        - {gc['Name']} (WebId: {gc['WebId']})")

                # Get great-grandchildren
                ggc_list = pi_web_api_client.element.get_elements(gc["WebId"])
                if ggc_list.get("Items"):
                    print(f"          Children of '{gc['Name']}':")
                    for ggc in ggc_list["Items"]:
                        print(f"            - {ggc['Name']} (WebId: {ggc['WebId']})")

    print(f"\n{'='*80}")
    print("Summary - Structure in PI System Explorer:")
    print(f"{'='*80}")
    print(f"{test_id}/")
    print(f"  └─ Plant1/")
    print(f"       ├─ Unit1/")
    print(f"       │    └─ Sensor1")
    print(f"       └─ Unit2/")
    print(f"            └─ Sensor2")

    print(f"\n{'='*80}")
    print("To view in PI System Explorer:")
    print(f"{'='*80}")
    print(f"1. Open PI System Explorer")
    print(f"2. Navigate to AF Database: Configuration")
    print(f"3. Look for element: {test_id}")
    print(f"4. Expand to see nested structure")
    print(f"{'='*80}")

    # Cleanup
    try:
        pi_web_api_client.element.delete(root_web_id)
        print(f"\nCleaned up test hierarchy: {test_id}")
    except Exception as e:
        print(f"\n⚠ Could not clean up: {e}")
