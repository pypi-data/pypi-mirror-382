"""Controllers for time rule endpoints."""

from __future__ import annotations

from typing import Dict, Optional, Union

from .base import BaseController
from ..models.time_rule import TimeRule, TimeRulePlugIn

__all__ = [
    'TimeRuleController',
    'TimeRulePlugInController',
]


class TimeRuleController(BaseController):
    """Controller for Time Rule operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get time rule by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"timerules/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get time rule by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"timerules/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, time_rule: Union[TimeRule, Dict]) -> Dict:
        """Update a time rule.

        Args:
            web_id: WebID of the time rule to update
            time_rule: TimeRule model instance or dictionary with time rule data

        Returns:
            Updated time rule response
        """
        data = time_rule.to_dict() if isinstance(time_rule, TimeRule) else time_rule
        return self.client.patch(f"timerules/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete a time rule."""
        return self.client.delete(f"timerules/{web_id}")


class TimeRulePlugInController(BaseController):
    """Controller for Time Rule PlugIn operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get time rule plugin by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"timeruleplugins/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get time rule plugin by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"timeruleplugins/path/{self._encode_path(path)}", params=params
        )