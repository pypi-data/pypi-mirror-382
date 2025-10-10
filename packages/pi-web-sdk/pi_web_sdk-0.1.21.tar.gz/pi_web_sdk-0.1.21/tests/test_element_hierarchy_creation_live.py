"""Live integration tests for creating element hierarchies using direct methods."""

import pytest
import time


@pytest.mark.integration
class TestElementHierarchyCreation:
    """Test creating complete element hierarchies without OMF."""

    def test_create_industrial_hierarchy_direct(self, pi_web_api_client):
        """Test creating Plant -> Area -> Line -> Sensor hierarchy."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_created = []

        try:
            # Create Plant (Level 1 - Root)
            plant = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": f"Plant_{test_id}",
                "Description": "Test manufacturing plant"
            })
            plant_web_id = plant["WebId"]
            elements_created.insert(0, plant_web_id)

            # Verify plant was created
            retrieved_plant = pi_web_api_client.element.get(plant_web_id)
            assert retrieved_plant["Name"] == f"Plant_{test_id}"
            print(f"\n✓ Created Plant: {retrieved_plant['Name']}")

            # Create Areas (Level 2)
            area1 = pi_web_api_client.element.create_element(plant_web_id, {
                "Name": "Area_A",
                "Description": "Production Area A"
            })
            area2 = pi_web_api_client.element.create_element(plant_web_id, {
                "Name": "Area_B",
                "Description": "Production Area B"
            })
            elements_created.insert(0, area1["WebId"])
            elements_created.insert(0, area2["WebId"])

            print(f"  ✓ Created Areas: Area_A, Area_B")

            # Verify areas are children of plant
            children = pi_web_api_client.element.get_elements(plant_web_id)
            child_names = [c["Name"] for c in children.get("Items", [])]
            assert "Area_A" in child_names
            assert "Area_B" in child_names

            # Create Lines under Area_A (Level 3)
            line1 = pi_web_api_client.element.create_element(area1["WebId"], {
                "Name": "Line_1",
                "Description": "Assembly Line 1"
            })
            line2 = pi_web_api_client.element.create_element(area1["WebId"], {
                "Name": "Line_2",
                "Description": "Assembly Line 2"
            })
            elements_created.insert(0, line1["WebId"])
            elements_created.insert(0, line2["WebId"])

            print(f"    ✓ Created Lines: Line_1, Line_2 under Area_A")

            # Create Sensors under Line_1 (Level 4)
            sensor1 = pi_web_api_client.element.create_element(line1["WebId"], {
                "Name": "TempSensor_1",
                "Description": "Temperature sensor"
            })
            sensor2 = pi_web_api_client.element.create_element(line1["WebId"], {
                "Name": "PressureSensor_1",
                "Description": "Pressure sensor"
            })
            elements_created.insert(0, sensor1["WebId"])
            elements_created.insert(0, sensor2["WebId"])

            print(f"      ✓ Created Sensors: TempSensor_1, PressureSensor_1 under Line_1")

            # Verify complete hierarchy
            line_children = pi_web_api_client.element.get_elements(line1["WebId"])
            sensor_names = [s["Name"] for s in line_children.get("Items", [])]
            assert "TempSensor_1" in sensor_names
            assert "PressureSensor_1" in sensor_names

            print(f"\n✓ Complete hierarchy verified:")
            print(f"  Plant_{test_id}")
            print(f"    └─ Area_A")
            print(f"         └─ Line_1")
            print(f"              ├─ TempSensor_1")
            print(f"              └─ PressureSensor_1")
            print(f"    └─ Area_B")

            # Cleanup (delete from leaf to root)
            for web_id in elements_created:
                pi_web_api_client.element.delete(web_id)
            print(f"\n✓ Cleaned up {len(elements_created)} elements")

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_created:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to create hierarchy: {e}")

    def test_create_multiple_parallel_hierarchies(self, pi_web_api_client):
        """Test creating multiple parallel hierarchies in same database."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_created = []

        try:
            # Create three parallel plant hierarchies
            plants = []
            for i in range(1, 4):
                plant = pi_web_api_client.asset_database.create_element(db_web_id, {
                    "Name": f"Plant_{test_id}_{i}",
                    "Description": f"Test plant {i}"
                })
                plants.append(plant["WebId"])
                elements_created.insert(0, plant["WebId"])

                # Add unit under each plant
                unit = pi_web_api_client.element.create_element(plant["WebId"], {
                    "Name": f"Unit_{i}",
                    "Description": f"Processing unit {i}"
                })
                elements_created.insert(0, unit["WebId"])

            print(f"\n✓ Created {len(plants)} parallel plant hierarchies")

            # Verify all plants exist at root level
            root_elements = pi_web_api_client.asset_database.get_elements(
                db_web_id,
                name_filter=f"Plant_{test_id}_*"
            )
            assert len(root_elements.get("Items", [])) == 3

            # Cleanup
            for web_id in elements_created:
                pi_web_api_client.element.delete(web_id)
            print(f"✓ Cleaned up {len(elements_created)} elements")

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_created:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to create parallel hierarchies: {e}")

    def test_create_hierarchy_with_attributes(self, pi_web_api_client):
        """Test creating hierarchy where elements have attributes."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_created = []

        try:
            # Create Equipment with attributes
            equipment = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": f"Pump_{test_id}",
                "Description": "Centrifugal pump"
            })
            equipment_web_id = equipment["WebId"]
            elements_created.insert(0, equipment_web_id)

            # Add multiple attributes
            attributes = [
                {"Name": "FlowRate", "Type": "Double", "Description": "Flow rate in m3/h"},
                {"Name": "Pressure", "Type": "Double", "Description": "Pressure in bar"},
                {"Name": "Temperature", "Type": "Double", "Description": "Temperature in C"},
                {"Name": "Status", "Type": "String", "Description": "Operational status"}
            ]

            for attr_data in attributes:
                pi_web_api_client.element.create_attribute(equipment_web_id, attr_data)

            # Verify attributes were created
            attrs = pi_web_api_client.element.get_attributes(equipment_web_id)
            attr_names = [a["Name"] for a in attrs.get("Items", [])]

            print(f"\n✓ Created Pump_{test_id} with {len(attr_names)} attributes:")
            for name in attr_names:
                print(f"    - {name}")

            assert "FlowRate" in attr_names
            assert "Pressure" in attr_names
            assert "Temperature" in attr_names
            assert "Status" in attr_names

            # Cleanup
            pi_web_api_client.element.delete(equipment_web_id)
            print(f"✓ Cleaned up equipment")

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_created:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to create hierarchy with attributes: {e}")

    def test_create_deep_hierarchy(self, pi_web_api_client):
        """Test creating a deep hierarchy (6+ levels)."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_created = []

        try:
            # Create 7-level hierarchy: Enterprise -> Site -> Plant -> Area -> Line -> Equipment -> Sensor
            levels = [
                (None, "Enterprise", f"Enterprise_{test_id}"),
                ("Enterprise", "Site", "Site_North"),
                ("Site", "Plant", "Plant_1"),
                ("Plant", "Area", "Area_Production"),
                ("Area", "Line", "Line_Assembly"),
                ("Line", "Equipment", "Robot_A01"),
                ("Equipment", "Sensor", "VibrationSensor")
            ]

            parent_web_id = db_web_id
            level_webids = {}

            for parent_level, level_name, element_name in levels:
                if parent_level is None:
                    # Root element
                    elem = pi_web_api_client.asset_database.create_element(parent_web_id, {
                        "Name": element_name,
                        "Description": f"{level_name} level"
                    })
                else:
                    # Child element
                    elem = pi_web_api_client.element.create_element(parent_web_id, {
                        "Name": element_name,
                        "Description": f"{level_name} level"
                    })

                level_webids[level_name] = elem["WebId"]
                elements_created.insert(0, elem["WebId"])
                parent_web_id = elem["WebId"]

                print(f"{'  ' * len([l for l in levels if l[0] is not None and levels.index(l) < levels.index((parent_level, level_name, element_name))])}✓ {element_name}")

            # Verify deepest element
            deepest = pi_web_api_client.element.get(level_webids["Sensor"])
            assert deepest["Name"] == "VibrationSensor"

            print(f"\n✓ Created 7-level hierarchy with {len(elements_created)} elements")

            # Cleanup
            for web_id in elements_created:
                pi_web_api_client.element.delete(web_id)
            print(f"✓ Cleaned up all elements")

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_created:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to create deep hierarchy: {e}")

    def test_batch_create_siblings(self, pi_web_api_client):
        """Test creating many sibling elements at same level."""
        # Get database
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        test_id = int(time.time())
        elements_created = []

        try:
            # Create parent
            parent = pi_web_api_client.asset_database.create_element(db_web_id, {
                "Name": f"SensorArray_{test_id}",
                "Description": "Array of sensors"
            })
            parent_web_id = parent["WebId"]
            elements_created.insert(0, parent_web_id)

            # Create 20 sibling sensors
            num_sensors = 20
            for i in range(1, num_sensors + 1):
                sensor = pi_web_api_client.element.create_element(parent_web_id, {
                    "Name": f"Sensor_{i:03d}",
                    "Description": f"Temperature sensor {i}"
                })
                elements_created.insert(0, sensor["WebId"])

            # Verify all siblings
            children = pi_web_api_client.element.get_elements(parent_web_id)
            assert len(children.get("Items", [])) == num_sensors

            print(f"\n✓ Created {num_sensors} sibling sensors under SensorArray_{test_id}")
            print(f"  Sample: {children['Items'][0]['Name']}, {children['Items'][1]['Name']}, ...")

            # Cleanup
            for web_id in elements_created:
                pi_web_api_client.element.delete(web_id)
            print(f"✓ Cleaned up {len(elements_created)} elements")

        except Exception as e:
            # Cleanup on failure
            for web_id in elements_created:
                try:
                    pi_web_api_client.element.delete(web_id)
                except:
                    pass
            pytest.fail(f"Failed to batch create siblings: {e}")
