"""Controllers for event frame endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional, Union

from .base import BaseController
from ..models.event import EventFrame

if TYPE_CHECKING:
    from ..client import PIWebAPIClient

__all__ = [
    'EventFrameController',
    'EventFrameHelpers',
]


class EventFrameController(BaseController):
    """Controller for Event Frame operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get an event frame by its WebID."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get an event frame by path."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        encoded_path = self._encode_path(path)
        return self.client.get(f"eventframes/path/{encoded_path}", params=params)

    def create(self, database_web_id: str, event_frame: Union[EventFrame, Dict]) -> Dict:
        """Create a new event frame in an asset database.
        
        Args:
            database_web_id: WebID of the parent database
            event_frame: EventFrame model instance or dictionary with event frame data
            
        Returns:
            Created event frame response
        """
        data = event_frame.to_dict() if isinstance(event_frame, EventFrame) else event_frame
        return self.client.post(
            f"assetdatabases/{database_web_id}/eventframes",
            data=data,
        )

    def update(self, web_id: str, event_frame: Union[EventFrame, Dict]) -> Dict:
        """Update an existing event frame.
        
        Args:
            web_id: WebID of the event frame to update
            event_frame: EventFrame model instance or dictionary with event frame data
            
        Returns:
            Updated event frame response
        """
        data = event_frame.to_dict() if isinstance(event_frame, EventFrame) else event_frame
        return self.client.patch(f"eventframes/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an event frame."""
        return self.client.delete(f"eventframes/{web_id}")

    def get_event_frames(
        self,
        database_web_id: str,
        name_filter: Optional[str] = None,
        category_name: Optional[str] = None,
        template_name: Optional[str] = None,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        search_full_hierarchy: bool = False,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Retrieve event frames from an asset database."""
        params: Dict[str, object] = {
            'searchFullHierarchy': search_full_hierarchy,
            'startIndex': start_index,
            'maxCount': max_count,
        }
        if name_filter:
            params['nameFilter'] = name_filter
        if category_name:
            params['categoryName'] = category_name
        if template_name:
            params['templateName'] = template_name
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params['startTime'] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params['endTime'] = end_time_str
        if sort_field:
            params['sortField'] = sort_field
        if sort_order:
            params['sortOrder'] = sort_order
        if selected_fields:
            params['selectedFields'] = selected_fields

        return self.client.get(
            f"assetdatabases/{database_web_id}/eventframes",
            params=params,
        )

    def get_attributes(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        category_name: Optional[str] = None,
        template_name: Optional[str] = None,
        value_type: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Retrieve attributes attached to an event frame."""
        params: Dict[str, object] = {
            'startIndex': start_index,
            'maxCount': max_count,
        }
        if name_filter:
            params['nameFilter'] = name_filter
        if category_name:
            params['categoryName'] = category_name
        if template_name:
            params['templateName'] = template_name
        if value_type:
            params['valueType'] = value_type
        if selected_fields:
            params['selectedFields'] = selected_fields

        return self.client.get(f"eventframes/{web_id}/attributes", params=params)

    def create_attribute(self, web_id: str, attribute: Dict) -> Dict:
        """Create an attribute for an event frame."""
        return self.client.post(f"eventframes/{web_id}/attributes", data=attribute)

    def create_child_event_frame(self, parent_web_id: str, event_frame: Union[EventFrame, Dict]) -> Dict:
        """Create a child event frame under a parent event frame.
        
        Args:
            parent_web_id: WebID of the parent event frame
            event_frame: EventFrame model instance or dictionary with event frame data
            
        Returns:
            Created child event frame response
        """
        data = event_frame.to_dict() if isinstance(event_frame, EventFrame) else event_frame
        return self.client.post(f"eventframes/{parent_web_id}/eventframes", data=data)

    def get_child_event_frames(
        self,
        parent_web_id: str,
        name_filter: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
        selected_fields: Optional[str] = None
    ) -> Dict:
        """Get child event frames of a parent event frame."""
        params: Dict[str, object] = {
            'startIndex': start_index,
            'maxCount': max_count,
        }
        if name_filter:
            params['nameFilter'] = name_filter
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{parent_web_id}/eventframes", params=params)

    def acknowledge(self, web_id: str) -> Dict:
        """Acknowledge an event frame."""
        return self.client.patch(f"eventframes/{web_id}/acknowledge")

    def get_annotations(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get annotations for an event frame."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}/annotations", params=params)

    def create_annotation(self, web_id: str, annotation: Dict) -> Dict:
        """Create an annotation on an event frame."""
        return self.client.post(f"eventframes/{web_id}/annotations", data=annotation)

    def get_annotation_by_id(
        self,
        web_id: str,
        annotation_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get a specific annotation by ID."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(
            f"eventframes/{web_id}/annotations/{annotation_id}", params=params
        )

    def update_annotation(
        self, web_id: str, annotation_id: str, annotation: Dict
    ) -> Dict:
        """Update an annotation."""
        return self.client.patch(
            f"eventframes/{web_id}/annotations/{annotation_id}", data=annotation
        )

    def delete_annotation(self, web_id: str, annotation_id: str) -> Dict:
        """Delete an annotation."""
        return self.client.delete(f"eventframes/{web_id}/annotations/{annotation_id}")

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get categories for an event frame."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}/categories", params=params)

    def capture_values(self, web_id: str) -> Dict:
        """Capture the event frame's attributes' values."""
        return self.client.post(f"eventframes/{web_id}/capturevalues")

    def find_event_frame_attributes(
        self,
        web_id: str,
        attribute_category: Optional[str] = None,
        attribute_description_filter: Optional[str] = None,
        attribute_name_filter: Optional[str] = None,
        attribute_type: Optional[str] = None,
        end_time: Union[str, datetime, None] = None,
        event_frame_category: Optional[str] = None,
        event_frame_description_filter: Optional[str] = None,
        event_frame_name_filter: Optional[str] = None,
        event_frame_template: Optional[str] = None,
        max_count: int = 1000,
        referenced_element_name_filter: Optional[str] = None,
        search_full_hierarchy: bool = False,
        search_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        start_time: Union[str, datetime, None] = None,
    ) -> Dict:
        """Search for event frame attributes by various criteria."""
        params: Dict[str, object] = {
            'startIndex': start_index,
            'maxCount': max_count,
            'searchFullHierarchy': search_full_hierarchy,
        }
        if attribute_category:
            params['attributeCategory'] = attribute_category
        if attribute_description_filter:
            params['attributeDescriptionFilter'] = attribute_description_filter
        if attribute_name_filter:
            params['attributeNameFilter'] = attribute_name_filter
        if attribute_type:
            params['attributeType'] = attribute_type
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params['endTime'] = end_time_str
        if event_frame_category:
            params['eventFrameCategory'] = event_frame_category
        if event_frame_description_filter:
            params['eventFrameDescriptionFilter'] = event_frame_description_filter
        if event_frame_name_filter:
            params['eventFrameNameFilter'] = event_frame_name_filter
        if event_frame_template:
            params['eventFrameTemplate'] = event_frame_template
        if referenced_element_name_filter:
            params['referencedElementNameFilter'] = referenced_element_name_filter
        if search_mode:
            params['searchMode'] = search_mode
        if sort_field:
            params['sortField'] = sort_field
        if sort_order:
            params['sortOrder'] = sort_order
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params['startTime'] = start_time_str
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(
            f"eventframes/{web_id}/eventframeattributes", params=params
        )

    def get_referenced_elements(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get elements referenced by this event frame's attributes."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}/referencedelements", params=params)

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for an event frame."""
        params: Dict[str, object] = {}
        if user_identity:
            params['userIdentity'] = user_identity
        if force_refresh:
            params['forceRefresh'] = force_refresh
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for an event frame."""
        params: Dict[str, object] = {}
        if name_filter:
            params['nameFilter'] = name_filter
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(f"eventframes/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for an event frame."""
        params: Dict[str, object] = {}
        if selected_fields:
            params['selectedFields'] = selected_fields
        return self.client.get(
            f"eventframes/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(
        self, web_id: str, security_entry: Dict, apply_to_children: bool = False
    ) -> Dict:
        """Create a security entry for the event frame."""
        params: Dict[str, object] = {}
        if apply_to_children:
            params['applyToChildren'] = apply_to_children
        return self.client.post(
            f"eventframes/{web_id}/securityentries", data=security_entry, params=params
        )

    def update_security_entry(
        self,
        web_id: str,
        name: str,
        security_entry: Dict,
        apply_to_children: bool = False,
    ) -> Dict:
        """Update a security entry for the event frame."""
        params: Dict[str, object] = {}
        if apply_to_children:
            params['applyToChildren'] = apply_to_children
        return self.client.put(
            f"eventframes/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry,
            params=params
        )

    def delete_security_entry(
        self, web_id: str, name: str, apply_to_children: bool = False
    ) -> Dict:
        """Delete a security entry from the event frame."""
        params: Dict[str, object] = {}
        if apply_to_children:
            params['applyToChildren'] = apply_to_children
        return self.client.delete(
            f"eventframes/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )


class EventFrameHelpers:
    """High-level helper methods for common event frame workflows.

    This class provides convenience methods that combine multiple API calls
    into single operations for common use cases like creating event frames
    with attributes.
    """

    def __init__(self, client: PIWebAPIClient):
        """Initialize helpers with PI Web API client.

        Args:
            client: PIWebAPIClient instance
        """
        self.client = client

    def create_event_frame_with_attributes(
        self,
        database_web_id: str,
        name: str,
        description: str,
        start_time: Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None,
        attributes: Optional[Dict[str, str]] = None,
        template_name: Optional[str] = None,
        category_names: Optional[list[str]] = None,
        referenced_element_web_id: Optional[str] = None,
    ) -> Dict:
        """Create a root event frame with attributes in one operation.

        This is a convenience method that:
        1. Creates the event frame
        2. Creates attributes with the specified names
        3. Sets initial values for each attribute

        Args:
            database_web_id: WebID of the parent asset database
            name: Name of the event frame
            description: Description of the event frame
            start_time: Start time (datetime or ISO string)
            end_time: Optional end time (datetime or ISO string)
            attributes: Dictionary of attribute names to initial values
            template_name: Optional template name to use
            category_names: Optional list of category names
            referenced_element_web_id: Optional referenced element WebID

        Returns:
            Created event frame dictionary with WebId

        Example:
            >>> from datetime import datetime
            >>> event = helpers.create_event_frame_with_attributes(
            ...     database_web_id="F1AbC...",
            ...     name="Batch001",
            ...     description="Production batch",
            ...     start_time=datetime.now(),
            ...     attributes={
            ...         "Operator": "John Doe",
            ...         "Product": "Widget A",
            ...         "Quantity": "1000"
            ...     }
            ... )
        """
        # Create the event frame
        event_frame = EventFrame(
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            template_name=template_name,
            category_names=category_names,
            referenced_element_web_id=referenced_element_web_id,
        )
        event = self.client.event_frame.create(database_web_id, event_frame)

        # Add attributes if provided
        if attributes:
            for attr_name, attr_value in attributes.items():
                # Create attribute
                attribute = self.client.event_frame.create_attribute(
                    event["WebId"],
                    {"Name": attr_name, "Type": "String"},
                )
                # Set initial value
                self.client.attribute.set_value(
                    attribute["WebId"],
                    {"Value": str(attr_value)}
                )

        return event

    def create_child_event_frame_with_attributes(
        self,
        parent_web_id: str,
        name: str,
        description: str,
        start_time: Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None,
        attributes: Optional[Dict[str, str]] = None,
        template_name: Optional[str] = None,
        category_names: Optional[list[str]] = None,
        referenced_element_web_id: Optional[str] = None,
    ) -> Dict:
        """Create a child event frame with attributes in one operation.

        This is a convenience method that:
        1. Creates a child event frame under the specified parent
        2. Creates attributes with the specified names
        3. Sets initial values for each attribute

        Args:
            parent_web_id: WebID of the parent event frame
            name: Name of the event frame
            description: Description of the event frame
            start_time: Start time (datetime or ISO string)
            end_time: Optional end time (datetime or ISO string)
            attributes: Dictionary of attribute names to initial values
            template_name: Optional template name to use
            category_names: Optional list of category names
            referenced_element_web_id: Optional referenced element WebID

        Returns:
            Created child event frame dictionary with WebId

        Example:
            >>> event = helpers.create_child_event_frame_with_attributes(
            ...     parent_web_id="F1AbC...",
            ...     name="Step1",
            ...     description="Mixing step",
            ...     start_time=datetime.now(),
            ...     attributes={
            ...         "Duration": "30",
            ...         "Temperature": "75"
            ...     }
            ... )
        """
        # Create the child event frame
        event_frame = EventFrame(
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            template_name=template_name,
            category_names=category_names,
            referenced_element_web_id=referenced_element_web_id,
        )
        event = self.client.event_frame.create_child_event_frame(
            parent_web_id,
            event_frame
        )

        # Add attributes if provided
        if attributes:
            for attr_name, attr_value in attributes.items():
                # Create attribute
                attribute = self.client.event_frame.create_attribute(
                    event["WebId"],
                    {"Name": attr_name, "Type": "String"},
                )
                # Set initial value
                self.client.attribute.set_value(
                    attribute["WebId"],
                    {"Value": str(attr_value)}
                )

        return event

    def update_event_frame_attributes(
        self,
        event_web_id: str,
        attributes: Dict[str, str],
    ) -> Dict[str, Dict]:
        """Update multiple attribute values on an event frame.

        Args:
            event_web_id: WebID of the event frame
            attributes: Dictionary mapping attribute names to new values

        Returns:
            Dictionary mapping attribute names to update responses

        Example:
            >>> responses = helpers.update_event_frame_attributes(
            ...     "F1AbC...",
            ...     {"Status": "Complete", "EndTemperature": "80"}
            ... )
        """
        # Get all attributes for the event frame
        attrs_response = self.client.event_frame.get_attributes(event_web_id)
        attrs_by_name = {
            attr["Name"]: attr
            for attr in attrs_response.get("Items", [])
        }

        # Update each attribute
        results = {}
        for attr_name, new_value in attributes.items():
            if attr_name in attrs_by_name:
                attr_web_id = attrs_by_name[attr_name]["WebId"]
                response = self.client.attribute.set_value(
                    attr_web_id,
                    {"Value": str(new_value)}
                )
                results[attr_name] = response
            else:
                results[attr_name] = {
                    "error": f"Attribute '{attr_name}' not found"
                }

        return results

    def create_event_frame_hierarchy(
        self,
        database_web_id: str,
        root_name: str,
        root_description: str,
        start_time: Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None,
        root_attributes: Optional[Dict[str, str]] = None,
        children: Optional[list[Dict]] = None,
    ) -> Dict:
        """Create a hierarchical event frame structure in one operation.

        Args:
            database_web_id: WebID of the parent asset database
            root_name: Name of the root event frame
            root_description: Description of the root event frame
            start_time: Start time for root event frame
            end_time: Optional end time for root event frame
            root_attributes: Optional attributes for root event frame
            children: Optional list of child event frame specs, each with:
                - name: Child name
                - description: Child description
                - start_time: Child start time
                - end_time: Optional child end time
                - attributes: Optional child attributes dict

        Returns:
            Dictionary with 'root' event frame and 'children' list

        Example:
            >>> hierarchy = helpers.create_event_frame_hierarchy(
            ...     database_web_id="F1AbC...",
            ...     root_name="Batch001",
            ...     root_description="Production batch",
            ...     start_time=datetime.now(),
            ...     root_attributes={"Operator": "John"},
            ...     children=[
            ...         {
            ...             "name": "Mix",
            ...             "description": "Mixing step",
            ...             "start_time": datetime.now(),
            ...             "attributes": {"Duration": "30"}
            ...         },
            ...         {
            ...             "name": "Package",
            ...             "description": "Packaging step",
            ...             "start_time": datetime.now() + timedelta(minutes=30)
            ...         }
            ...     ]
            ... )
        """
        # Create root event frame
        root = self.create_event_frame_with_attributes(
            database_web_id=database_web_id,
            name=root_name,
            description=root_description,
            start_time=start_time,
            end_time=end_time,
            attributes=root_attributes,
        )

        # Create child event frames
        created_children = []
        if children:
            for child_spec in children:
                child = self.create_child_event_frame_with_attributes(
                    parent_web_id=root["WebId"],
                    name=child_spec["name"],
                    description=child_spec.get("description", ""),
                    start_time=child_spec["start_time"],
                    end_time=child_spec.get("end_time"),
                    attributes=child_spec.get("attributes"),
                    template_name=child_spec.get("template_name"),
                    category_names=child_spec.get("category_names"),
                    referenced_element_web_id=child_spec.get("referenced_element_web_id"),
                )
                created_children.append(child)

        return {
            "root": root,
            "children": created_children,
        }

    def get_event_frame_with_attributes(
        self,
        event_web_id: str,
        include_values: bool = True,
    ) -> Dict:
        """Get an event frame with all its attributes and optionally their values.

        Args:
            event_web_id: WebID of the event frame
            include_values: Whether to fetch attribute values

        Returns:
            Event frame dictionary with 'attributes' key containing attribute details

        Example:
            >>> event = helpers.get_event_frame_with_attributes("F1AbC...")
            >>> for attr in event["attributes"]:
            ...     print(f"{attr['Name']}: {attr.get('Value')}")
        """
        # Get event frame
        event = self.client.event_frame.get(event_web_id)

        # Get attributes
        attrs_response = self.client.event_frame.get_attributes(event_web_id)
        attributes = attrs_response.get("Items", [])

        # Optionally get values
        if include_values:
            for attr in attributes:
                try:
                    value_response = self.client.attribute.get_value(attr["WebId"])
                    attr["Value"] = value_response.get("Value")
                    attr["Timestamp"] = value_response.get("Timestamp")
                except Exception:
                    attr["Value"] = None
                    attr["Timestamp"] = None

        event["attributes"] = attributes
        return event

    def close_event_frame(
        self,
        event_web_id: str,
        end_time: Optional[Union[str, datetime]] = None,
        capture_values: bool = True,
    ) -> Dict:
        """Close an event frame by setting its end time and optionally capturing values.

        Args:
            event_web_id: WebID of the event frame
            end_time: End time (defaults to current time)
            capture_values: Whether to capture attribute values at end time

        Returns:
            Updated event frame dictionary

        Example:
            >>> event = helpers.close_event_frame("F1AbC...", capture_values=True)
        """
        # Use current time if not specified
        if end_time is None:
            end_time = datetime.now()

        # Update event frame with end time
        event_update = EventFrame(end_time=end_time)
        self.client.event_frame.update(event_web_id, event_update)

        # Optionally capture values
        if capture_values:
            self.client.event_frame.capture_values(event_web_id)

        # Return updated event frame
        return self.client.event_frame.get(event_web_id)
