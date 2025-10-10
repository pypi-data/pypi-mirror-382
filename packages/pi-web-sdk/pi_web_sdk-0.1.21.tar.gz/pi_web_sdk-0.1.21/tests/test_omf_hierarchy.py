"""Tests for OMF hierarchy creation functionality."""

import pytest
from pi_web_sdk.models.omf import (
    OMFHierarchy, OMFHierarchyNode,
    create_hierarchy_node_type, create_hierarchy_from_paths, create_industrial_hierarchy
)
from pi_web_sdk.controllers.omf import OMFManager


class TestOMFHierarchyNode:
    """Test OMF Hierarchy Node functionality."""
    
    def test_node_creation(self):
        """Test creating a hierarchy node."""
        node = OMFHierarchyNode(
            name="Plant1",
            type_id="PlantType",
            properties={"location": "Texas", "capacity": 1000},
            is_leaf=False
        )
        
        assert node.name == "Plant1"
        assert node.type_id == "PlantType"
        assert node.properties["location"] == "Texas"
        assert node.is_leaf is False
        assert node.parent is None
        assert len(node.children) == 0
    
    def test_node_path_generation(self):
        """Test generating full paths."""
        root = OMFHierarchyNode(name="Plant1", type_id="PlantType")
        unit = OMFHierarchyNode(name="Unit1", type_id="UnitType")
        sensor = OMFHierarchyNode(name="Sensor1", type_id="SensorType", is_leaf=True)
        
        root.add_child(unit)
        unit.add_child(sensor)
        
        assert root.get_full_path() == "Plant1"
        assert unit.get_full_path() == "Plant1/Unit1"
        assert sensor.get_full_path() == "Plant1/Unit1/Sensor1"
    
    def test_node_path_with_custom_separator(self):
        """Test path generation with custom separator."""
        root = OMFHierarchyNode(name="Plant1", type_id="PlantType")
        unit = OMFHierarchyNode(name="Unit1", type_id="UnitType")
        
        root.add_child(unit)
        
        assert unit.get_full_path("\\") == "Plant1\\Unit1"
        assert unit.get_full_path(".") == "Plant1.Unit1"
    
    def test_find_child(self):
        """Test finding child nodes."""
        parent = OMFHierarchyNode(name="Parent", type_id="ParentType")
        child1 = OMFHierarchyNode(name="Child1", type_id="ChildType")
        child2 = OMFHierarchyNode(name="Child2", type_id="ChildType")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        found = parent.find_child("Child1")
        assert found is not None
        assert found.name == "Child1"
        
        not_found = parent.find_child("Child3")
        assert not_found is None
    
    def test_get_all_descendants(self):
        """Test getting all descendant nodes."""
        root = OMFHierarchyNode(name="Root", type_id="RootType")
        child1 = OMFHierarchyNode(name="Child1", type_id="ChildType")
        child2 = OMFHierarchyNode(name="Child2", type_id="ChildType")
        grandchild = OMFHierarchyNode(name="GrandChild", type_id="GrandChildType")
        
        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild)
        
        descendants = root.get_all_descendants()
        assert len(descendants) == 3
        assert child1 in descendants
        assert child2 in descendants
        assert grandchild in descendants


