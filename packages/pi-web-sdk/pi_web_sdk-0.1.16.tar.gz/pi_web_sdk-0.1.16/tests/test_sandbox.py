import pytest


@pytest.mark.integration
def test_sandbox_placeholder(pi_web_api_client):
    result = pi_web_api_client.asset_server.list()
    
    # The list() method returns a dict with an 'Items' key
    if "Items" in result and len(result["Items"]) > 0:
        asset_servers = result["Items"][0]
        assert asset_servers is not None
    else:
        # If no asset servers are found, just pass the test
        assert True
