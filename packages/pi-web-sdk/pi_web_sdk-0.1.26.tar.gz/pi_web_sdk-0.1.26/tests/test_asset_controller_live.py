import pytest


@pytest.mark.integration
def test_asset_server_listing_contains_items(pi_web_api_client):
    response = pi_web_api_client.asset_server.list()
    items = response.get("Items", [])

    if not items:
        pytest.skip("No asset servers returned from live PI Web API")

    first = items[0]
    assert set(first) >= {"WebId", "Name"}


@pytest.mark.integration
def test_asset_database_listing_for_first_server(pi_web_api_client):
    servers = pi_web_api_client.asset_server.list().get("Items", [])
    if not servers:
        pytest.skip("No asset servers returned from live PI Web API")

    first_server = servers[0]
    databases = pi_web_api_client.asset_server.get_databases(first_server["WebId"]).get(
        "Items", []
    )
    if not databases:
        pytest.skip(
            f"No asset databases available on asset server {first_server.get('Name', 'unknown')}"
        )

    for database in databases:
        assert set(database) >= {"WebId", "Name"}
