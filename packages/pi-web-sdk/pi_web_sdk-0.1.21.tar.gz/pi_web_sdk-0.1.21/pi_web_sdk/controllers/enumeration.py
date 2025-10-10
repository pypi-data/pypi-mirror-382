"""Controllers for enumeration set and value endpoints."""

from __future__ import annotations

from typing import Dict, Optional, Union

from .base import BaseController
from ..models.enumeration import EnumerationSet, EnumerationValue

__all__ = [
    'EnumerationSetController',
    'EnumerationValueController',
]

class EnumerationSetController(BaseController):
    """Controller for Enumeration Set operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get enumeration set by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"enumerationsets/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get enumeration set by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"enumerationsets/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, enumeration_set: Union[EnumerationSet, Dict]) -> Dict:
        """Update an enumeration set.

        Args:
            web_id: WebID of the enumeration set to update
            enumeration_set: EnumerationSet model instance or dictionary with enumeration set data

        Returns:
            Updated enumeration set response
        """
        data = enumeration_set.to_dict() if isinstance(enumeration_set, EnumerationSet) else enumeration_set
        return self.client.patch(f"enumerationsets/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an enumeration set."""
        return self.client.delete(f"enumerationsets/{web_id}")

    def get_values(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get enumeration values for an enumeration set."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"enumerationsets/{web_id}/values", params=params)

    def create_value(self, web_id: str, value: Union[EnumerationValue, Dict]) -> Dict:
        """Create an enumeration value.

        Args:
            web_id: WebID of the enumeration set
            value: EnumerationValue model instance or dictionary with enumeration value data

        Returns:
            Created enumeration value response
        """
        data = value.to_dict() if isinstance(value, EnumerationValue) else value
        return self.client.post(f"enumerationsets/{web_id}/values", data=data)


class EnumerationValueController(BaseController):
    """Controller for Enumeration Value operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get enumeration value by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"enumerationvalues/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get enumeration value by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"enumerationvalues/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, enumeration_value: Union[EnumerationValue, Dict]) -> Dict:
        """Update an enumeration value.

        Args:
            web_id: WebID of the enumeration value to update
            enumeration_value: EnumerationValue model instance or dictionary with enumeration value data

        Returns:
            Updated enumeration value response
        """
        data = enumeration_value.to_dict() if isinstance(enumeration_value, EnumerationValue) else enumeration_value
        return self.client.patch(f"enumerationvalues/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an enumeration value."""
        return self.client.delete(f"enumerationvalues/{web_id}")
