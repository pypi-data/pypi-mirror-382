"""Controllers for asset model endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Union

from ..models.asset import AssetDatabase, Element, ElementCategory, ElementTemplate
from ..models.attribute import Attribute, AttributeTemplate
from ..models.analysis import Analysis
from ..models.security import SecurityEntry
from ..models.notification import NotificationRule
from ..models.data import Point
from .base import BaseController

__all__ = [
    "AssetServerController",
    "AssetDatabaseController",
    "ElementController",
    "ElementCategoryController",
    "ElementTemplateController",
]


class AssetServerController(BaseController):
    """Controller for Asset Server operations."""

    def list(self) -> Dict:
        """List all asset servers."""
        return self.client.get("assetservers")

    def get_default(self) -> Dict:
        """Get the default asset server (first in the list).

        Returns:
            Dictionary with the default asset server information

        Example:
            >>> asset_server = client.asset_server.get_default()
            >>> print(f"Default asset server: {asset_server['Name']}")
            >>> print(f"WebId: {asset_server['WebId']}")
        """
        servers = self.list()
        items = servers.get("Items", [])
        if not items:
            raise ValueError("No asset servers found")
        return items[0]

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get asset server by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetservers/{web_id}", params=params)

    def get_by_name(self, name: str, selected_fields: Optional[str] = None) -> Dict:
        """Get asset server by name."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"assetservers/name/{self._encode_path(name)}", params=params
        )

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get asset server by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"assetservers/path/{self._encode_path(path)}", params=params
        )

    def get_databases(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get databases for an asset server."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetservers/{web_id}/assetdatabases", params=params)

    def get_enumeration_sets(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get enumeration sets for an asset server."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetservers/{web_id}/enumerationsets", params=params)


