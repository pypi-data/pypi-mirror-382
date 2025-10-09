"""Controller for table endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

__all__ = [
    'TableController',
    'TableCategoryController',
]


class TableController(BaseController):
    """Controller for Table operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get table by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tables/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get table by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"tables/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, table: Dict) -> Dict:
        """Update a table."""
        return self.client.patch(f"tables/{web_id}", data=table)

    def delete(self, web_id: str) -> Dict:
        """Delete a table."""
        return self.client.delete(f"tables/{web_id}")

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get categories for a table."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tables/{web_id}/categories", params=params)

    def get_data(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get data stored in the table."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tables/{web_id}/data", params=params)

    def update_data(self, web_id: str, data: Dict) -> Dict:
        """Update the data stored in the table."""
        return self.client.put(f"tables/{web_id}/data", data=data)

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a table."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tables/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a table."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tables/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a table."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"tables/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(self, web_id: str, security_entry: Dict) -> Dict:
        """Create a security entry for the table."""
        return self.client.post(
            f"tables/{web_id}/securityentries", data=security_entry
        )

    def update_security_entry(
        self, web_id: str, name: str, security_entry: Dict
    ) -> Dict:
        """Update a security entry for the table."""
        return self.client.put(
            f"tables/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry
        )

    def delete_security_entry(self, web_id: str, name: str) -> Dict:
        """Delete a security entry from the table."""
        return self.client.delete(
            f"tables/{web_id}/securityentries/{self._encode_path(name)}"
        )


class TableCategoryController(BaseController):
    """Controller for Table Category operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get table category by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tablecategories/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get table category by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"tablecategories/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, table_category: Dict) -> Dict:
        """Update a table category."""
        return self.client.patch(f"tablecategories/{web_id}", data=table_category)

    def delete(self, web_id: str) -> Dict:
        """Delete a table category."""
        return self.client.delete(f"tablecategories/{web_id}")

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a table category."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tablecategories/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a table category."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"tablecategories/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a table category."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"tablecategories/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(self, web_id: str, security_entry: Dict) -> Dict:
        """Create a security entry for the table category."""
        return self.client.post(
            f"tablecategories/{web_id}/securityentries", data=security_entry
        )

    def update_security_entry(
        self, web_id: str, name: str, security_entry: Dict
    ) -> Dict:
        """Update a security entry for the table category."""
        return self.client.put(
            f"tablecategories/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry
        )

    def delete_security_entry(self, web_id: str, name: str) -> Dict:
        """Delete a security entry from the table category."""
        return self.client.delete(
            f"tablecategories/{web_id}/securityentries/{self._encode_path(name)}"
        )
