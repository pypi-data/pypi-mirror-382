"""Controllers for system-level endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

__all__ = [
    'HomeController',
    'SystemController',
    'ConfigurationController',
]

class HomeController(BaseController):
    """Controller for Home endpoint."""

    def get(self) -> Dict:
        """Get the home page links."""
        return self.client.get("")


class SystemController(BaseController):
    """Controller for System operations."""

    def landing(self) -> Dict:
        """Get system landing page."""
        return self.client.get("system")

    def cache_instances(self) -> Dict:
        """Get cache instances."""
        return self.client.get("system/cacheinstances")

    def user_info(self) -> Dict:
        """Get current user information."""
        return self.client.get("system/userinfo")

    def versions(self) -> Dict:
        """Get system version information."""
        return self.client.get("system/versions")

    def status(self) -> Dict:
        """Get system status."""
        return self.client.get("system/status")


class ConfigurationController(BaseController):
    """Controller for Configuration operations."""

    def list(self) -> Dict:
        """List all configurations."""
        return self.client.get("configuration")

    def get(self, item_id: str) -> Dict:
        """Get configuration item by ID."""
        return self.client.get(f"configuration/{item_id}")

    def update(self, item_id: str, config: Dict) -> Dict:
        """Update a configuration item."""
        return self.client.put(f"configuration/{item_id}", data=config)

    def delete(self, item_id: str) -> Dict:
        """Delete a configuration item."""
        return self.client.delete(f"configuration/{item_id}")
