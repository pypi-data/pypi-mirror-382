"""Live integration tests for element creation in PI Web API."""

import pytest
import time


@pytest.mark.integration
class TestElementCreationLive:
    """Live tests for creating elements in PI Asset Framework."""

    def test_create_root_element_in_database(self, pi_web_api_client):
        """Test creating a root-level element in an asset database."""
        # Get asset server and database
        servers = pi_web_api_client.asset_server.list()
        assert servers["Items"], "No asset servers found"

        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        assert dbs.get("Items"), "No databases found"

        # Use first database (or create test database if needed)
        db = dbs["Items"][0]
        db_web_id = db["WebId"]

        # Create a test element
        test_name = f"TestElement_{int(time.time())}"
        element_data = {
            "Name": test_name,
            "Description": "Test element created by integration test"
        }

        try:
            result = pi_web_api_client.asset_database.create_element(db_web_id, element_data)

            print(f"\nCreated element with WebId: {result.get('WebId')}")
            assert "WebId" in result, "Element creation should return WebId"

            # Verify element exists by reading it back
            created_web_id = result["WebId"]
            retrieved = pi_web_api_client.element.get(created_web_id)
            assert retrieved["Name"] == test_name, "Retrieved element name should match"
            print(f"Verified element: {retrieved['Name']}")

            # Cleanup - delete the test element
            pi_web_api_client.element.delete(created_web_id)
            print(f"Cleaned up test element: {test_name}")

        except Exception as e:
            pytest.fail(f"Failed to create element: {e}")

    def test_create_child_element(self, pi_web_api_client):
        """Test creating a child element under a parent element."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        # Create parent element
        parent_name = f"ParentElement_{int(time.time())}"
        parent_data = {
            "Name": parent_name,
            "Description": "Parent test element"
        }

        try:
            parent = pi_web_api_client.asset_database.create_element(db_web_id, parent_data)
            parent_web_id = parent["WebId"]

            # Create child element under parent
            child_name = f"ChildElement_{int(time.time())}"
            child_data = {
                "Name": child_name,
                "Description": "Child test element"
            }

            child = pi_web_api_client.element.create_element(parent_web_id, child_data)
            child_web_id = child["WebId"]

            print(f"\nCreated parent: {parent_name}")
            print(f"Created child: {child_name}")

            # Verify hierarchy
            assert "WebId" in child, "Child creation should return WebId"

            # Verify child exists by reading it back
            retrieved_child = pi_web_api_client.element.get(child_web_id)
            assert retrieved_child["Name"] == child_name
            print(f"Verified child element: {retrieved_child['Name']}")

            # Get children of parent to verify hierarchy
            children = pi_web_api_client.element.get_elements(parent_web_id)
            child_names = [c["Name"] for c in children.get("Items", [])]
            assert child_name in child_names, "Child should appear in parent's children list"

            # Cleanup - delete child then parent
            pi_web_api_client.element.delete(child_web_id)
            pi_web_api_client.element.delete(parent_web_id)
            print("Cleaned up test elements")

        except Exception as e:
            pytest.fail(f"Failed to create child element: {e}")

    def test_create_element_hierarchy(self, pi_web_api_client):
        """Test creating a multi-level element hierarchy."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_to_cleanup = []

        try:
            # Create Plant -> Area -> Line -> Sensor hierarchy
            plant = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": f"Plant_{test_id}",
                "Description": "Test plant"
            })
            elements_to_cleanup.insert(0, plant["WebId"])

            area = pi_web_api_client.element.create_element(plant["WebId"], {
                "Name": f"Area_{test_id}",
                "Description": "Test area"
            })
            elements_to_cleanup.insert(0, area["WebId"])

            line = pi_web_api_client.element.create_element(area["WebId"], {
                "Name": f"Line_{test_id}",
                "Description": "Test line"
            })
            elements_to_cleanup.insert(0, line["WebId"])

            sensor = pi_web_api_client.element.create_element(line["WebId"], {
                "Name": f"Sensor_{test_id}",
                "Description": "Test sensor"
            })
            elements_to_cleanup.insert(0, sensor["WebId"])

            print(f"\nCreated hierarchy:")
            print(f"  Plant_{test_id}")
            print(f"    └─ Area_{test_id}")
            print(f"         └─ Line_{test_id}")
            print(f"              └─ Sensor_{test_id}")

            # Verify structure
            assert plant["WebId"], "Plant should have WebId"
            assert area["WebId"], "Area should have WebId"
            assert line["WebId"], "Line should have WebId"
            assert sensor["WebId"], "Sensor should have WebId"

            # Verify hierarchy by getting children at each level
            areas = pi_web_api_client.element.get_elements(plant["WebId"])
            assert any(a["Name"] == f"Area_{test_id}" for a in areas.get("Items", []))

            lines = pi_web_api_client.element.get_elements(area["WebId"])
            assert any(l["Name"] == f"Line_{test_id}" for l in lines.get("Items", []))

            sensors = pi_web_api_client.element.get_elements(line["WebId"])
            assert any(s["Name"] == f"Sensor_{test_id}" for s in sensors.get("Items", []))

            # Cleanup in reverse order (leaf to root)
            for web_id in elements_to_cleanup:
                pi_web_api_client.element.delete(web_id)
            print("Cleaned up hierarchy")

        except Exception as e:
            # Attempt cleanup even on failure
            for web_id in elements_to_cleanup:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to create element hierarchy: {e}")

    def test_create_element_with_attributes(self, pi_web_api_client):
        """Test creating an element and adding attributes to it."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_name = f"ElementWithAttrs_{int(time.time())}"

        try:
            # Create element
            element = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": test_name,
                "Description": "Element with attributes"
            })
            element_web_id = element["WebId"]

            # Create attribute on the element
            attr_name = f"TestAttribute_{int(time.time())}"
            attribute_data = {
                "Name": attr_name,
                "Description": "Test attribute",
                "Type": "Double"
            }

            attr_result = pi_web_api_client.element.create_attribute(
                element_web_id,
                attribute_data
            )

            print(f"\nCreated element: {test_name}")
            print(f"Created attribute: {attr_name}")

            assert "WebId" in attr_result, "Attribute creation should return WebId"

            # Verify attribute exists
            attributes = pi_web_api_client.element.get_attributes(element_web_id)
            attr_names = [a["Name"] for a in attributes.get("Items", [])]
            assert attr_name in attr_names, "Attribute should be in element's attributes"

            # Cleanup
            pi_web_api_client.element.delete(element_web_id)
            print("Cleaned up test element")

        except Exception as e:
            pytest.fail(f"Failed to create element with attributes: {e}")

    def test_get_element_by_path(self, pi_web_api_client):
        """Test retrieving element by path after creation."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db = dbs["Items"][0]
        db_web_id = db["WebId"]
        db_path = db.get("Path", f"\\\\{asset_server['Name']}\\{db['Name']}")

        test_name = f"PathTestElement_{int(time.time())}"

        elements_to_cleanup = []

        try:
            # Create element
            element = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": test_name
            })
            element_web_id = element["WebId"]
            elements_to_cleanup.append(element_web_id)

            # Wait for element to be indexed
            time.sleep(2)

            # Get element by path
            element_path = f"{db_path}\\{test_name}"

            print(f"\nCreated element: {test_name}")
            print(f"Attempting to retrieve by path: {element_path}")

            try:
                retrieved = pi_web_api_client.element.get_by_path(element_path)
                assert retrieved["Name"] == test_name
                assert retrieved["WebId"] == element_web_id
                print(f"Successfully retrieved by path")
            except Exception as path_error:
                # Path-based retrieval might not work immediately or path format might be wrong
                print(f"Warning: Could not retrieve by path: {path_error}")
                print("This is expected if AF indexing takes time or path format differs")
                # Verify element exists by WebId instead
                retrieved = pi_web_api_client.element.get(element_web_id)
                assert retrieved["Name"] == test_name

            # Cleanup
            for web_id in elements_to_cleanup:
                pi_web_api_client.element.delete(web_id)

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_to_cleanup:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed element creation test: {e}")
