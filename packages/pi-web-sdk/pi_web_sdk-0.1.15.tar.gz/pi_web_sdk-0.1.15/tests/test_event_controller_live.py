import pytest


@pytest.mark.integration
def test_event_frame_roundtrip_from_first_database(pi_web_api_client):
    asset_servers = pi_web_api_client.asset_server.list().get("Items", [])
    if not asset_servers:
        pytest.skip("No asset servers returned from live PI Web API")

    first_server = asset_servers[0]
    databases = pi_web_api_client.asset_server.get_databases(first_server["WebId"]).get("Items", [])
    if not databases:
        pytest.skip(f"No asset databases available on asset server {first_server.get('Name', 'unknown')}")

    first_database = databases[0]
    event_frames_response = pi_web_api_client.event_frame.get_event_frames(
        database_web_id=first_database["WebId"],
        max_count=5,
    )
    event_frames = event_frames_response.get("Items", [])
    if not event_frames:
        pytest.skip(f"No event frames available in asset database {first_database.get('Name', 'unknown')}")

    first_frame = event_frames[0]
    details = pi_web_api_client.event_frame.get(
        first_frame["WebId"],
        selected_fields="WebId;Name;PrimaryReferencedElement",
    )

    assert details.get("WebId") == first_frame["WebId"]
    assert "Name" in details


@pytest.mark.integration
def test_event_frame_attributes_listing(pi_web_api_client):
    asset_servers = pi_web_api_client.asset_server.list().get("Items", [])
    if not asset_servers:
        pytest.skip("No asset servers returned from live PI Web API")

    first_server = asset_servers[0]
    databases = pi_web_api_client.asset_server.get_databases(first_server["WebId"]).get("Items", [])
    if not databases:
        pytest.skip(f"No asset databases available on asset server {first_server.get('Name', 'unknown')}")

    first_database = databases[0]
    event_frames = pi_web_api_client.event_frame.get_event_frames(
        database_web_id=first_database["WebId"],
        max_count=1,
    ).get("Items", [])
    if not event_frames:
        pytest.skip(f"No event frames available in asset database {first_database.get('Name', 'unknown')}")

    event_frame = event_frames[0]
    attributes_response = pi_web_api_client.event_frame.get_attributes(event_frame["WebId"], max_count=10)
    assert "Items" in attributes_response
