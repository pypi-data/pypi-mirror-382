"""Live integration tests for nested event frame hierarchy creation."""

import pytest
import time
from datetime import datetime, timezone, timedelta
from pi_web_sdk.event_hierarchy import EventFrameHierarchyManager


@pytest.mark.integration
class TestEventFrameHierarchyCreation:
    """Test creating nested event frame hierarchies."""

    def test_create_batch_unit_sub_batch_hierarchy(self, pi_web_api_client, test_af_database):
        """Test creating Batch -> Unit -> SubBatch hierarchy."""
        # Use the configured test database
        db_web_id = test_af_database["web_id"]
        print(f"\nUsing database: {test_af_database['name']} ({test_af_database['path']})")

        # Create manager
        manager = EventFrameHierarchyManager(pi_web_api_client, db_web_id)

        # Set time range
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=2)
        end = now - timedelta(hours=1)

        test_id = f"test_batch_{int(time.time())}"

        # Create paths
        paths = [
            f"{test_id}/Batch_001/ReactorA/Phase1",
            f"{test_id}/Batch_001/ReactorA/Phase2",
            f"{test_id}/Batch_001/ReactorB/Phase1",
            f"{test_id}/Batch_002/ReactorA/Phase1",
        ]

        try:
            results = manager.create_from_paths(
                paths=paths,
                start_time=start.isoformat(),
                end_time=end.isoformat()
            )

            print(f"\nCreated {results['total_count']} event frames:")
            for ef in results["event_frames_created"]:
                indent = "  " * ef["path"].count("/")
                print(f"{indent}{ef['name']}")

            assert results["total_count"] == 10  # root + 2 batches + 3 units + 4 phases

            # Verify root
            root_web_id = results["node_map"][test_id]
            root = pi_web_api_client.event_frame.get(root_web_id)
            assert root["Name"] == test_id

            # Verify children
            children = pi_web_api_client.event_frame.get_child_event_frames(root_web_id)
            child_names = [c["Name"] for c in children.get("Items", [])]
            assert "Batch_001" in child_names
            assert "Batch_002" in child_names

            print(f"\nHierarchy created:")
            print(f"{test_id}/")
            print(f"  - Batch_001/")
            print(f"      - ReactorA/")
            print(f"          - Phase1")
            print(f"          - Phase2")
            print(f"      - ReactorB/")
            print(f"          - Phase1")
            print(f"  - Batch_002/")
            print(f"      - ReactorA/")
            print(f"          - Phase1")

            # Cleanup
            pi_web_api_client.event_frame.delete(root_web_id)
            print(f"\nCleaned up test event frames")

        except Exception as e:
            pytest.fail(f"Failed to create event frame hierarchy: {e}")

    def test_create_batch_hierarchy_with_convenience_method(self, pi_web_api_client):
        """Test using the batch hierarchy convenience method."""
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        manager = EventFrameHierarchyManager(pi_web_api_client, db_web_id)

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=1)
        end = now

        test_id = int(time.time())

        try:
            results = manager.create_batch_hierarchy(
                batches=[f"Batch_{test_id}_A", f"Batch_{test_id}_B"],
                units_per_batch={
                    f"Batch_{test_id}_A": ["Reactor1", "Reactor2"],
                    f"Batch_{test_id}_B": ["Reactor1", "Reactor3"]
                },
                sub_batches_per_unit={
                    "Reactor1": ["Charge", "React", "Discharge"],
                    "Reactor2": ["Charge", "React"],
                    "Reactor3": ["Charge", "React", "Discharge"]
                },
                start_time=start.isoformat(),
                end_time=end.isoformat()
            )

            print(f"\nCreated {results['total_count']} event frames")
            assert results["total_count"] > 0

            # Find a batch to verify
            batch_a_web_id = results["node_map"].get(f"Batch_{test_id}_A")
            if batch_a_web_id:
                batch = pi_web_api_client.event_frame.get(batch_a_web_id)
                assert batch["Name"] == f"Batch_{test_id}_A"
                print(f"Verified batch: {batch['Name']}")

                # Cleanup
                pi_web_api_client.event_frame.delete(batch_a_web_id)

            batch_b_web_id = results["node_map"].get(f"Batch_{test_id}_B")
            if batch_b_web_id:
                pi_web_api_client.event_frame.delete(batch_b_web_id)

            print(f"Cleaned up test batches")

        except Exception as e:
            pytest.fail(f"Failed to create batch hierarchy: {e}")

    def test_verify_event_frame_nesting(self, pi_web_api_client):
        """Verify event frames are properly nested, not flat."""
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        manager = EventFrameHierarchyManager(pi_web_api_client, db_web_id)

        test_id = f"nest_test_{int(time.time())}"
        now = datetime.now(timezone.utc)

        paths = [f"{test_id}/Batch1/Unit1/SubBatch1"]

        try:
            results = manager.create_from_paths(
                paths=paths,
                start_time=now.isoformat()
            )

            print(f"\nVerifying proper nesting:")

            # Get root
            root_web_id = results["node_map"][test_id]
            root = pi_web_api_client.event_frame.get(root_web_id)

            # CRITICAL: Verify name is just the node name, not full path
            assert root["Name"] == test_id, f"Root name should be '{test_id}'"
            print(f"Root: {root['Name']}")

            # Verify Batch1 is child of root
            children = pi_web_api_client.event_frame.get_child_event_frames(root_web_id)
            child_names = [c["Name"] for c in children.get("Items", [])]
            assert "Batch1" in child_names
            print(f"  Child: Batch1")

            # Get Batch1
            batch1_web_id = results["node_map"][f"{test_id}/Batch1"]
            batch1 = pi_web_api_client.event_frame.get(batch1_web_id)
            assert batch1["Name"] == "Batch1"

            # Verify Unit1 is child of Batch1
            batch1_children = pi_web_api_client.event_frame.get_child_event_frames(batch1_web_id)
            unit_names = [c["Name"] for c in batch1_children.get("Items", [])]
            assert "Unit1" in unit_names
            print(f"    Child: Unit1")

            # Get Unit1
            unit1_web_id = results["node_map"][f"{test_id}/Batch1/Unit1"]
            unit1 = pi_web_api_client.event_frame.get(unit1_web_id)
            assert unit1["Name"] == "Unit1"

            # Verify SubBatch1 is child of Unit1
            unit1_children = pi_web_api_client.event_frame.get_child_event_frames(unit1_web_id)
            sub_names = [c["Name"] for c in unit1_children.get("Items", [])]
            assert "SubBatch1" in sub_names
            print(f"      Child: SubBatch1")

            print(f"\nNested structure verified!")
            print(f"{test_id}/")
            print(f"  - Batch1/")
            print(f"      - Unit1/")
            print(f"          - SubBatch1")

            # Cleanup
            pi_web_api_client.event_frame.delete(root_web_id)
            print(f"\nCleaned up test event frames")

        except Exception as e:
            pytest.fail(f"Failed to verify nesting: {e}")

    def test_event_frames_with_time_ranges(self, pi_web_api_client):
        """Test creating event frames with specific time ranges."""
        servers = pi_web_api_client.asset_server.list()
        asset_server = servers["Items"][0]
        dbs = pi_web_api_client.asset_server.get_databases(asset_server["WebId"])
        db_web_id = dbs["Items"][0]["WebId"]

        manager = EventFrameHierarchyManager(pi_web_api_client, db_web_id)

        test_id = f"time_test_{int(time.time())}"
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=3)
        end = now - timedelta(hours=2)

        paths = [f"{test_id}/Batch1/Unit1"]

        try:
            results = manager.create_from_paths(
                paths=paths,
                start_time=start.isoformat(),
                end_time=end.isoformat()
            )

            # Verify time stamps
            root_web_id = results["node_map"][test_id]
            root = pi_web_api_client.event_frame.get(root_web_id)

            assert "StartTime" in root
            assert "EndTime" in root

            print(f"\nEvent frame with time range:")
            print(f"  Name: {root['Name']}")
            print(f"  Start: {root['StartTime']}")
            print(f"  End: {root['EndTime']}")

            # Cleanup
            pi_web_api_client.event_frame.delete(root_web_id)
            print(f"\nCleaned up test event frame")

        except Exception as e:
            pytest.fail(f"Failed to create event frame with time range: {e}")