class TestOMFHierarchy:
    """Test OMF Hierarchy functionality."""
    
    def test_hierarchy_creation(self):
        """Test creating a basic hierarchy."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        assert hierarchy.root_type_id == "ContainerType"
        assert hierarchy.leaf_type_id == "SensorType"
        assert hierarchy.separator == "/"
        assert len(hierarchy.root_nodes) == 0
    
    def test_single_path_creation(self):
        """Test creating a single path."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        leaf_node = hierarchy.create_path(
            "Plant1/Unit1/Sensor1",
            leaf_properties={"sensor_type": "temperature"},
            intermediate_properties={"facility_type": "manufacturing"}
        )
        
        assert leaf_node.name == "Sensor1"
        assert leaf_node.is_leaf is True
        assert leaf_node.type_id == "SensorType"
        assert leaf_node.properties["sensor_type"] == "temperature"
        
        # Check path structure
        assert leaf_node.get_full_path() == "Plant1/Unit1/Sensor1"
        assert leaf_node.parent.name == "Unit1"
        assert leaf_node.parent.parent.name == "Plant1"
    
    def test_multiple_paths_with_shared_nodes(self):
        """Test creating multiple paths that share intermediate nodes."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        # Create first path
        sensor1 = hierarchy.create_path("Plant1/Unit1/Sensor1")
        
        # Create second path sharing Plant1 and Unit1
        sensor2 = hierarchy.create_path("Plant1/Unit1/Sensor2")
        
        # Create third path sharing only Plant1
        sensor3 = hierarchy.create_path("Plant1/Unit2/Sensor3")
        
        # Verify structure
        assert len(hierarchy.root_nodes) == 1  # Only one Plant1
        plant1 = hierarchy.root_nodes[0]
        assert plant1.name == "Plant1"
        assert len(plant1.children) == 2  # Unit1 and Unit2
        
        unit1 = plant1.find_child("Unit1")
        assert len(unit1.children) == 2  # Sensor1 and Sensor2
        
        unit2 = plant1.find_child("Unit2")
        assert len(unit2.children) == 1  # Sensor3
    
    def test_find_node_by_path(self):
        """Test finding nodes by path."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        hierarchy.create_path("Plant1/Unit1/Sensor1")
        hierarchy.create_path("Plant1/Unit2/Sensor2")
        
        # Find existing nodes
        sensor1 = hierarchy.find_node_by_path("Plant1/Unit1/Sensor1")
        assert sensor1 is not None
        assert sensor1.name == "Sensor1"
        
        unit1 = hierarchy.find_node_by_path("Plant1/Unit1")
        assert unit1 is not None
        assert unit1.name == "Unit1"
        
        # Try to find non-existent node
        not_found = hierarchy.find_node_by_path("Plant1/Unit3/Sensor3")
        assert not_found is None
    
    def test_get_all_paths(self):
        """Test getting all complete paths."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        hierarchy.create_path("Plant1/Unit1/Sensor1")
        hierarchy.create_path("Plant1/Unit1/Sensor2")
        hierarchy.create_path("Plant1/Unit2/Sensor3")
        hierarchy.create_path("Plant2/Unit1/Sensor4")
        
        all_paths = hierarchy.get_all_paths()
        expected_paths = [
            "Plant1/Unit1/Sensor1",
            "Plant1/Unit1/Sensor2",
            "Plant1/Unit2/Sensor3",
            "Plant2/Unit1/Sensor4"
        ]
        
        assert len(all_paths) == 4
        for path in expected_paths:
            assert path in all_paths
    
    def test_get_all_nodes(self):
        """Test getting all nodes in hierarchy."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        hierarchy.create_path("Plant1/Unit1/Sensor1")
        hierarchy.create_path("Plant1/Unit2/Sensor2")
        
        all_nodes = hierarchy.get_all_nodes()
        assert len(all_nodes) == 5  # Plant1, Unit1, Unit2, Sensor1, Sensor2
        
        node_names = [node.name for node in all_nodes]
        assert "Plant1" in node_names
        assert "Unit1" in node_names
        assert "Unit2" in node_names
        assert "Sensor1" in node_names
        assert "Sensor2" in node_names
    
    def test_to_omf_assets(self):
        """Test converting hierarchy to OMF assets."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        hierarchy.create_path(
            "Plant1/Unit1/Sensor1",
            leaf_properties={"sensor_model": "TH-3000"},
            intermediate_properties={"facility_code": "FAC001"}
        )
        
        omf_assets = hierarchy.to_omf_assets()
        
        # Should have assets for both ContainerType and SensorType
        assert len(omf_assets) == 2
        
        # Find assets by type
        container_asset = None
        sensor_asset = None
        
        for asset in omf_assets:
            if asset.type_id == "ContainerType":
                container_asset = asset
            elif asset.type_id == "SensorType":
                sensor_asset = asset
        
        assert container_asset is not None
        assert sensor_asset is not None
        
        # Check container asset structure
        assert len(container_asset.values) == 2  # Plant1 and Unit1
        
        # Check sensor asset structure
        assert len(sensor_asset.values) == 1  # Sensor1
        sensor_values = sensor_asset.values[0]
        assert sensor_values["name"] == "Plant1/Unit1/Sensor1"
        assert sensor_values["display_name"] == "Sensor1"
        assert sensor_values["path"] == "Plant1/Unit1/Sensor1"
        assert sensor_values["is_leaf"] is True
        assert sensor_values["sensor_model"] == "TH-3000"
    
    def test_custom_separator(self):
        """Test hierarchy with custom path separator."""
        hierarchy = OMFHierarchy(
            root_type_id="ContainerType",
            leaf_type_id="SensorType",
            separator="\\"
        )
        
        node = hierarchy.create_path("Plant1\\Unit1\\Sensor1")
        
        assert node.get_full_path("\\") == "Plant1\\Unit1\\Sensor1"
        
        found = hierarchy.find_node_by_path("Plant1\\Unit1\\Sensor1")
        assert found is not None
        assert found.name == "Sensor1"


class TestHierarchyConvenienceFunctions:
    """Test hierarchy convenience functions."""
    
    def test_create_hierarchy_node_type(self):
        """Test creating hierarchy node type."""
        node_type = create_hierarchy_node_type("HierarchyNodeType")
        
        assert node_type.id == "HierarchyNodeType"
        assert "display_name" in node_type.properties
        assert "path" in node_type.properties
        assert "parent_path" in node_type.properties
        assert "level" in node_type.properties
        assert "is_leaf" in node_type.properties
    
    def test_create_hierarchy_from_paths(self):
        """Test creating hierarchy from path list."""
        paths = [
            "Plant1/Unit1/Sensor1",
            "Plant1/Unit1/Sensor2", 
            "Plant1/Unit2/Sensor3",
            "Plant2/Unit1/Sensor4"
        ]
        
        hierarchy = create_hierarchy_from_paths(
            paths=paths,
            root_type_id="ContainerType",
            leaf_type_id="SensorType"
        )
        
        assert len(hierarchy.root_nodes) == 2  # Plant1 and Plant2
        
        all_paths = hierarchy.get_all_paths()
        assert len(all_paths) == 4
        for path in paths:
            assert path in all_paths
    
    def test_create_hierarchy_from_paths_with_properties(self):
        """Test creating hierarchy with specific path properties."""
        paths = ["Plant1/Unit1/Sensor1", "Plant1/Unit2/Sensor2"]
        
        path_properties = {
            "Plant1": {"facility_type": "manufacturing", "location": "Texas"},
            "Plant1/Unit1/Sensor1": {"sensor_type": "temperature", "model": "TH-3000"},
            "Plant1/Unit2/Sensor2": {"sensor_type": "pressure", "model": "PR-2000"}
        }
        
        hierarchy = create_hierarchy_from_paths(
            paths=paths,
            root_type_id="ContainerType",
            leaf_type_id="SensorType",
            path_properties=path_properties
        )
        
        plant1 = hierarchy.find_node_by_path("Plant1")
        assert plant1.properties["facility_type"] == "manufacturing"
        
        sensor1 = hierarchy.find_node_by_path("Plant1/Unit1/Sensor1")
        assert sensor1.properties["sensor_type"] == "temperature"
        assert sensor1.properties["model"] == "TH-3000"
    
    def test_create_industrial_hierarchy(self):
        """Test creating industrial hierarchy."""
        plants = ["PlantA", "PlantB"]
        units_per_plant = {
            "PlantA": ["Unit1", "Unit2"],
            "PlantB": ["Unit1", "Unit3"]
        }
        sensors_per_unit = {
            "Unit1": ["TempSensor", "PressureSensor"],
            "Unit2": ["FlowSensor"],
            "Unit3": ["VibrationSensor"]
        }
        
        hierarchy = create_industrial_hierarchy(
            plants=plants,
            units_per_plant=units_per_plant,
            sensors_per_unit=sensors_per_unit
        )
        
        # Verify structure
        assert len(hierarchy.root_nodes) == 2  # PlantA and PlantB
        
        # Check PlantA structure
        plantA = hierarchy.find_node_by_path("PlantA")
        assert plantA is not None
        assert len(plantA.children) == 2  # Unit1 and Unit2
        
        # Check sensors in PlantA/Unit1
        temp_sensor = hierarchy.find_node_by_path("PlantA/Unit1/TempSensor")
        assert temp_sensor is not None
        assert temp_sensor.is_leaf is True
        assert temp_sensor.properties["node_type"] == "sensor"
        
        pressure_sensor = hierarchy.find_node_by_path("PlantA/Unit1/PressureSensor")
        assert pressure_sensor is not None
        
        # Check PlantB structure
        plantB = hierarchy.find_node_by_path("PlantB")
        assert plantB is not None
        
        vib_sensor = hierarchy.find_node_by_path("PlantB/Unit3/VibrationSensor")
        assert vib_sensor is not None


class TestOMFManagerHierarchy:
    """Test OMF Manager hierarchy methods."""
    
    @pytest.fixture
    def mock_omf_manager(self):
        """Create a mock OMF manager for testing."""
        class MockOMFController:
            def post_async(self, **kwargs):
                return {"status": "success", "kwargs": kwargs}
        
        class MockDataServerController:
            def list(self):
                return {"Items": [{"WebId": "test-server-id", "Name": "Test Server"}]}
            
            def get(self, web_id):
                return {"WebId": web_id, "Name": "Test Server"}
        
        class MockClient:
            def __init__(self):
                self.omf = MockOMFController()
                self.data_server = MockDataServerController()
        
        return OMFManager(MockClient())
    
    def test_create_hierarchy_from_paths_with_manager(self, mock_omf_manager):
        """Test creating hierarchy from paths using manager."""
        paths = ["Plant1/Unit1/Sensor1", "Plant1/Unit2/Sensor2"]

        results = mock_omf_manager.create_hierarchy_from_paths(
            paths=paths,
            root_type_id="ContainerType",
            leaf_type_id="SensorType",
            create_types=False,
            use_af_elements=False  # Use OMF assets instead of AF elements for mock
        )
        
        assert isinstance(results, dict)
        # Should have created assets for both container and sensor types
        assert len(results) >= 1
    
    def test_create_industrial_hierarchy_with_manager(self, mock_omf_manager):
        """Test creating industrial hierarchy using manager."""
        results = mock_omf_manager.create_industrial_hierarchy(
            plants=["PlantA"],
            units_per_plant={"PlantA": ["Unit1"]},
            sensors_per_unit={"Unit1": ["Sensor1"]},
            create_types=False,
            use_af_elements=False  # Use OMF assets instead of AF elements for mock
        )
        
        assert isinstance(results, dict)
    
    def test_add_path_to_existing_hierarchy(self, mock_omf_manager):
        """Test adding a path to existing hierarchy."""
        results = mock_omf_manager.add_path_to_existing_hierarchy(
            path="NewPlant/NewUnit/NewSensor",
            root_type_id="ContainerType",
            leaf_type_id="SensorType",
            leaf_properties={"sensor_type": "temperature"}
        )
        
        assert isinstance(results, dict)