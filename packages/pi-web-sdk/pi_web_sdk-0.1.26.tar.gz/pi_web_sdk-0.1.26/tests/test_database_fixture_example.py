"""Example test showing how to use the test_af_database fixture."""

import pytest


def test_using_default_database(pi_web_api_client, test_af_database):
    """Example test using the test database fixture."""
    print(f"\nDatabase Name: {test_af_database['name']}")
    print(f"Database Path: {test_af_database['path']}")
    print(f"Database WebId: {test_af_database['web_id']}")
    print(f"Asset Server WebId: {test_af_database['asset_server_web_id']}")

    # Use the database in your test
    db_web_id = test_af_database["web_id"]

    # Example: Get elements from the database
    elements = pi_web_api_client.asset_database.get_elements(db_web_id, max_count=10)
    print(f"\nNumber of elements: {len(elements.get('Items', []))}")

    assert db_web_id is not None
    assert test_af_database["name"] is not None


def test_create_element_in_test_database(pi_web_api_client, test_af_database):
    """Example showing how to create elements in the test database."""
    db_web_id = test_af_database["web_id"]

    # Create a test element
    element_data = {
        "Name": f"TestElement_{int(__import__('time').time())}",
        "Description": "Created by test using test_af_database fixture"
    }

    try:
        result = pi_web_api_client.asset_database.create_element(db_web_id, element_data)
        print(f"\nCreated element: {element_data['Name']}")
        print(f"Element WebId: {result['WebId']}")

        # Cleanup
        pi_web_api_client.element.delete(result["WebId"])
        print(f"Cleaned up element")

        assert result["WebId"] is not None

    except Exception as e:
        pytest.fail(f"Failed to create element: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
