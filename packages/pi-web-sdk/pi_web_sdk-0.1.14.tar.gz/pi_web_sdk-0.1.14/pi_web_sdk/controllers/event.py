"""Controllers for event frame endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Union

from .base import BaseController
from ..models.event import EventFrame

__all__ = [
    'EventFrameController',
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
