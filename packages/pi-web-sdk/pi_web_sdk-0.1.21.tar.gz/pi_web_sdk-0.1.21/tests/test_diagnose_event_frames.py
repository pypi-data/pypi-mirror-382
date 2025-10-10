"""Diagnostic test to see what event frames exist in PI."""

import pytest
from pi_web_sdk.config import PIWebAPIConfig
from pi_web_sdk.client import PIWebAPIClient


def test_list_all_event_frames(pi_web_api_client):
    """List all event frames to see what exists."""
    # Get database
    servers = pi_web_api_client.asset_server.list()
    asset_server = servers["Items"][0]
    print(f"\nAsset Server: {asset_server['Name']}")

    dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
    database = dbs["Items"][0]
    db_web_id = database["WebId"]
    print(f"Database: {database['Name']}")
    print(f"Database WebId: {db_web_id}")

    # Get all event frames
    event_frames = pi_web_api_client.asset_database.get_event_frames(
        db_web_id,
        max_count=100
    )

    print(f"\nTotal event frames found: {len(event_frames.get('Items', []))}")

    if event_frames.get("Items"):
        print("\nEvent Frames:")
        for ef in event_frames["Items"]:
            print(f"  - {ef['Name']}")
            print(f"    WebId: {ef['WebId']}")
            print(f"    Path: {ef.get('Path', 'N/A')}")
            print(f"    Start: {ef.get('StartTime', 'N/A')}")
            print(f"    End: {ef.get('EndTime', 'N/A')}")

            # Try to get children
            try:
                children = pi_web_api_client.event_frame.get_child_event_frames(ef["WebId"])
                if children.get("Items"):
                    print(f"    Children:")
                    for child in children["Items"]:
                        print(f"      - {child['Name']}")
            except Exception as e:
                print(f"    Error getting children: {e}")
            print()
    else:
        print("No event frames found!")


def test_search_recent_event_frames(pi_web_api_client):
    """Search for recently created event frames."""
    # Get database
    servers = pi_web_api_client.asset_server.list()
    asset_server = servers["Items"][0]
    dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
    db_web_id = dbs["Items"][0]["WebId"]

    # Search with name filter
    event_frames = pi_web_api_client.asset_database.get_event_frames(
        db_web_id,
        name_filter="test_*",
        max_count=100
    )

    print(f"\nEvent frames matching 'test_*': {len(event_frames.get('Items', []))}")
    for ef in event_frames.get("Items", []):
        print(f"  - {ef['Name']} ({ef['WebId']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
