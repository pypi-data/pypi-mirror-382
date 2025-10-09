"""Controllers for enumeration set and value endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

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

    def update(self, web_id: str, enumeration_set: Dict) -> Dict:
        """Update an enumeration set."""
        return self.client.patch(f"enumerationsets/{web_id}", data=enumeration_set)

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

    def create_value(self, web_id: str, value: Dict) -> Dict:
        """Create an enumeration value."""
        return self.client.post(f"enumerationsets/{web_id}/values", data=value)


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

    def update(self, web_id: str, enumeration_value: Dict) -> Dict:
        """Update an enumeration value."""
        return self.client.patch(f"enumerationvalues/{web_id}", data=enumeration_value)

    def delete(self, web_id: str) -> Dict:
        """Delete an enumeration value."""
        return self.client.delete(f"enumerationvalues/{web_id}")
