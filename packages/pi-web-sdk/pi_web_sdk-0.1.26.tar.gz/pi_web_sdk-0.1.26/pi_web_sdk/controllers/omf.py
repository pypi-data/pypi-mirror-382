"""Controllers for OMF (OCS Message Format) endpoints."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Dict, List, Optional, Any
from datetime import datetime, timezone

from .base import BaseController
from ..models.omf import (
    OMFType, OMFContainer, OMFAsset, OMFTimeSeriesData, OMFBatch,
    OMFHierarchy, OMFHierarchyNode, OMFAction, OMFMessageType,
    create_hierarchy_node_type, create_hierarchy_from_paths,
    create_industrial_hierarchy
)

if TYPE_CHECKING:
    from ..client import PIWebAPIClient

__all__ = [
    'OmfController',
    'OMFManager',
]


class OmfController(BaseController):
    """Controller for OMF operations."""

    def post_async(
        self,
        data: Dict,
        message_type: Optional[str] = None,
        omf_version: Optional[str] = None,
        action: Optional[str] = None,
        data_server_web_id: Optional[str] = None,
    ) -> Dict:
        """Send OMF data asynchronously.

        Args:
            data: The OMF message data
            message_type: Type of OMF message (Type, Container, Data)
            omf_version: OMF version
            action: Action to perform (create, update, delete)
            data_server_web_id: WebID of the target data server
        """
        headers = {}
        if message_type:
            headers["messagetype"] = message_type
        if omf_version:
            headers["omfversion"] = omf_version
        if action:
            headers["action"] = action

        params = {}
        if data_server_web_id:
            params["dataServerWebId"] = data_server_web_id

        return self.client.post("omf", data=data, headers=headers, params=params)


class OMFManager:
    """High-level manager for OMF operations using dataclass models."""

    def __init__(self, client: PIWebAPIClient, data_server_web_id: Optional[str] = None):
        """
        Initialize OMF Manager.

        Args:
            client: PI Web API client instance
            data_server_web_id: Optional specific data server WebID
        """
        self.client = client
        self.data_server_web_id = data_server_web_id
        self.omf_version = "1.2"

        # Auto-detect data server if not provided
        if not self.data_server_web_id:
            self._auto_detect_data_server()

    def _auto_detect_data_server(self) -> None:
        """Auto-detect the first available data server."""
        try:
            servers = self.client.data_server.list().get("Items", [])
            if servers:
                self.data_server_web_id = servers[0]["WebId"]
        except Exception:
            pass  # Will be handled when operations are attempted

    def create_type(
        self,
        omf_type: OMFType,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Create an OMF type.

        Args:
            omf_type: OMF type dataclass instance
            action: OMF action (create, update, delete)

        Returns:
            Response from PI Web API
        """
        if not self.data_server_web_id:
            raise ValueError("No data server WebID available")

        return self.client.omf.post_async(
            data=[omf_type.to_dict()],
            message_type=OMFMessageType.TYPE.value,
            omf_version=self.omf_version,
            action=action.value,
            data_server_web_id=self.data_server_web_id
        )

    def create_container(
        self,
        container: OMFContainer,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Create an OMF container (stream).

        Args:
            container: OMF container dataclass instance
            action: OMF action (create, update, delete)

        Returns:
            Response from PI Web API
        """
        if not self.data_server_web_id:
            raise ValueError("No data server WebID available")

        return self.client.omf.post_async(
            data=[container.to_dict()],
            message_type=OMFMessageType.CONTAINER.value,
            omf_version=self.omf_version,
            action=action.value,
            data_server_web_id=self.data_server_web_id
        )

    def create_asset(
        self,
        asset: OMFAsset,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Create an OMF asset.

        Args:
            asset: OMF asset dataclass instance
            action: OMF action (create, update, delete)

        Returns:
            Response from PI Web API
        """
        if not self.data_server_web_id:
            raise ValueError("No data server WebID available")

        return self.client.omf.post_async(
            data=[asset.to_dict()],
            message_type=OMFMessageType.DATA.value,
            omf_version=self.omf_version,
            action=action.value,
            data_server_web_id=self.data_server_web_id
        )

    def send_time_series_data(
        self,
        ts_data: OMFTimeSeriesData,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Send time series data.

        Args:
            ts_data: OMF time series data dataclass instance
            action: OMF action (create, update, delete)

        Returns:
            Response from PI Web API
        """
        if not self.data_server_web_id:
            raise ValueError("No data server WebID available")

        return self.client.omf.post_async(
            data=[ts_data.to_dict()],
            message_type=OMFMessageType.DATA.value,
            omf_version=self.omf_version,
            action=action.value,
            data_server_web_id=self.data_server_web_id
        )

    def send_batch(
        self,
        batch: OMFBatch,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Send a batch of OMF messages in optimal order.

        Args:
            batch: OMF batch containing types, containers, and data
            action: OMF action (create, update, delete)

        Returns:
            Dict containing responses for each message type
        """
        results = {}

        # Send types first
        if batch.types:
            type_messages = batch.get_type_messages()
            results["types"] = self.client.omf.post_async(
                data=type_messages,
                message_type=OMFMessageType.TYPE.value,
                omf_version=self.omf_version,
                action=action.value,
                data_server_web_id=self.data_server_web_id
            )

        # Send containers second
        if batch.containers:
            container_messages = batch.get_container_messages()
            results["containers"] = self.client.omf.post_async(
                data=container_messages,
                message_type=OMFMessageType.CONTAINER.value,
                omf_version=self.omf_version,
                action=action.value,
                data_server_web_id=self.data_server_web_id
            )

        # Send data (assets and time series) last
        data_messages = batch.get_data_messages()
        if data_messages:
            results["data"] = self.client.omf.post_async(
                data=data_messages,
                message_type=OMFMessageType.DATA.value,
                omf_version=self.omf_version,
                action=action.value,
                data_server_web_id=self.data_server_web_id
            )

        return results

    def create_complete_sensor_setup(
        self,
        sensor_id: str,
        sensor_name: str,
        sensor_type: OMFType,
        initial_data: Optional[List[Dict[str, Any]]] = None,
        asset_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete sensor setup with type, container, optional asset, and initial data.

        Args:
            sensor_id: Unique identifier for the sensor
            sensor_name: Human-readable name for the sensor
            sensor_type: OMF type definition for the sensor
            initial_data: Optional initial data points
            asset_properties: Optional asset properties for static data

        Returns:
            Dict containing all operation results
        """
        results = {}

        # Create type
        results["type"] = self.create_type(sensor_type)

        # Create container
        container = OMFContainer(
            id=sensor_id,
            type_id=sensor_type.id,
            name=sensor_name,
            description=f"Data stream for {sensor_name}"
        )
        results["container"] = self.create_container(container)

        # Create asset if properties provided
        if asset_properties:
            # Create asset type if needed
            asset_type_id = f"{sensor_type.id}_Asset"
            # Note: This assumes asset type exists or is created separately

            asset = OMFAsset.create_single_asset(
                type_id=asset_type_id,
                **asset_properties
            )
            results["asset"] = self.create_asset(asset)

        # Send initial data if provided
        if initial_data:
            ts_data = OMFTimeSeriesData(
                container_id=sensor_id,
                values=initial_data
            )
            results["initial_data"] = self.send_time_series_data(ts_data)

        return results

    def send_sensor_data(
        self,
        sensor_id: str,
        data_points: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Convenience method to send data to a sensor stream.

        Args:
            sensor_id: Container ID for the sensor
            data_points: List of data points to send

        Returns:
            Response from PI Web API
        """
        ts_data = OMFTimeSeriesData(
            container_id=sensor_id,
            values=data_points
        )
        return self.send_time_series_data(ts_data)

    def send_single_data_point(
        self,
        sensor_id: str,
        **data
    ) -> Dict[str, Any]:
        """
        Send a single data point to a sensor stream.

        Args:
            sensor_id: Container ID for the sensor
            **data: Data point properties

        Returns:
            Response from PI Web API
        """
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).isoformat()

        return self.send_sensor_data(sensor_id, [data])

    def create_af_hierarchy(
        self,
        hierarchy: OMFHierarchy,
        database_web_id: str
    ) -> Dict[str, Any]:
        """
        Create a proper AF element hierarchy with parent-child relationships.

        This creates traditional AF elements (not OMF assets) with proper nesting.

        Args:
            hierarchy: OMF hierarchy structure to create
            database_web_id: WebId of the AF database to create elements in

        Returns:
            Dict containing created element WebIds and structure info
        """
        results = {
            "elements_created": [],
            "total_count": 0,
            "node_map": {}  # Maps node path to WebId
        }

        # Track WebIds for parent-child relationships
        node_webids = {}

        # Process nodes level by level (breadth-first)
        for node in hierarchy.get_all_nodes():
            node_path = node.get_full_path(hierarchy.separator)

            # Prepare element data
            element_data = {
                "Name": node.name,
                "Description": node.properties.get("description", f"{node.name} element")
            }
            # Add any additional properties as custom attributes (if needed)

            try:
                if node.parent is None:
                    # Root node - create in database
                    elem = self.client.asset_database.create_element(
                        database_web_id,
                        element_data
                    )
                else:
                    # Child node - create under parent
                    parent_path = node.parent.get_full_path(hierarchy.separator)
                    parent_web_id = node_webids.get(parent_path)

                    if not parent_web_id:
                        raise ValueError(f"Parent WebId not found for {parent_path}")

                    elem = self.client.element.create_element(
                        parent_web_id,
                        element_data
                    )

                # Store WebId for this node
                node_webids[node_path] = elem["WebId"]

                results["elements_created"].append({
                    "name": node.name,
                    "path": node_path,
                    "web_id": elem["WebId"],
                    "is_leaf": node.is_leaf
                })
                results["total_count"] += 1

            except Exception as e:
                results["elements_created"].append({
                    "name": node.name,
                    "path": node_path,
                    "error": str(e),
                    "status": "failed"
                })

        results["node_map"] = node_webids
        return results

    def create_hierarchy(
        self,
        hierarchy: OMFHierarchy,
        create_types: bool = True,
        action: OMFAction = OMFAction.CREATE
    ) -> Dict[str, Any]:
        """
        Create a complete hierarchy in OMF.

        Args:
            hierarchy: OMF hierarchy to create
            create_types: Whether to create the types first
            action: OMF action (create, update, delete)

        Returns:
            Dict containing operation results
        """
        results = {}

        if create_types:
            # Get unique type IDs from hierarchy
            type_ids = set()
            for node in hierarchy.get_all_nodes():
                type_ids.add(node.type_id)

            # Create types for each unique type_id
            results["types_created"] = []
            for type_id in type_ids:
                try:
                    # Create hierarchy node type
                    omf_type = create_hierarchy_node_type(type_id)

                    # Send type to OMF
                    type_response = self.create_type(omf_type)
                    results["types_created"].append({
                        "type_id": type_id,
                        "status": "success",
                        "response": type_response
                    })
                except Exception as e:
                    results["types_created"].append({
                        "type_id": type_id,
                        "status": "error",
                        "error": str(e)
                    })

        # Convert hierarchy to OMF assets
        hierarchy_assets = hierarchy.to_omf_assets()

        # Send each asset type separately for better organization
        results["assets_created"] = []
        for asset in hierarchy_assets:
            try:
                response = self.create_asset(asset, action)
                results["assets_created"].append({
                    "type_id": asset.type_id,
                    "count": len(asset.values),
                    "status": "success",
                    "response": response
                })
            except Exception as e:
                results["assets_created"].append({
                    "type_id": asset.type_id,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def create_hierarchy_from_paths(
        self,
        paths: List[str],
        root_type_id: str,
        leaf_type_id: str,
        separator: str = "/",
        path_properties: Optional[Dict[str, Dict[str, Any]]] = None,
        create_types: bool = True,
        use_af_elements: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete hierarchy from a list of paths.

        Args:
            paths: List of paths like ["plant1/unit1/sensor1", "plant1/unit2/sensor2"]
            root_type_id: Type ID for intermediate nodes
            leaf_type_id: Type ID for leaf nodes
            separator: Path separator (default: "/")
            path_properties: Optional dict mapping paths to properties
            create_types: Whether to create the types first (only for OMF method)
            use_af_elements: If True, creates proper AF elements with parent-child relationships.
                            If False, creates OMF assets (flat structure)

        Returns:
            Dict containing operation results
        """
        # Create hierarchy structure
        hierarchy = create_hierarchy_from_paths(
            paths=paths,
            root_type_id=root_type_id,
            leaf_type_id=leaf_type_id,
            separator=separator,
            path_properties=path_properties
        )

        if use_af_elements:
            # Create proper AF element hierarchy
            # Get database from asset server
            asset_servers = self.client.asset_server.list()
            if not asset_servers.get("Items"):
                raise ValueError("No asset servers found")

            asset_server = asset_servers["Items"][0]
            dbs = self.client.asset_server.get_databases(asset_server["WebId"])
            if not dbs.get("Items"):
                raise ValueError("No databases found")

            database_web_id = dbs["Items"][0]["WebId"]
            return self.create_af_hierarchy(hierarchy, database_web_id)
        else:
            # Create using OMF (flat assets)
            return self.create_hierarchy(hierarchy, create_types)

    def create_industrial_hierarchy(
        self,
        plants: List[str],
        units_per_plant: Dict[str, List[str]],
        sensors_per_unit: Dict[str, List[str]],
        plant_type_id: str = "PlantType",
        unit_type_id: str = "UnitType",
        sensor_type_id: str = "SensorType",
        create_types: bool = True,
        use_af_elements: bool = True
    ) -> Dict[str, Any]:
        """
        Create a typical industrial hierarchy: Plant -> Unit -> Sensor.

        Args:
            plants: List of plant names
            units_per_plant: Dict mapping plant names to unit lists
            sensors_per_unit: Dict mapping unit names to sensor lists
            plant_type_id: Type ID for plant nodes
            unit_type_id: Type ID for unit nodes
            sensor_type_id: Type ID for sensor nodes
            create_types: Whether to create the types first (only for OMF method)
            use_af_elements: If True, creates proper AF elements with parent-child relationships.
                            If False, creates OMF assets (flat structure)

        Returns:
            Dict containing operation results
        """
        # Create hierarchy structure
        hierarchy = create_industrial_hierarchy(
            plants=plants,
            units_per_plant=units_per_plant,
            sensors_per_unit=sensors_per_unit,
            plant_type_id=plant_type_id,
            unit_type_id=unit_type_id,
            sensor_type_id=sensor_type_id
        )

        if use_af_elements:
            # Create proper AF element hierarchy
            asset_servers = self.client.asset_server.list()
            if not asset_servers.get("Items"):
                raise ValueError("No asset servers found")

            asset_server = asset_servers["Items"][0]
            dbs = self.client.asset_server.get_databases(asset_server["WebId"])
            if not dbs.get("Items"):
                raise ValueError("No databases found")

            database_web_id = dbs["Items"][0]["WebId"]
            return self.create_af_hierarchy(hierarchy, database_web_id)
        else:
            # Create using OMF (flat assets)
            return self.create_hierarchy(hierarchy, create_types)

    def add_path_to_existing_hierarchy(
        self,
        path: str,
        root_type_id: str,
        leaf_type_id: str,
        separator: str = "/",
        leaf_properties: Optional[Dict[str, Any]] = None,
        intermediate_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a single path to an existing hierarchy.

        Args:
            path: Path string like "element1/element2/element3"
            root_type_id: Type ID for intermediate nodes
            leaf_type_id: Type ID for leaf nodes
            separator: Path separator
            leaf_properties: Properties for the leaf node
            intermediate_properties: Properties for intermediate nodes

        Returns:
            Response from PI Web API
        """
        # Create a temporary hierarchy with just this path
        hierarchy = OMFHierarchy(
            root_type_id=root_type_id,
            leaf_type_id=leaf_type_id,
            separator=separator
        )

        hierarchy.create_path(
            path=path,
            leaf_properties=leaf_properties,
            intermediate_properties=intermediate_properties
        )

        # Create the hierarchy in OMF
        return self.create_hierarchy(hierarchy, create_types=False)

    def get_data_server_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current data server."""
        if not self.data_server_web_id:
            return None

        try:
            return self.client.data_server.get(self.data_server_web_id)
        except Exception:
            return None
