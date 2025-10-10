"""Controller for attribute trait endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

__all__ = ['AttributeTraitController']


class AttributeTraitController(BaseController):
    """Controller for Attribute Trait operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get attribute trait by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributetraits/{web_id}", params=params)

    def get_by_name(
        self,
        name: str,
        selected_fields: Optional[str] = None
    ) -> Dict:
        """Get attribute trait by name."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributetraits", params={"name": name, **params})

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None
    ) -> Dict:
        """Get categories for an attribute trait."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"attributetraits/{web_id}/categories", params=params)
