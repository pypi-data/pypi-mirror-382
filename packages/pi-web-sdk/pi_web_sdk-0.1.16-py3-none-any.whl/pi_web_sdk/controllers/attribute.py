"""Controllers for attribute endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Union

from .base import BaseController
from ..models.attribute import Attribute, AttributeCategory, AttributeTemplate

__all__ = [
    'AttributeController',
    'AttributeCategoryController',
    'AttributeTemplateController',
]

class AttributeController(BaseController):
    """Controller for Attribute operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributes/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"attributes/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, attribute: Union[Attribute, Dict]) -> Dict:
        """Update an attribute.
        
        Args:
            web_id: WebID of the attribute to update
            attribute: Attribute model instance or dictionary with attribute data
            
        Returns:
            Updated attribute response
        """
        data = attribute.to_dict() if isinstance(attribute, Attribute) else attribute
        return self.client.patch(f"attributes/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an attribute."""
        return self.client.delete(f"attributes/{web_id}")

    def get_value(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
        time: Union[str, datetime, None] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get attribute value."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        time_str = self._format_time(time)
        if time_str:
            params["time"] = time_str
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get(f"attributes/{web_id}/value", params=params)

    def set_value(
        self,
        web_id: str,
        value: Dict,
        buffer_option: Optional[str] = None,
        update_option: Optional[str] = None,
    ) -> Dict:
        """Set attribute value."""
        params = {}
        if buffer_option:
            params["bufferOption"] = buffer_option
        if update_option:
            params["updateOption"] = update_option
        return self.client.put(f"attributes/{web_id}/value", data=value, params=params)


class AttributeCategoryController(BaseController):
    """Controller for Attribute Category operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute category by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributecategories/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute category by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"attributecategories/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, category: Union[AttributeCategory, Dict]) -> Dict:
        """Update an attribute category.
        
        Args:
            web_id: WebID of the category to update
            category: AttributeCategory model instance or dictionary with category data
            
        Returns:
            Updated category response
        """
        data = category.to_dict() if isinstance(category, AttributeCategory) else category
        return self.client.patch(f"attributecategories/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an attribute category."""
        return self.client.delete(f"attributecategories/{web_id}")


class AttributeTemplateController(BaseController):
    """Controller for Attribute Template operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute template by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributetemplates/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute template by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"attributetemplates/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, template: Union[AttributeTemplate, Dict]) -> Dict:
        """Update an attribute template.
        
        Args:
            web_id: WebID of the template to update
            template: AttributeTemplate model instance or dictionary with template data
            
        Returns:
            Updated template response
        """
        data = template.to_dict() if isinstance(template, AttributeTemplate) else template
        return self.client.patch(f"attributetemplates/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an attribute template."""
        return self.client.delete(f"attributetemplates/{web_id}")