class AssetDatabaseController(BaseController):
    """Controller for Asset Database operations."""

    def get_default_server(self) -> Dict:
        asset_server = self.client.asset_server.list()
        return asset_server["Items"][0]

    def get_default_database(self) -> Dict:
        asset_server = self.get_default_server()
        asset_database = self.client.asset_server.get_databases(asset_server["WebId"])
        return asset_database["Items"][1]

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get asset database by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetdatabases/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get asset database by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"assetdatabases/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, database: Union[AssetDatabase, Dict]) -> Dict:
        """Update an asset database.

        Args:
            web_id: WebID of the database to update
            database: AssetDatabase model instance or dictionary with database data

        Returns:
            Updated database response
        """
        data = database.to_dict() if isinstance(database, AssetDatabase) else database
        return self.client.patch(f"assetdatabases/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an asset database."""
        return self.client.delete(f"assetdatabases/{web_id}")

    def get_elements(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        category_name: Optional[str] = None,
        template_name: Optional[str] = None,
        element_type: Optional[str] = None,
        search_full_hierarchy: bool = False,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get elements from asset database."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if category_name:
            params["categoryName"] = category_name
        if template_name:
            params["templateName"] = template_name
        if element_type:
            params["elementType"] = element_type
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if selected_fields:
            params["selectedFields"] = selected_fields

        return self.client.get(f"assetdatabases/{web_id}/elements", params=params)

    def create_element(self, web_id: str, element: Union[Element, Dict]) -> Dict:
        """Create an element in the asset database.

        Args:
            web_id: WebID of the parent database
            element: Element model instance or dictionary with element data

        Returns:
            Created element response
        """
        data = element.to_dict() if isinstance(element, Element) else element
        return self.client.post(f"assetdatabases/{web_id}/elements", data=data)

    def create_or_get_element(self, web_id: str, element: Union[Element, Dict]) -> Dict:
        """Create a root element in the asset database or get it if it already exists.

        Args:
            web_id: WebID of the parent database
            element: Element model instance or dictionary with element data

        Returns:
            Created or existing element response

        Example:
            >>> db = client.asset_database.get_default_database()
            >>> element = Element(name="Plant", description="Main plant")
            >>> plant = client.asset_database.create_or_get_element(db['WebId'], element)
            >>> print(f"Plant: {plant['Name']}, WebId: {plant['WebId']}")
        """
        data = element.to_dict() if isinstance(element, Element) else element
        name = data.get("Name")

        return self._create_or_get(
            create_func=self.create_element,
            get_func=self.get_elements,
            create_args=(web_id, element),
            get_args=(web_id,),
            get_kwargs={"name_filter": name, "max_count": 1}
        )

    def get_analyses(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get analyses for an asset database."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetdatabases/{web_id}/analyses", params=params)

    def get_event_frames(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get event frames for an asset database."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetdatabases/{web_id}/eventframes", params=params)

    def get_tables(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get tables for an asset database."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"assetdatabases/{web_id}/tables", params=params)


class ElementController(BaseController):
    """Controller for Element operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elements/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, element: Union[Element, Dict]) -> Dict:
        """Update an element.

        Args:
            web_id: WebID of the element to update
            element: Element model instance or dictionary with element data

        Returns:
            Updated element response
        """
        data = element.to_dict() if isinstance(element, Element) else element
        return self.client.patch(f"elements/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an element."""
        return self.client.delete(f"elements/{web_id}")

    def get_attributes(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        category_name: Optional[str] = None,
        template_name: Optional[str] = None,
        value_type: Optional[str] = None,
        search_full_hierarchy: bool = False,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get attributes for an element."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if category_name:
            params["categoryName"] = category_name
        if template_name:
            params["templateName"] = template_name
        if value_type:
            params["valueType"] = value_type
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if selected_fields:
            params["selectedFields"] = selected_fields

        return self.client.get(f"elements/{web_id}/attributes", params=params)

    def create_attribute(
        self,
        web_id: str,
        attribute: Union[Attribute, Dict],
        value: Optional[Any] = None
    ) -> Dict:
        """Create an attribute on the element.

        Args:
            web_id: WebID of the element
            attribute: Attribute model instance or dictionary with attribute data
            value: Optional initial value to set after creating the attribute

        Returns:
            Created attribute response
        """
        data = attribute.to_dict() if isinstance(attribute, Attribute) else attribute
        response = self.client.post(f"elements/{web_id}/attributes", data=data)

        # If a value was provided and we got a WebId back, write the initial value
        if value is not None and response.get("WebId"):
            # Use POST to record the value instead of PUT (for newly created attributes)
            value_data = [{"Value": value}] if not isinstance(value, dict) else [value]
            self.client.post(f"streams/{response['WebId']}/recorded", data=value_data)

        return response

    def create_pipoint_attribute(
        self,
        element_web_id: str,
        attribute: Union[Attribute, Dict],
        point: Union[Point, Dict, str],
        value: Optional[Any] = None,
    ) -> Dict:
        """Create a dynamic attribute with a PI Point data reference.

        Args:
            element_web_id: WebID of the parent element
            attribute: Attribute model instance or dictionary with attribute data.
                      The data_reference_plugin_name will be automatically set to "PI Point".
            point: Point model instance, dictionary with point data, or string with PI Point name.
                  If Point instance or dict, the name field will be used for config_string.
                  If string, it will be used directly as the PI Point name.
            value: Optional initial value to set after creating the attribute

        Returns:
            Created attribute response
        """
        # Convert attribute to dict if needed
        attr_data = attribute.to_dict() if isinstance(attribute, Attribute) else attribute.copy()

        # Set PI Point data reference plugin
        attr_data['DataReferencePlugIn'] = "PI Point"

        # Determine PI Point name from point parameter
        if isinstance(point, Point):
            pi_point_name = point.name
        elif isinstance(point, dict):
            pi_point_name = point.get('Name') or point.get('name')
            if not pi_point_name:
                raise ValueError("Point dictionary must contain 'Name' or 'name' field")
        elif isinstance(point, str):
            pi_point_name = point
        else:
            raise TypeError(f"point must be Point, dict, or str, got {type(point)}")

        # Set config string to PI Point name
        attr_data['ConfigString'] = pi_point_name

        return self.create_attribute(element_web_id, attr_data, value)

    def create_or_get_attribute(
        self,
        web_id: str,
        attribute: Union[Attribute, Dict],
        value: Optional[Any] = None
    ) -> Dict:
        """Create an attribute or get it if it already exists.

        Args:
            web_id: WebID of the element
            attribute: Attribute model instance or dictionary with attribute data
            value: Optional initial value to set after creating the attribute

        Returns:
            Created or existing attribute response
        """
        data = attribute.to_dict() if isinstance(attribute, Attribute) else attribute
        name = data.get("Name")

        return self._create_or_get(
            create_func=self.create_attribute,
            get_func=self.get_attributes,
            create_args=(web_id, attribute, value),
            get_args=(web_id,),
            get_kwargs={"name_filter": name, "max_count": 1}
        )

    def create_or_get_pipoint_attribute(
        self,
        element_web_id: str,
        data_server_web_id: str,
        attribute: Union[Attribute, Dict],
        point: Union[Point, Dict, str],
        value: Optional[Any] = None,
    ) -> Dict:
        """Create a PI Point attribute or get it if it already exists.

        This method will:
        1. Create or get the PI Point on the data server (if point is not a string)
        2. Create or get the attribute that references the PI Point

        Args:
            element_web_id: WebID of the parent element
            data_server_web_id: WebID of the data server where the PI Point will be created
            attribute: Attribute model instance or dictionary with attribute data
            point: Point model instance, dictionary with point data, or string with existing PI Point name
            value: Optional initial value to set after creating the attribute

        Returns:
            Created or existing attribute response

        Example:
            # Create or get a PI Point attribute with a new PI Point
            point = Point(name="TempSensor01", point_type=PointType.FLOAT32, engineering_units="degC")
            attr = Attribute(name="Temperature", type=AttributeType.DOUBLE.value)

            result = client.element.create_or_get_pipoint_attribute(
                element_web_id=element['WebId'],
                data_server_web_id=data_server['WebId'],
                attribute=attr,
                point=point,
                value=25.5
            )

            # Or with an existing PI Point name
            result = client.element.create_or_get_pipoint_attribute(
                element_web_id=element['WebId'],
                data_server_web_id=data_server['WebId'],  # Not used if point is a string
                attribute=attr,
                point="ExistingPoint",  # Existing PI Point name
                value=25.5
            )
        """
        # If point is a Point instance or dict, create or get it first
        if isinstance(point, (Point, dict)):
            point_obj = self.client.data_server.create_or_get_point(data_server_web_id, point)
            pi_point_name = point_obj.get("Name")
        else:
            # point is already a string (existing PI Point name)
            pi_point_name = point

        # Now create or get the attribute
        data = attribute.to_dict() if isinstance(attribute, Attribute) else attribute
        attr_name = data.get("Name")

        return self._create_or_get(
            create_func=self.create_pipoint_attribute,
            get_func=self.get_attributes,
            create_args=(element_web_id, attribute, pi_point_name, value),
            get_args=(element_web_id,),
            get_kwargs={"name_filter": attr_name, "max_count": 1}
        )

    def get_elements(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        category_name: Optional[str] = None,
        template_name: Optional[str] = None,
        element_type: Optional[str] = None,
        search_full_hierarchy: bool = False,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get child elements."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if category_name:
            params["categoryName"] = category_name
        if template_name:
            params["templateName"] = template_name
        if element_type:
            params["elementType"] = element_type
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if selected_fields:
            params["selectedFields"] = selected_fields

        return self.client.get(f"elements/{web_id}/elements", params=params)

    def create_uns(self, web_id: str, uns: str):
        """Create a UNS."""
        uns = uns.replace("\\", "/")
        parts = uns.split("/")
        try:
            root = self.client.asset_database.create_element(
                web_id, Element(name=parts[0])
            )
        except:
            root = self.client.asset_database.get_elements(web_id, name_filter=parts[0])
            root = root["Items"][0]
        for part in parts[1:]:
            try:
                root = self.client.element.create_element(
                    root["WebId"], Element(name=part)
                )
            except:
                root = self.client.element.get_elements(root["WebId"], name_filter=part)
                root = root["Items"][0]
        return root

    def create_element(self, web_id: str, element: Union[Element, Dict]) -> Dict:
        """Create a child element.

        Args:
            web_id: WebID of the parent element
            element: Element model instance or dictionary with element data

        Returns:
            Created element response
        """
        data = element.to_dict() if isinstance(element, Element) else element
        return self.client.post(f"elements/{web_id}/elements", data=data)

    def create_or_get_element(self, web_id: str, element: Union[Element, Dict]) -> Dict:
        """Create a child element or get it if it already exists.

        Args:
            web_id: WebID of the parent element
            element: Element model instance or dictionary with element data

        Returns:
            Created or existing element response
        """
        data = element.to_dict() if isinstance(element, Element) else element
        name = data.get("Name")

        return self._create_or_get(
            create_func=self.create_element,
            get_func=self.get_elements,
            create_args=(web_id, element),
            get_args=(web_id,),
            get_kwargs={"name_filter": name, "max_count": 1}
        )

    def get_analyses(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get analyses for an element."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/analyses", params=params)

    def create_analysis(self, web_id: str, analysis: Union[Analysis, Dict]) -> Dict:
        """Create an analysis on the element.

        Args:
            web_id: WebID of the element
            analysis: Analysis model instance or dictionary with analysis data

        Returns:
            Created analysis response
        """
        data = analysis.to_dict() if isinstance(analysis, Analysis) else analysis
        return self.client.post(f"elements/{web_id}/analyses", data=data)

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get categories for an element."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/categories", params=params)

    def create_config(self, web_id: str, include_child_elements: bool = False) -> Dict:
        """Create or update an element's configuration."""
        params = {}
        if include_child_elements:
            params["includeChildElements"] = include_child_elements
        return self.client.post(f"elements/{web_id}/config", params=params)

    def delete_config(self, web_id: str, include_child_elements: bool = False) -> Dict:
        """Delete an element's configuration."""
        params = {}
        if include_child_elements:
            params["includeChildElements"] = include_child_elements
        return self.client.delete(f"elements/{web_id}/config", params=params)

    def find_element_attributes(
        self,
        web_id: str,
        attribute_category: Optional[str] = None,
        attribute_description_filter: Optional[str] = None,
        attribute_name_filter: Optional[str] = None,
        attribute_type: Optional[str] = None,
        element_category: Optional[str] = None,
        element_description_filter: Optional[str] = None,
        element_name_filter: Optional[str] = None,
        element_template: Optional[str] = None,
        element_type: Optional[str] = None,
        max_count: int = 1000,
        search_full_hierarchy: bool = False,
        selected_fields: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
    ) -> Dict:
        """Search for element attributes by various criteria."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if attribute_category:
            params["attributeCategory"] = attribute_category
        if attribute_description_filter:
            params["attributeDescriptionFilter"] = attribute_description_filter
        if attribute_name_filter:
            params["attributeNameFilter"] = attribute_name_filter
        if attribute_type:
            params["attributeType"] = attribute_type
        if element_category:
            params["elementCategory"] = element_category
        if element_description_filter:
            params["elementDescriptionFilter"] = element_description_filter
        if element_name_filter:
            params["elementNameFilter"] = element_name_filter
        if element_template:
            params["elementTemplate"] = element_template
        if element_type:
            params["elementType"] = element_type
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/elementattributes", params=params)

    def get_event_frames(
        self,
        web_id: str,
        can_be_acknowledged: Optional[bool] = None,
        category_name: Optional[str] = None,
        end_time: Union[str, datetime, None] = None,
        is_acknowledged: Optional[bool] = None,
        name_filter: Optional[str] = None,
        referenced_element_name_filter: Optional[str] = None,
        search_full_hierarchy: bool = False,
        search_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        severity: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        start_time: Union[str, datetime, None] = None,
        max_count: int = 1000,
        template_name: Optional[str] = None,
    ) -> Dict:
        """Get event frames for an element."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if can_be_acknowledged is not None:
            params["canBeAcknowledged"] = can_be_acknowledged
        if category_name:
            params["categoryName"] = category_name
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if is_acknowledged is not None:
            params["isAcknowledged"] = is_acknowledged
        if name_filter:
            params["nameFilter"] = name_filter
        if referenced_element_name_filter:
            params["referencedElementNameFilter"] = referenced_element_name_filter
        if search_mode:
            params["searchMode"] = search_mode
        if severity:
            params["severity"] = severity
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        if template_name:
            params["templateName"] = template_name
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/eventframes", params=params)

    def get_notification_rule_subscribers(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get notification rule subscribers for an element."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elements/{web_id}/notificationrulesubscribers", params=params
        )

    def get_paths(self, web_id: str, relative_path: Optional[str] = None) -> Dict:
        """Get the element's paths."""
        params = {}
        if relative_path:
            params["relativePath"] = relative_path
        return self.client.get(f"elements/{web_id}/paths", params=params)

    def get_referenced_elements(
        self,
        web_id: str,
        category_name: Optional[str] = None,
        description_filter: Optional[str] = None,
        element_type: Optional[str] = None,
        max_count: int = 1000,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        template_name: Optional[str] = None,
    ) -> Dict:
        """Get elements referenced by this element's attributes."""
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
        }
        if category_name:
            params["categoryName"] = category_name
        if description_filter:
            params["descriptionFilter"] = description_filter
        if element_type:
            params["elementType"] = element_type
        if name_filter:
            params["nameFilter"] = name_filter
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if template_name:
            params["templateName"] = template_name
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/referencedelements", params=params)

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for an element."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for an element."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for an element."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elements/{web_id}/securityentries/{self._encode_path(name)}",
            params=params,
        )

    def create_security_entry(
        self, web_id: str, security_entry: Union[SecurityEntry, Dict], apply_to_children: bool = False
    ) -> Dict:
        """Create a security entry for the element.

        Args:
            web_id: WebID of the element
            security_entry: SecurityEntry model instance or dictionary with security entry data
            apply_to_children: Whether to apply to child elements

        Returns:
            Created security entry response
        """
        data = security_entry.to_dict() if isinstance(security_entry, SecurityEntry) else security_entry
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.post(
            f"elements/{web_id}/securityentries", data=data, params=params
        )

    def update_security_entry(
        self,
        web_id: str,
        name: str,
        security_entry: Union[SecurityEntry, Dict],
        apply_to_children: bool = False,
    ) -> Dict:
        """Update a security entry for the element.

        Args:
            web_id: WebID of the element
            name: Name of the security entry
            security_entry: SecurityEntry model instance or dictionary with security entry data
            apply_to_children: Whether to apply to child elements

        Returns:
            Updated security entry response
        """
        data = security_entry.to_dict() if isinstance(security_entry, SecurityEntry) else security_entry
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.put(
            f"elements/{web_id}/securityentries/{self._encode_path(name)}",
            data=data,
            params=params,
        )

    def delete_security_entry(
        self, web_id: str, name: str, apply_to_children: bool = False
    ) -> Dict:
        """Delete a security entry from the element."""
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.delete(
            f"elements/{web_id}/securityentries/{self._encode_path(name)}",
            params=params,
        )

    def add_referenced_element(
        self, web_id: str, referenced_element_web_ids: list[str]
    ) -> Dict:
        """Add referenced elements to an element's attributes.

        Args:
            web_id: WebID of the element
            referenced_element_web_ids: List of WebIDs of elements to reference

        Returns:
            Response from the API
        """
        return self.client.post(
            f"elements/{web_id}/referencedelements", data=referenced_element_web_ids
        )

    def remove_referenced_element(
        self, web_id: str, referenced_element_web_ids: list[str]
    ) -> Dict:
        """Remove referenced elements from an element's attributes.

        Args:
            web_id: WebID of the element
            referenced_element_web_ids: List of WebIDs of elements to unreference

        Returns:
            Response from the API
        """
        return self.client.delete(
            f"elements/{web_id}/referencedelements", data=referenced_element_web_ids
        )

    def get_notification_rules(
        self, web_id: str, selected_fields: Optional[str] = None
    ) -> Dict:
        """Get notification rules for an element.

        Args:
            web_id: WebID of the element
            selected_fields: Optional semicolon-delimited list of fields to include

        Returns:
            Dictionary containing Items array with notification rule data
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/notificationrules", params=params)

    def create_notification_rule(self, web_id: str, notification_rule: Union[NotificationRule, Dict]) -> Dict:
        """Create a notification rule on the element.

        Args:
            web_id: WebID of the element
            notification_rule: NotificationRule model instance or dictionary with notification rule data

        Returns:
            Created notification rule response
        """
        data = notification_rule.to_dict() if isinstance(notification_rule, NotificationRule) else notification_rule
        return self.client.post(
            f"elements/{web_id}/notificationrules", data=data
        )

    def get_multiple(
        self, web_ids: list[str], selected_fields: Optional[str] = None
    ) -> Dict:
        """Get multiple elements by WebID.

        Args:
            web_ids: List of WebIDs to retrieve
            selected_fields: Optional semicolon-delimited list of fields to include

        Returns:
            Dictionary containing Items array with element data
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        params["webId"] = web_ids
        return self.client.get("elements/multiple", params=params)

    def create_search_by_attribute(
        self, web_id: str, query: str, no_results: bool = False
    ) -> Dict:
        """Create a search object for finding element attributes.

        Args:
            web_id: WebID of the element
            query: Search query using AF search syntax
            no_results: If true, only return search ID without results

        Returns:
            Search response with search ID and optionally results
        """
        params = {"query": query}
        if no_results:
            params["noResults"] = no_results
        return self.client.post(f"elements/{web_id}/searchattributes", params=params)

    def execute_search_by_attribute(
        self, search_id: str, selected_fields: Optional[str] = None
    ) -> Dict:
        """Execute a previously created attribute search.

        Args:
            search_id: Search ID from create_search_by_attribute
            selected_fields: Optional semicolon-delimited list of fields to include

        Returns:
            Dictionary containing Items array with attribute data
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/searchattributes/{search_id}", params=params)

    def get_elements_query(
        self,
        web_id: str,
        query: Optional[str] = None,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Query for child elements using AFSearch syntax.

        Args:
            web_id: WebID of the element
            query: AFSearch query string
            max_count: Maximum number of elements to return
            selected_fields: Optional semicolon-delimited list of fields to include

        Returns:
            Dictionary containing Items array with element data
        """
        params = {"maxCount": max_count}
        if query:
            params["query"] = query
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elements/{web_id}/elementsquery", params=params)


class ElementCategoryController(BaseController):
    """Controller for Element Category operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element category by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elementcategories/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element category by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elementcategories/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, category: Union[ElementCategory, Dict]) -> Dict:
        """Update an element category.

        Args:
            web_id: WebID of the category to update
            category: ElementCategory model instance or dictionary with category data

        Returns:
            Updated category response
        """
        data = category.to_dict() if isinstance(category, ElementCategory) else category
        return self.client.patch(f"elementcategories/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an element category."""
        return self.client.delete(f"elementcategories/{web_id}")


class ElementTemplateController(BaseController):
    """Controller for Element Template operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element template by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"elementtemplates/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get element template by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elementtemplates/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, template: Union[ElementTemplate, Dict]) -> Dict:
        """Update an element template.

        Args:
            web_id: WebID of the template to update
            template: ElementTemplate model instance or dictionary with template data

        Returns:
            Updated template response
        """
        data = template.to_dict() if isinstance(template, ElementTemplate) else template
        return self.client.patch(f"elementtemplates/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an element template."""
        return self.client.delete(f"elementtemplates/{web_id}")

    def get_attribute_templates(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get attribute templates for an element template."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"elementtemplates/{web_id}/attributetemplates", params=params
        )

    def create_attribute_template(self, web_id: str, template: Union[AttributeTemplate, Dict]) -> Dict:
        """Create an attribute template.

        Args:
            web_id: WebID of the element template
            template: AttributeTemplate model instance or dictionary with template data

        Returns:
            Created attribute template response
        """
        data = template.to_dict() if isinstance(template, AttributeTemplate) else template
        return self.client.post(
            f"elementtemplates/{web_id}/attributetemplates", data=data
        )
