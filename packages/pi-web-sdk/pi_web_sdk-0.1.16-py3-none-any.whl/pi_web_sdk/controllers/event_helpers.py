"""High-level convenience methods for event frame operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional, Union

if TYPE_CHECKING:
    from ..client import PIWebAPIClient


__all__ = [
    'EventFrameHelpers',
]


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
        from ..models.event import EventFrame

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
        from ..models.event import EventFrame

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
        from ..models.event import EventFrame

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
