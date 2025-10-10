"""Controllers for security-related endpoints."""

from __future__ import annotations

from typing import Dict, Optional, Union

from .base import BaseController
from ..models.security import SecurityIdentity, SecurityMapping

__all__ = [
    'SecurityIdentityController',
    'SecurityMappingController',
]


class SecurityIdentityController(BaseController):
    """Controller for Security Identity operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get security identity by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securityidentities/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get security identity by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"securityidentities/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, security_identity: Union[SecurityIdentity, Dict]) -> Dict:
        """Update a security identity.

        Args:
            web_id: WebID of the security identity to update
            security_identity: SecurityIdentity model instance or dictionary with security identity data

        Returns:
            Updated security identity response
        """
        data = security_identity.to_dict() if isinstance(security_identity, SecurityIdentity) else security_identity
        return self.client.patch(f"securityidentities/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete a security identity."""
        return self.client.delete(f"securityidentities/{web_id}")

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a security identity."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securityidentities/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a security identity."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securityidentities/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a security identity."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"securityidentities/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def get_security_mappings(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security mappings for a security identity."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securityidentities/{web_id}/securitymappings", params=params)


class SecurityMappingController(BaseController):
    """Controller for Security Mapping operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get security mapping by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securitymappings/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get security mapping by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"securitymappings/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, security_mapping: Union[SecurityMapping, Dict]) -> Dict:
        """Update a security mapping.

        Args:
            web_id: WebID of the security mapping to update
            security_mapping: SecurityMapping model instance or dictionary with security mapping data

        Returns:
            Updated security mapping response
        """
        data = security_mapping.to_dict() if isinstance(security_mapping, SecurityMapping) else security_mapping
        return self.client.patch(f"securitymappings/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete a security mapping."""
        return self.client.delete(f"securitymappings/{web_id}")

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a security mapping."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securitymappings/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a security mapping."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"securitymappings/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a security mapping."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"securitymappings/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )