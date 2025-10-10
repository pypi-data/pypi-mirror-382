import pytest


@pytest.mark.integration
def test_data_server_listing_contains_items(pi_web_api_client):
    response = pi_web_api_client.data_server.list()
    items = response.get("Items", [])
    if not items:
        pytest.skip("No data servers returned from live PI Web API")

    first = items[0]
    assert set(first) >= {"WebId", "Name"}


@pytest.mark.integration
def test_points_for_first_data_server(pi_web_api_client):
    data_servers = pi_web_api_client.data_server.list().get("Items", [])
    if not data_servers:
        pytest.skip("No data servers returned from live PI Web API")

    first_server = data_servers[0]
    points_response = pi_web_api_client.data_server.get_points(
        first_server["WebId"],
        max_count=10,
    )
    points = points_response.get("Items", [])
    if not points:
        pytest.skip(f"No points available on data server {first_server.get('Name', 'unknown')}")

    first_point = points[0]
    point_details = pi_web_api_client.point.get(
        first_point["WebId"],
        selected_fields="WebId;Name;Descriptor",
    )
    assert point_details.get("WebId") == first_point["WebId"]
    assert "Name" in point_details
