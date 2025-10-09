"""OMF dataclass models for type-safe OMF operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional, Union


class Classification(Enum):
    """OMF type classifications."""
    DYNAMIC = "dynamic"
    STATIC = "static"


class PropertyType(Enum):
    """OMF property types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class OMFAction(Enum):
    """OMF actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class OMFMessageType(Enum):
    """OMF message types."""
    TYPE = "Type"
    CONTAINER = "Container"
    DATA = "Data"


@dataclass
class OMFProperty:
    """Represents an OMF property definition."""
    type: PropertyType
    description: Optional[str] = None
    format: Optional[str] = None
    is_index: bool = False
    is_name: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OMF property format."""
        result = {
            "type": self.type.value
        }
        
        if self.description:
            result["description"] = self.description
        if self.format:
            result["format"] = self.format
        if self.is_index:
            result["isindex"] = True
        if self.is_name:
            result["isname"] = True
            
        return result


@dataclass
class OMFType:
    """Represents an OMF Type definition."""
    id: str
    classification: Classification
    properties: Dict[str, OMFProperty]
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate the type definition."""
        if self.classification == Classification.DYNAMIC:
            # Dynamic types should have at least one index property (typically timestamp)
            index_props = [p for p in self.properties.values() if p.is_index]
            if not index_props:
                raise ValueError("Dynamic types must have at least one index property")
        
        elif self.classification == Classification.STATIC:
            # Static types should have at least one index or name property
            index_or_name_props = [p for p in self.properties.values() if p.is_index or p.is_name]
            if not index_or_name_props:
                raise ValueError("Static types must have at least one index or name property")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OMF Type message format."""
        result = {
            "id": self.id,
            "type": "object",
            "classification": self.classification.value,
            "properties": {
                name: prop.to_dict() 
                for name, prop in self.properties.items()
            }
        }
        
        if self.description:
            result["description"] = self.description
            
        return result
    
    @classmethod
    def create_dynamic_type(
        cls,
        id: str,
        timestamp_property: str = "timestamp",
        additional_properties: Optional[Dict[str, OMFProperty]] = None,
        description: Optional[str] = None
    ) -> OMFType:
        """Create a dynamic type with timestamp index."""
        properties = {
            timestamp_property: OMFProperty(
                type=PropertyType.STRING,
                format="date-time",
                is_index=True,
                description="Timestamp for time series data"
            )
        }
        
        if additional_properties:
            properties.update(additional_properties)
            
        return cls(
            id=id,
            classification=Classification.DYNAMIC,
            properties=properties,
            description=description
        )
    
    @classmethod
    def create_static_type(
        cls,
        id: str,
        name_property: str = "name",
        additional_properties: Optional[Dict[str, OMFProperty]] = None,
        description: Optional[str] = None
    ) -> OMFType:
        """Create a static type with name index."""
        properties = {
            name_property: OMFProperty(
                type=PropertyType.STRING,
                is_index=True,
                description="Unique identifier for the asset"
            )
        }
        
        if additional_properties:
            properties.update(additional_properties)
            
        return cls(
            id=id,
            classification=Classification.STATIC,
            properties=properties,
            description=description
        )


@dataclass
class OMFContainer:
    """Represents an OMF Container (stream) definition."""
    id: str
    type_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OMF Container message format."""
        result = {
            "id": self.id,
            "typeid": self.type_id
        }
        
        if self.name:
            result["name"] = self.name
        if self.description:
            result["description"] = self.description
        if self.tags:
            result["tags"] = self.tags
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


@dataclass
class OMFAsset:
    """Represents OMF static data (asset) definition."""
    type_id: str
    values: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OMF Data message format for static data."""
        return {
            "typeid": self.type_id,
            "values": self.values
        }
    
    @classmethod
    def create_single_asset(
        cls,
        type_id: str,
        **properties
    ) -> OMFAsset:
        """Create an asset with a single set of property values."""
        return cls(
            type_id=type_id,
            values=[properties]
        )


@dataclass
class OMFTimeSeriesData:
    """Represents OMF time series data."""
    container_id: str
    values: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OMF Data message format for time series."""
        return {
            "containerid": self.container_id,
            "values": self.values
        }
    
    def add_data_point(self, **data) -> None:
        """Add a single data point."""
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.values.append(data)
    
    def add_data_points(self, data_points: List[Dict[str, Any]]) -> None:
        """Add multiple data points."""
        for point in data_points:
            if "timestamp" not in point:
                point["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.values.extend(data_points)


@dataclass
class OMFHierarchyNode:
    """Represents a node in an OMF hierarchy tree."""
    name: str
    type_id: str
    parent: Optional[OMFHierarchyNode] = None
    children: List[OMFHierarchyNode] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    is_leaf: bool = False
    
    def get_full_path(self, separator: str = "/") -> str:
        """Get the full path from root to this node."""
        if self.parent is None:
            return self.name
        return f"{self.parent.get_full_path(separator)}{separator}{self.name}"
    
    def add_child(self, child: OMFHierarchyNode) -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)
    
    def find_child(self, name: str) -> Optional[OMFHierarchyNode]:
        """Find a direct child by name."""
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_all_descendants(self) -> List[OMFHierarchyNode]:
        """Get all descendant nodes."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


