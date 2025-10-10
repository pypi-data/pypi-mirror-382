"""Helper utilities for creating nested event frame hierarchies from path expressions."""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class EventFrameNode:
    """Represents a node in an event frame hierarchy."""
    name: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None
    template_name: Optional[str] = None
    category_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent: Optional[EventFrameNode] = None
    children: List[EventFrameNode] = field(default_factory=list)
    web_id: Optional[str] = None

    def add_child(self, child: EventFrameNode) -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def get_full_path(self, separator: str = "/") -> str:
        """Get the full path from root to this node."""
        if self.parent is None:
            return self.name
        return f"{self.parent.get_full_path(separator)}{separator}{self.name}"


@dataclass
class EventFrameHierarchy:
    """Manages a hierarchy of event frames."""
    root_nodes: List[EventFrameNode] = field(default_factory=list)
    separator: str = "/"
    node_map: Dict[str, EventFrameNode] = field(default_factory=dict)

    def create_path(
        self,
        path: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        node_properties: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> EventFrameNode:
        """
        Create event frames along a path.

        Args:
            path: Path like "Batch1/Unit1/SubBatch1"
            start_time: ISO 8601 start time
            end_time: ISO 8601 end time
            node_properties: Dict mapping node names to their properties

        Returns:
            The leaf node
        """
        parts = [p for p in path.split(self.separator) if p]
        current_parent = None
        current_path = ""

        for i, part in enumerate(parts):
            current_path = self.separator.join(parts[:i+1]) if i > 0 else parts[0]

            # Check if node already exists
            if current_path in self.node_map:
                current_parent = self.node_map[current_path]
                continue

            # Get properties for this node
            props = node_properties.get(part, {}) if node_properties else {}

            # Create new node
            node = EventFrameNode(
                name=part,
                start_time=start_time or props.get("start_time"),
                end_time=end_time or props.get("end_time"),
                description=props.get("description"),
                template_name=props.get("template_name"),
                category_name=props.get("category_name"),
                attributes=props.get("attributes", {})
            )

            # Add to hierarchy
            if current_parent is None:
                self.root_nodes.append(node)
            else:
                current_parent.add_child(node)

            # Store in map
            self.node_map[current_path] = node
            current_parent = node

        return current_parent

    def get_all_nodes(self) -> List[EventFrameNode]:
        """Get all nodes in breadth-first order."""
        nodes = []
        queue = list(self.root_nodes)

        while queue:
            node = queue.pop(0)
            nodes.append(node)
            queue.extend(node.children)

        return nodes


def create_event_frame_hierarchy_from_paths(
    paths: List[str],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    separator: str = "/",
    path_properties: Optional[Dict[str, Dict[str, Any]]] = None
) -> EventFrameHierarchy:
    """
    Create an event frame hierarchy from a list of paths.

    Args:
        paths: List of paths like ["Batch1/Unit1/SubBatch1", "Batch1/Unit2/SubBatch2"]
        start_time: Default start time (ISO 8601)
        end_time: Default end time (ISO 8601)
        separator: Path separator
        path_properties: Dict mapping full paths to properties

    Returns:
        EventFrameHierarchy object

    Example:
        >>> paths = [
        ...     "Batch_001/UnitA/SubBatch_A1",
        ...     "Batch_001/UnitB/SubBatch_B1",
        ...     "Batch_002/UnitA/SubBatch_A2"
        ... ]
        >>> hierarchy = create_event_frame_hierarchy_from_paths(
        ...     paths,
        ...     start_time="2024-01-01T00:00:00Z",
        ...     end_time="2024-01-01T01:00:00Z"
        ... )
    """
    hierarchy = EventFrameHierarchy(separator=separator)

    for path in paths:
        hierarchy.create_path(
            path,
            start_time=start_time,
            end_time=end_time,
            node_properties=path_properties
        )

    return hierarchy


def create_batch_hierarchy(
    batches: List[str],
    units_per_batch: Dict[str, List[str]],
    sub_batches_per_unit: Optional[Dict[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> EventFrameHierarchy:
    """
    Create a typical batch hierarchy: Batch -> Unit -> SubBatch.

    Args:
        batches: List of batch names
        units_per_batch: Dict mapping batch names to unit lists
        sub_batches_per_unit: Optional dict mapping unit names to sub-batch lists
        start_time: Start time for all event frames
        end_time: End time for all event frames

    Returns:
        EventFrameHierarchy object

    Example:
        >>> hierarchy = create_batch_hierarchy(
        ...     batches=["Batch_001", "Batch_002"],
        ...     units_per_batch={
        ...         "Batch_001": ["ReactorA", "ReactorB"],
        ...         "Batch_002": ["ReactorA", "ReactorC"]
        ...     },
        ...     sub_batches_per_unit={
        ...         "ReactorA": ["Phase1", "Phase2", "Phase3"],
        ...         "ReactorB": ["Phase1", "Phase2"],
        ...         "ReactorC": ["Phase1", "Phase2", "Phase3"]
        ...     }
        ... )
    """
    hierarchy = EventFrameHierarchy()
    paths = []

    for batch in batches:
        units = units_per_batch.get(batch, [])
        for unit in units:
            if sub_batches_per_unit:
                sub_batches = sub_batches_per_unit.get(unit, [])
                for sub_batch in sub_batches:
                    paths.append(f"{batch}/{unit}/{sub_batch}")
            else:
                paths.append(f"{batch}/{unit}")

    for path in paths:
        hierarchy.create_path(path, start_time=start_time, end_time=end_time)

    return hierarchy


class EventFrameHierarchyManager:
    """Manager for creating event frame hierarchies in PI."""

    def __init__(self, client, database_web_id: str):
        """
        Initialize the manager.

        Args:
            client: PI Web API client
            database_web_id: WebId of the AF database
        """
        self.client = client
        self.database_web_id = database_web_id

    def create_hierarchy(self, hierarchy: EventFrameHierarchy) -> Dict[str, Any]:
        """
        Create event frame hierarchy in PI.

        Args:
            hierarchy: EventFrameHierarchy to create

        Returns:
            Dict with created event frame WebIds and info
        """
        results = {
            "event_frames_created": [],
            "total_count": 0,
            "node_map": {}
        }

        # Create event frames in breadth-first order
        for node in hierarchy.get_all_nodes():
            node_path = node.get_full_path(hierarchy.separator)

            # Prepare event frame data
            event_frame_data = {
                "Name": node.name,
                "StartTime": node.start_time or datetime.now(timezone.utc).isoformat(),
            }

            if node.end_time:
                event_frame_data["EndTime"] = node.end_time
            if node.description:
                event_frame_data["Description"] = node.description
            if node.template_name:
                event_frame_data["TemplateName"] = node.template_name
            if node.category_name:
                event_frame_data["CategoryName"] = node.category_name

            try:
                if node.parent is None:
                    # Root event frame - create in database
                    result = self.client.event_frame.create(
                        self.database_web_id,
                        event_frame_data
                    )
                else:
                    # Child event frame - create under parent
                    parent_web_id = node.parent.web_id
                    if not parent_web_id:
                        raise ValueError(f"Parent WebId not found for {node_path}")

                    result = self.client.event_frame.create_child_event_frame(
                        parent_web_id,
                        event_frame_data
                    )

                # Store WebId
                node.web_id = result["WebId"]
                hierarchy.node_map[node_path] = node

                results["event_frames_created"].append({
                    "name": node.name,
                    "path": node_path,
                    "web_id": result["WebId"],
                    "start_time": event_frame_data["StartTime"],
                    "end_time": event_frame_data.get("EndTime")
                })
                results["total_count"] += 1

                # Create attributes if specified
                if node.attributes:
                    for attr_name, attr_value in node.attributes.items():
                        attr_data = {
                            "Name": attr_name,
                            "Value": attr_value
                        }
                        self.client.event_frame.create_attribute(result["WebId"], attr_data)

            except Exception as e:
                results["event_frames_created"].append({
                    "name": node.name,
                    "path": node_path,
                    "error": str(e),
                    "status": "failed"
                })

        results["node_map"] = {path: node.web_id for path, node in hierarchy.node_map.items()}
        return results

    def create_from_paths(
        self,
        paths: List[str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        separator: str = "/",
        path_properties: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create event frame hierarchy from paths.

        Args:
            paths: List of paths
            start_time: Default start time
            end_time: Default end time
            separator: Path separator
            path_properties: Properties for specific paths

        Returns:
            Creation results
        """
        hierarchy = create_event_frame_hierarchy_from_paths(
            paths=paths,
            start_time=start_time,
            end_time=end_time,
            separator=separator,
            path_properties=path_properties
        )
        return self.create_hierarchy(hierarchy)

    def create_batch_hierarchy(
        self,
        batches: List[str],
        units_per_batch: Dict[str, List[str]],
        sub_batches_per_unit: Optional[Dict[str, List[str]]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create batch event frame hierarchy."""
        hierarchy = create_batch_hierarchy(
            batches=batches,
            units_per_batch=units_per_batch,
            sub_batches_per_unit=sub_batches_per_unit,
            start_time=start_time,
            end_time=end_time
        )
        return self.create_hierarchy(hierarchy)
