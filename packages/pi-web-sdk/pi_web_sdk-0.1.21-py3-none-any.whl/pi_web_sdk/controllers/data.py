"""Controllers for data server and point endpoints."""

from __future__ import annotations

from typing import Dict, Optional, Union

from .base import BaseController
from ..models.data import DataServer, Point
from ..models.responses import ItemsResponse, parse_response, parse_items_response

__all__ = [
    'DataServerController',
    'PointController',
]

class DataServerController(BaseController):
    """Controller for Data Server operations."""

    def list(self) -> Dict:
        """List all data servers."""
        return self.client.get("dataservers")
    
    def list_parsed(self) -> ItemsResponse[DataServer]:
        """List all data servers, parsed into DataServer objects.
        
        Returns:
            ItemsResponse containing list of DataServer objects
            
        Example:
            >>> servers = client.data_server.list_parsed()
            >>> for server in servers:
            ...     print(f"{server.name}: {server.server_version}")
        """
        response = self.list()
        return parse_items_response(response, DataServer)

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get data server by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"dataservers/{web_id}", params=params)
    
    def get_parsed(self, web_id: str, selected_fields: Optional[str] = None) -> DataServer:
        """Get data server by WebID, parsed into DataServer object.
        
        Args:
            web_id: WebID of the data server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            DataServer object
            
        Example:
            >>> server = client.data_server.get_parsed(web_id)
            >>> print(f"Server: {server.name}")
            >>> print(f"Version: {server.server_version}")
            >>> print(f"Connected: {server.is_connected}")
        """
        response = self.get(web_id, selected_fields)
        return parse_response(response, DataServer)

    def get_by_name(self, name: str, selected_fields: Optional[str] = None) -> Dict:
        """Get data server by name."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"dataservers/name/{self._encode_path(name)}", params=params
        )
    
    def get_by_name_parsed(self, name: str, selected_fields: Optional[str] = None) -> DataServer:
        """Get data server by name, parsed into DataServer object.
        
        Args:
            name: Name of the data server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            DataServer object
            
        Example:
            >>> server = client.data_server.get_by_name_parsed("PISERVER")
            >>> print(server.path)
        """
        response = self.get_by_name(name, selected_fields)
        return parse_response(response, DataServer)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get data server by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"dataservers/path/{self._encode_path(path)}", params=params
        )
    
    def get_by_path_parsed(self, path: str, selected_fields: Optional[str] = None) -> DataServer:
        """Get data server by path, parsed into DataServer object.
        
        Args:
            path: Path to the data server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            DataServer object
            
        Example:
            >>> server = client.data_server.get_by_path_parsed(r"\\PISERVER")
            >>> print(server.name)
        """
        response = self.get_by_path(path, selected_fields)
        return parse_response(response, DataServer)

    def get_points(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get points for a data server."""
        params = {"startIndex": start_index, "maxCount": max_count}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields

        return self.client.get(f"dataservers/{web_id}/points", params=params)
    
    def get_points_parsed(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> ItemsResponse[Point]:
        """Get points for a data server, parsed into Point objects.
        
        Args:
            web_id: WebID of the data server
            name_filter: Optional name filter pattern
            start_index: Starting index for pagination
            max_count: Maximum number of points to return
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            ItemsResponse containing list of Point objects
            
        Example:
            >>> points = client.data_server.get_points_parsed(server_web_id, name_filter="*temp*")
            >>> for point in points:
            ...     print(f"{point.name}: {point.point_type} ({point.engineering_units})")
        """
        response = self.get_points(web_id, name_filter, start_index, max_count, selected_fields)
        return parse_items_response(response, Point)

    def find_point_by_name(self, web_id: str, point_name: str) -> Optional[Dict]:
        """Find a specific point by name on this data server."""
        points = self.get_points(web_id, name_filter=point_name)
        items = points.get("Items", [])
        for item in items:
            if item.get("Name", "").upper() == point_name.upper():
                return item
        return None

    def create_point(self, web_id: str, point: Union[Point, Dict]) -> Dict:
        """Create a new PI Point on the data server.

        Args:
            web_id: WebID of the data server
            point: Point model instance or dictionary with point definition (Name, PointType, etc.)

        Returns:
            Dictionary with the created point information
        """
        data = point.to_dict() if isinstance(point, Point) else point
        return self.client.post(f"dataservers/{web_id}/points", data=data)


class PointController(BaseController):
    """Controller for Point operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get point by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"points/{web_id}", params=params)
    
    def get_parsed(self, web_id: str, selected_fields: Optional[str] = None) -> Point:
        """Get point by WebID, parsed into Point object.
        
        Args:
            web_id: WebID of the point
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Point object
            
        Example:
            >>> point = client.point.get_parsed(web_id)
            >>> print(f"{point.name}: {point.point_type}")
            >>> print(f"Units: {point.engineering_units}")
            >>> print(f"Step: {point.step}")
        """
        response = self.get(web_id, selected_fields)
        return parse_response(response, Point)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get point by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"points/path/{self._encode_path(path)}", params=params)
    
    def get_by_path_parsed(self, path: str, selected_fields: Optional[str] = None) -> Point:
        """Get point by path, parsed into Point object.
        
        Args:
            path: Path to the point
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Point object
            
        Example:
            >>> point = client.point.get_by_path_parsed(r"\\PISERVER\\sinusoid")
            >>> print(point.description)
        """
        response = self.get_by_path(path, selected_fields)
        return parse_response(response, Point)

    def update(self, web_id: str, point: Union[Point, Dict]) -> Dict:
        """Update a point.
        
        Args:
            web_id: WebID of the point to update
            point: Point model instance or dictionary with point data
            
        Returns:
            Updated point response
        """
        data = point.to_dict() if isinstance(point, Point) else point
        return self.client.patch(f"points/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete a point."""
        return self.client.delete(f"points/{web_id}")

    def get_attributes(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get attributes for a point."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"points/{web_id}/attributes", params=params)