@dataclass
class OMFHierarchy:
    """Represents a complete OMF hierarchy tree structure."""
    root_type_id: str
    leaf_type_id: str
    root_nodes: List[OMFHierarchyNode] = field(default_factory=list)
    separator: str = "/"
    
    def create_path(
        self,
        path: str,
        leaf_properties: Optional[Dict[str, Any]] = None,
        intermediate_properties: Optional[Dict[str, Any]] = None
    ) -> OMFHierarchyNode:
        """
        Create a hierarchical path in the tree.
        
        Args:
            path: Path string like "element1/element2/element3"
            leaf_properties: Properties for the leaf node
            intermediate_properties: Properties for intermediate nodes
            
        Returns:
            The leaf node of the created path
        """
        parts = [part.strip() for part in path.split(self.separator) if part.strip()]
        if not parts:
            raise ValueError("Path cannot be empty")
        
        current_node = None
        current_parent = None
        
        # Find or create each level of the hierarchy
        for i, part in enumerate(parts):
            is_leaf = (i == len(parts) - 1)
            type_id = self.leaf_type_id if is_leaf else self.root_type_id
            
            # If this is the first part, check root nodes
            if current_parent is None:
                current_node = None
                for root in self.root_nodes:
                    if root.name == part:
                        current_node = root
                        break
                
                if current_node is None:
                    # Create new root node
                    properties = leaf_properties if is_leaf else intermediate_properties
                    current_node = OMFHierarchyNode(
                        name=part,
                        type_id=type_id,
                        properties=properties or {},
                        is_leaf=is_leaf
                    )
                    self.root_nodes.append(current_node)
            else:
                # Look for existing child
                current_node = current_parent.find_child(part)
                
                if current_node is None:
                    # Create new child node
                    properties = leaf_properties if is_leaf else intermediate_properties
                    current_node = OMFHierarchyNode(
                        name=part,
                        type_id=type_id,
                        properties=properties or {},
                        is_leaf=is_leaf
                    )
                    current_parent.add_child(current_node)
            
            current_parent = current_node
        
        return current_node
    
    def find_node_by_path(self, path: str) -> Optional[OMFHierarchyNode]:
        """Find a node by its path."""
        parts = [part.strip() for part in path.split(self.separator) if part.strip()]
        if not parts:
            return None
        
        # Start from root nodes
        current_node = None
        for root in self.root_nodes:
            if root.name == parts[0]:
                current_node = root
                break
        
        if current_node is None:
            return None
        
        # Navigate down the path
        for part in parts[1:]:
            current_node = current_node.find_child(part)
            if current_node is None:
                return None
        
        return current_node
    
    def get_all_paths(self) -> List[str]:
        """Get all complete paths in the hierarchy."""
        paths = []
        
        def collect_paths(node: OMFHierarchyNode):
            if node.is_leaf or not node.children:
                paths.append(node.get_full_path(self.separator))
            else:
                for child in node.children:
                    collect_paths(child)
        
        for root in self.root_nodes:
            collect_paths(root)
        
        return paths
    
    def get_all_nodes(self) -> List[OMFHierarchyNode]:
        """Get all nodes in the hierarchy."""
        all_nodes = []
        for root in self.root_nodes:
            all_nodes.append(root)
            all_nodes.extend(root.get_all_descendants())
        return all_nodes
    
    def to_omf_assets(self) -> List[OMFAsset]:
        """Convert hierarchy to OMF assets."""
        assets_by_type = {}
        
        for node in self.get_all_nodes():
            if node.type_id not in assets_by_type:
                assets_by_type[node.type_id] = []
            
            # Create asset values with hierarchy information
            asset_values = {
                "name": node.get_full_path(self.separator),
                "display_name": node.name,
                "path": node.get_full_path(self.separator),
                "parent_path": node.parent.get_full_path(self.separator) if node.parent else None,
                "level": len(node.get_full_path(self.separator).split(self.separator)),
                "is_leaf": node.is_leaf,
                **node.properties
            }
            
            assets_by_type[node.type_id].append(asset_values)
        
        # Create OMF assets
        omf_assets = []
        for type_id, values_list in assets_by_type.items():
            asset = OMFAsset(type_id=type_id, values=values_list)
            omf_assets.append(asset)
        
        return omf_assets


