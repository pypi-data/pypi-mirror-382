"""Controllers for unit endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

__all__ = [
    'UnitController',
    'UnitClassController',
]


class UnitController(BaseController):
    """Controller for Unit operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get unit by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"units/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get unit by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"units/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, unit: Dict) -> Dict:
        """Update a unit."""
        return self.client.patch(f"units/{web_id}", data=unit)

    def delete(self, web_id: str) -> Dict:
        """Delete a unit."""
        return self.client.delete(f"units/{web_id}")


class UnitClassController(BaseController):
    """Controller for Unit Class operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get unit class by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"unitclasses/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get unit class by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"unitclasses/path/{self._encode_path(path)}", params=params
        )