"""Show the complete event frame hierarchy structure."""

import pytest
from pi_web_sdk.config import PIWebAPIConfig
from pi_web_sdk.client import PIWebAPIClient


def print_event_frame_tree(client, web_id, indent=0):
    """Recursively print event frame tree."""
    ef = client.event_frame.get(web_id)
    prefix = "  " * indent
    print(f"{prefix}- {ef['Name']}")
    print(f"{prefix}  Path: {ef.get('Path', 'N/A')}")
    print(f"{prefix}  Start: {ef.get('StartTime', 'N/A')}")
    print(f"{prefix}  End: {ef.get('EndTime', 'N/A')}")

    # Get children
    try:
        children = client.event_frame.get_child_event_frames(web_id)
        if children.get("Items"):
            print(f"{prefix}  Children:")
            for child in children["Items"]:
                print_event_frame_tree(client, child["WebId"], indent + 2)
    except Exception as e:
        print(f"{prefix}  Error getting children: {e}")


def test_show_event_frame_structure(pi_web_api_client):
    """Show the complete structure of event frames."""
    # Get database
    servers = pi_web_api_client.asset_server.list()
    asset_server = servers["Items"][0]
    dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
    db_web_id = dbs["Items"][0]["WebId"]

    # Get all top-level event frames
    event_frames = pi_web_api_client.asset_database.get_event_frames(
        db_web_id,
        name_filter="test_*",
        max_count=100
    )

    print(f"\n{'='*60}")
    print(f"EVENT FRAME HIERARCHY")
    print(f"{'='*60}\n")
    print(f"Database: {dbs['Items'][0]['Name']}")
    print(f"Total top-level event frames: {len(event_frames.get('Items', []))}\n")

    if event_frames.get("Items"):
        for ef in event_frames["Items"]:
            print_event_frame_tree(pi_web_api_client, ef["WebId"])
            print()
    else:
        print("No event frames found matching 'test_*'")

    print(f"\n{'='*60}")
    print("WHERE TO FIND EVENT FRAMES IN PI SYSTEM EXPLORER:")
    print("1. Open PI System Explorer (PSE)")
    print("2. Expand your Asset Server (WIN-040LFOGLJIE)")
    print("3. Expand 'Configuration' database")
    print("4. Look in the 'Event Frames' section (not in Elements!)")
    print("5. Event frames are stored separately from elements")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