@dataclass
class OMFBatch:
    """Represents a batch of OMF messages."""
    types: List[OMFType] = field(default_factory=list)
    containers: List[OMFContainer] = field(default_factory=list)
    assets: List[OMFAsset] = field(default_factory=list)
    time_series: List[OMFTimeSeriesData] = field(default_factory=list)
    hierarchies: List[OMFHierarchy] = field(default_factory=list)
    
    def add_type(self, omf_type: OMFType) -> None:
        """Add an OMF type to the batch."""
        self.types.append(omf_type)
    
    def add_container(self, container: OMFContainer) -> None:
        """Add an OMF container to the batch."""
        self.containers.append(container)
    
    def add_asset(self, asset: OMFAsset) -> None:
        """Add an OMF asset to the batch."""
        self.assets.append(asset)
    
    def add_time_series(self, ts_data: OMFTimeSeriesData) -> None:
        """Add time series data to the batch."""
        self.time_series.append(ts_data)
    
    def add_hierarchy(self, hierarchy: OMFHierarchy) -> None:
        """Add a hierarchy to the batch."""
        self.hierarchies.append(hierarchy)
    
    def get_type_messages(self) -> List[Dict[str, Any]]:
        """Get all type definitions as OMF messages."""
        return [t.to_dict() for t in self.types]
    
    def get_container_messages(self) -> List[Dict[str, Any]]:
        """Get all container definitions as OMF messages."""
        return [c.to_dict() for c in self.containers]
    
    def get_data_messages(self) -> List[Dict[str, Any]]:
        """Get all data (assets + time series + hierarchies) as OMF messages."""
        messages = []
        messages.extend([a.to_dict() for a in self.assets])
        messages.extend([ts.to_dict() for ts in self.time_series])
        
        # Add hierarchy assets
        for hierarchy in self.hierarchies:
            hierarchy_assets = hierarchy.to_omf_assets()
            messages.extend([asset.to_dict() for asset in hierarchy_assets])
        
        return messages
    
    def clear(self) -> None:
        """Clear all messages from the batch."""
        self.types.clear()
        self.containers.clear()
        self.assets.clear()
        self.time_series.clear()
        self.hierarchies.clear()


# Convenience factory functions
def create_sensor_type(
    type_id: str,
    sensor_properties: Dict[str, OMFProperty],
    description: Optional[str] = None
) -> OMFType:
    """Create a sensor type with timestamp and custom properties."""
    return OMFType.create_dynamic_type(
        id=type_id,
        additional_properties=sensor_properties,
        description=description
    )


def create_equipment_type(
    type_id: str,
    equipment_properties: Dict[str, OMFProperty],
    description: Optional[str] = None
) -> OMFType:
    """Create an equipment asset type."""
    return OMFType.create_static_type(
        id=type_id,
        additional_properties=equipment_properties,
        description=description
    )


def create_temperature_sensor_type(type_id: str) -> OMFType:
    """Create a standard temperature sensor type."""
    return create_sensor_type(
        type_id=type_id,
        sensor_properties={
            "temperature": OMFProperty(
                type=PropertyType.NUMBER,
                description="Temperature in Celsius"
            ),
            "humidity": OMFProperty(
                type=PropertyType.NUMBER,
                description="Relative humidity percentage"
            ),
            "quality": OMFProperty(
                type=PropertyType.STRING,
                description="Data quality indicator"
            )
        },
        description="Temperature and humidity sensor"
    )


def create_equipment_asset_type(type_id: str) -> OMFType:
    """Create a standard equipment asset type."""
    return create_equipment_type(
        type_id=type_id,
        equipment_properties={
            "location": OMFProperty(
                type=PropertyType.STRING,
                description="Physical location"
            ),
            "manufacturer": OMFProperty(
                type=PropertyType.STRING,
                description="Equipment manufacturer"
            ),
            "model": OMFProperty(
                type=PropertyType.STRING,
                description="Equipment model"
            ),
            "serialNumber": OMFProperty(
                type=PropertyType.STRING,
                description="Serial number"
            ),
            "installDate": OMFProperty(
                type=PropertyType.STRING,
                format="date-time",
                description="Installation date"
            )
        },
        description="Standard equipment asset"
    )


