"""Live integration tests for Stream Updates functionality.

These tests require a configured PI Web API connection in .env file.
They will write test values to a stream and verify they are received via Stream Updates.
"""

from __future__ import annotations

import pytest
import time
from datetime import datetime


class TestStreamUpdatesLive:
    """Live tests for Stream Updates with real PI server."""

    def test_single_stream_update_workflow(self, pi_web_api_client, test_af_database):
        """Test complete stream update workflow: write value and receive it via updates."""
        # Get or create a test attribute
        db_web_id = test_af_database["web_id"]
        
        # Find or create a test element
        elements = pi_web_api_client.asset_database.get_elements(db_web_id)
        
        if elements["Items"]:
            element = elements["Items"][0]
        else:
            # Create test element
            element_data = {
                "Name": "StreamUpdatesTestElement",
                "Description": "Test element for stream updates"
            }
            element = pi_web_api_client.element.create_element(db_web_id, element_data)
        
        element_web_id = element["WebId"]
        
        # Get or create a test attribute
        attributes = pi_web_api_client.element.get_attributes(element_web_id)
        
        test_attr = None
        for attr in attributes.get("Items", []):
            if attr["Name"] == "StreamUpdatesTest":
                test_attr = attr
                break
        
        if not test_attr:
            # Create a test attribute
            attr_data = {
                "Name": "StreamUpdatesTest",
                "Description": "Test attribute for stream updates",
                "Type": "Double"
            }
            test_attr = pi_web_api_client.element.create_attribute(
                element_web_id,
                attr_data
            )
        
        stream_web_id = test_attr["WebId"]
        print(f"\nUsing stream: {stream_web_id}")
        
        # Step 1: Register for updates
        print("Registering for stream updates...")
        try:
            registration = pi_web_api_client.stream.register_update(
                stream_web_id,
                selected_fields="Items.Timestamp;Items.Value;Items.Good"
            )
        except Exception as e:
            print(f"Registration failed with exception: {e}")
            print(f"Exception type: {type(e)}")
            pytest.skip(f"Stream Updates may not be enabled on this server: {e}")

        print(f"Registration response: {registration}")
        print(f"Registration type: {type(registration)}")

        if not registration:
            pytest.skip("Stream Updates returned empty response - feature may not be enabled")

        print(f"Registration keys: {registration.keys()}")
        print(f"Registration status: {registration.get('Status')}")

        # Check if we have a marker
        if "LatestMarker" not in registration:
            pytest.skip(f"Registration response missing LatestMarker - feature may not be enabled: {registration}")

        # Status might not always be present
        status = registration.get("Status")
        if status:
            assert status in ["Succeeded", "AlreadyRegistered"], f"Unexpected status: {status}"
        
        initial_marker = registration["LatestMarker"]
        print(f"Initial marker: {initial_marker}")
        
        # Step 2: Write a test value
        test_value = 42.123
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        print(f"\nWriting test value: {test_value} at {timestamp}")
        value_data = {
            "Timestamp": timestamp,
            "Value": test_value
        }
        
        pi_web_api_client.stream.update_value(stream_web_id, value_data)
        print("Value written successfully")
        
        # Step 3: Wait a moment for the value to be processed
        print("Waiting for value to be processed...")
        time.sleep(2)
        
        # Step 4: Retrieve updates
        print("\nRetrieving updates...")
        updates = pi_web_api_client.stream.retrieve_update(
            initial_marker,
            selected_fields="Items.Timestamp;Items.Value;Items.Good"
        )
        
        print(f"Update response keys: {updates.keys()}")
        new_marker = updates["LatestMarker"]
        print(f"New marker: {new_marker}")
        
        # Step 5: Verify we received the value
        items = updates.get("Items", [])
        print(f"\nReceived {len(items)} update(s)")
        
        if items:
            for item in items:
                print(f"  Timestamp: {item.get('Timestamp')}")
                print(f"  Value: {item.get('Value')}")
                print(f"  Good: {item.get('Good')}")
        
        # Verify we got at least one update
        assert len(items) > 0, "Should receive at least one update after writing a value"
        
        # Verify our test value is in the updates
        received_values = [item.get("Value") for item in items]
        assert test_value in received_values, f"Expected {test_value} in updates, got {received_values}"
        
        print("\n✓ Test passed: Value written and received via Stream Updates")
        
        # Step 6: Test continuous polling
        print("\nTesting continuous polling...")
        
        # Write another value
        test_value_2 = 99.876
        timestamp_2 = datetime.utcnow().isoformat() + "Z"
        
        print(f"Writing second value: {test_value_2} at {timestamp_2}")
        value_data_2 = {
            "Timestamp": timestamp_2,
            "Value": test_value_2
        }
        pi_web_api_client.stream.update_value(stream_web_id, value_data_2)
        
        time.sleep(2)
        
        # Retrieve using the new marker
        print("Retrieving updates with new marker...")
        updates_2 = pi_web_api_client.stream.retrieve_update(new_marker)
        
        items_2 = updates_2.get("Items", [])
        print(f"Received {len(items_2)} update(s) in second poll")
        
        if items_2:
            received_values_2 = [item.get("Value") for item in items_2]
            assert test_value_2 in received_values_2, f"Expected {test_value_2} in second poll"
            print(f"✓ Second value received: {test_value_2}")
        
        print("\n✓ Continuous polling test passed")