def create_hierarchy_node_type(type_id: str) -> OMFType:
    """Create a type for hierarchy nodes (folders/containers)."""
    return create_equipment_type(
        type_id=type_id,
        equipment_properties={
            "display_name": OMFProperty(
                type=PropertyType.STRING,
                description="Display name for UI"
            ),
            "path": OMFProperty(
                type=PropertyType.STRING,
                description="Full hierarchical path"
            ),
            "parent_path": OMFProperty(
                type=PropertyType.STRING,
                description="Parent node path"
            ),
            "level": OMFProperty(
                type=PropertyType.INTEGER,
                description="Hierarchy level (depth)"
            ),
            "is_leaf": OMFProperty(
                type=PropertyType.BOOLEAN,
                description="Whether this is a leaf node"
            ),
            "description": OMFProperty(
                type=PropertyType.STRING,
                description="Node description"
            ),
            "node_type": OMFProperty(
                type=PropertyType.STRING,
                description="Type of node (folder, equipment, sensor, etc.)"
            )
        },
        description="Hierarchical tree node"
    )


def create_hierarchy_from_paths(
    paths: List[str],
    root_type_id: str,
    leaf_type_id: str,
    separator: str = "/",
    path_properties: Optional[Dict[str, Dict[str, Any]]] = None
) -> OMFHierarchy:
    """
    Create a complete hierarchy from a list of paths.
    
    Args:
        paths: List of paths like ["plant1/unit1/sensor1", "plant1/unit2/sensor2"]
        root_type_id: Type ID for intermediate nodes
        leaf_type_id: Type ID for leaf nodes
        separator: Path separator (default: "/")
        path_properties: Optional dict mapping paths to properties
        
    Returns:
        Complete OMF hierarchy
    """
    hierarchy = OMFHierarchy(
        root_type_id=root_type_id,
        leaf_type_id=leaf_type_id,
        separator=separator
    )
    
    for path in paths:
        # Get properties for this path
        leaf_props = None
        intermediate_props = None
        
        if path_properties:
            leaf_props = path_properties.get(path, {})
            # For intermediate nodes, use properties from parent paths
            parts = path.split(separator)
            for i in range(len(parts) - 1):
                parent_path = separator.join(parts[:i + 1])
                if parent_path in path_properties:
                    intermediate_props = path_properties[parent_path]
        
        hierarchy.create_path(
            path=path,
            leaf_properties=leaf_props,
            intermediate_properties=intermediate_props
        )
    
    return hierarchy


def create_industrial_hierarchy(
    plants: List[str],
    units_per_plant: Dict[str, List[str]],
    sensors_per_unit: Dict[str, List[str]],
    plant_type_id: str = "PlantType",
    unit_type_id: str = "UnitType", 
    sensor_type_id: str = "SensorType"
) -> OMFHierarchy:
    """
    Create a typical industrial hierarchy: Plant -> Unit -> Sensor.
    
    Args:
        plants: List of plant names
        units_per_plant: Dict mapping plant names to unit lists
        sensors_per_unit: Dict mapping unit names to sensor lists
        plant_type_id: Type ID for plant nodes
        unit_type_id: Type ID for unit nodes
        sensor_type_id: Type ID for sensor nodes
        
    Returns:
        Industrial hierarchy with three levels
    """
    hierarchy = OMFHierarchy(
        root_type_id=plant_type_id,
        leaf_type_id=sensor_type_id
    )
    
    for plant in plants:
        # Create plant node
        plant_node = hierarchy.create_path(
            path=plant,
            intermediate_properties={
                "node_type": "plant",
                "description": f"Manufacturing plant: {plant}"
            }
        )
        
        # Add units to this plant
        if plant in units_per_plant:
            for unit in units_per_plant[plant]:
                unit_path = f"{plant}/{unit}"
                unit_node = hierarchy.create_path(
                    path=unit_path,
                    intermediate_properties={
                        "node_type": "unit",
                        "description": f"Production unit: {unit}"
                    }
                )
                
                # Add sensors to this unit
                if unit in sensors_per_unit:
                    for sensor in sensors_per_unit[unit]:
                        sensor_path = f"{plant}/{unit}/{sensor}"
                        hierarchy.create_path(
                            path=sensor_path,
                            leaf_properties={
                                "node_type": "sensor",
                                "description": f"Sensor: {sensor}",
                                "data_type": "measurement"
                            }
                        )
    
    return hierarchy


__all__ = [
    'OMFType',
    'OMFProperty', 
    'OMFContainer',
    'OMFAsset',
    'OMFTimeSeriesData',
    'OMFBatch',
    'OMFHierarchy',
    'OMFHierarchyNode',
    'Classification',
    'PropertyType',
    'OMFAction',
    'OMFMessageType',
    'create_sensor_type',
    'create_equipment_type',
    'create_temperature_sensor_type',
    'create_equipment_asset_type',
    'create_hierarchy_node_type',
    'create_hierarchy_from_paths',
    'create_industrial_hierarchy',
]