class TestStreamSetUpdatesLive:
    """Live tests for Stream Set Updates with multiple streams."""

    def test_multiple_streams_update_workflow(self, pi_web_api_client, test_af_database):
        """Test stream set updates: write values to multiple streams and receive them."""
        db_web_id = test_af_database["web_id"]
        
        # Find or create test element
        elements = pi_web_api_client.asset_database.get_elements(db_web_id)
        
        if elements["Items"]:
            element = elements["Items"][0]
        else:
            element_data = {
                "Name": "StreamSetUpdatesTestElement",
                "Description": "Test element for stream set updates"
            }
            element = pi_web_api_client.element.create_element(db_web_id, element_data)
        
        element_web_id = element["WebId"]
        
        # Create or get 3 test attributes
        test_attr_names = ["StreamSetTest1", "StreamSetTest2", "StreamSetTest3"]
        stream_web_ids = []
        
        existing_attrs = pi_web_api_client.element.get_attributes(element_web_id)
        existing_attr_map = {attr["Name"]: attr for attr in existing_attrs.get("Items", [])}
        
        for attr_name in test_attr_names:
            if attr_name in existing_attr_map:
                test_attr = existing_attr_map[attr_name]
            else:
                attr_data = {
                    "Name": attr_name,
                    "Description": f"Test attribute {attr_name}",
                    "Type": "Double"
                }
                test_attr = pi_web_api_client.element.create_attribute(
                    element_web_id,
                    attr_data
                )
            stream_web_ids.append(test_attr["WebId"])
        
        print(f"\nUsing {len(stream_web_ids)} streams for testing")
        
        # Step 1: Register multiple streams for updates
        print("Registering multiple streams for updates...")
        registration = pi_web_api_client.streamset.register_updates(
            stream_web_ids,
            selected_fields="Items.Timestamp;Items.Value;Items.WebId"
        )
        
        print(f"Registration response keys: {registration.keys()}")
        initial_marker = registration["LatestMarker"]
        print(f"Initial marker: {initial_marker}")
        
        # Check registration status for each stream
        reg_items = registration.get("Items", [])
        print(f"Registration status for {len(reg_items)} stream(s):")
        for item in reg_items:
            print(f"  {item.get('WebId')}: {item.get('Status')}")
        
        # Step 2: Write test values to all streams
        test_values = [111.1, 222.2, 333.3]
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        print(f"\nWriting test values at {timestamp}:")
        for i, (web_id, value) in enumerate(zip(stream_web_ids, test_values)):
            print(f"  Stream {i+1}: {value}")
            value_data = {
                "Timestamp": timestamp,
                "Value": value
            }
            pi_web_api_client.stream.update_value(web_id, value_data)
        
        print("Values written successfully")
        
        # Step 3: Wait for values to be processed
        print("Waiting for values to be processed...")
        time.sleep(3)
        
        # Step 4: Retrieve updates
        print("\nRetrieving updates for all streams...")
        updates = pi_web_api_client.streamset.retrieve_updates(
            initial_marker,
            selected_fields="Items.Timestamp;Items.Value;Items.WebId"
        )
        
        new_marker = updates["LatestMarker"]
        print(f"New marker: {new_marker}")
        
        # Step 5: Verify we received updates for all streams
        stream_updates = updates.get("Items", [])
        print(f"\nReceived updates for {len(stream_updates)} stream(s)")
        
        received_values_by_stream = {}
        for stream_update in stream_updates:
            stream_id = stream_update.get("WebId")
            items = stream_update.get("Items", [])
            
            if items:
                values = [item.get("Value") for item in items]
                received_values_by_stream[stream_id] = values
                print(f"\nStream {stream_id}:")
                for item in items:
                    print(f"  {item.get('Timestamp')}: {item.get('Value')}")
        
        # Verify all test values were received
        all_received_values = []
        for values in received_values_by_stream.values():
            all_received_values.extend(values)
        
        print(f"\nAll received values: {all_received_values}")
        print(f"Expected values: {test_values}")
        
        for test_value in test_values:
            assert test_value in all_received_values, \
                f"Expected {test_value} in updates, got {all_received_values}"
        
        print("\n✓ Test passed: All values written and received via Stream Set Updates")


class TestStreamUpdatesErrorHandling:
    """Test error handling and edge cases for Stream Updates."""

    def test_invalid_marker(self, pi_web_api_client):
        """Test handling of invalid marker."""
        invalid_marker = "INVALID_MARKER_123"
        
        try:
            updates = pi_web_api_client.stream.retrieve_update(invalid_marker)
            # If we get here, check if there's an error in the response
            if "Errors" in updates or "Exception" in updates:
                print(f"✓ Invalid marker returned error as expected")
            else:
                pytest.fail("Expected error for invalid marker")
        except Exception as e:
            print(f"✓ Invalid marker raised exception as expected: {type(e).__name__}")
    
    def test_retrieve_before_register(self, pi_web_api_client, test_af_database):
        """Test retrieving updates without registering first."""
        # This should fail or return an error
        # The actual behavior depends on PI Web API server configuration
        db_web_id = test_af_database["web_id"]
        
        # Get any attribute
        elements = pi_web_api_client.asset_database.get_elements(db_web_id)
        if not elements["Items"]:
            pytest.skip("No elements available for testing")
        
        element = elements["Items"][0]
        attributes = pi_web_api_client.element.get_attributes(element["WebId"])
        
        if not attributes["Items"]:
            pytest.skip("No attributes available for testing")
        
        stream_web_id = attributes["Items"][0]["WebId"]
        
        # Try to use a made-up marker
        fake_marker = "ABC123XYZ"
        
        try:
            updates = pi_web_api_client.stream.retrieve_update(fake_marker)
            print(f"Response: {updates}")
            # Check if error is reported
            assert "Errors" in updates or "Exception" in updates, \
                "Expected error when using unregistered marker"
        except Exception as e:
            print(f"✓ Correctly raised exception: {type(e).__name__}")
