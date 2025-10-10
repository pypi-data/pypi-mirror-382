"""Shared helpers for PI Web API controllers."""

from __future__ import annotations

import urllib.parse
from datetime import datetime
from typing import Optional, Union, Callable, Any, Dict

__all__ = ['BaseController']

class BaseController:
    """Base controller class."""

    def __init__(self, client: "PIWebAPIClient"):
        self.client = client

    def _encode_path(self, path: str) -> str:
        """URL encode a path parameter."""
        return urllib.parse.quote(path, safe="")

    def _format_time(self, time_value: Union[str, datetime, None]) -> Optional[str]:
        """Convert time value to PI Web API compatible string format.

        Args:
            time_value: Time as string, datetime object, or None

        Returns:
            Formatted time string or None if input is None

        Notes:
            - String values are returned as-is (allows special values like "*", "Today", etc.)
            - datetime objects are converted to ISO 8601 format
            - UTC timezone (+00:00) is converted to 'Z' suffix for PI Web API compatibility
            - Timezone-naive datetimes are treated as local time
        """
        if time_value is None:
            return None
        if isinstance(time_value, str):
            return time_value
        if isinstance(time_value, datetime):
            # Use isoformat() which produces ISO 8601 compliant strings
            # Format: YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM]
            time_str = time_value.isoformat()
            # Convert +00:00 to Z for better PI Web API compatibility
            if time_str.endswith('+00:00'):
                time_str = time_str[:-6] + 'Z'
            return time_str
        raise TypeError(f"Time value must be str, datetime, or None, got {type(time_value)}")

    def _create_or_get(
        self,
        create_func: Callable[..., Dict],
        get_func: Callable[..., Dict],
        create_args: tuple = (),
        create_kwargs: Optional[Dict[str, Any]] = None,
        get_args: tuple = (),
        get_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Helper to create a resource or get it if it already exists.

        Args:
            create_func: Function to call for creating the resource
            get_func: Function to call for getting the resource if create fails
            create_args: Positional arguments for create_func
            create_kwargs: Keyword arguments for create_func
            get_args: Positional arguments for get_func
            get_kwargs: Keyword arguments for get_func

        Returns:
            The created or retrieved resource

        Example:
            result = self._create_or_get(
                create_func=self.create_element,
                get_func=self.get_elements,
                create_args=(parent_web_id, element_data),
                get_args=(parent_web_id,),
                get_kwargs={"name_filter": element_data["Name"]}
            )
        """
        create_kwargs = create_kwargs or {}
        get_kwargs = get_kwargs or {}

        try:
            # Try to create the resource
            return create_func(*create_args, **create_kwargs)
        except Exception:
            # If creation fails, try to get the existing resource
            result = get_func(*get_args, **get_kwargs)
            # If get returns an Items list, return the first item
            if isinstance(result, dict) and "Items" in result and result["Items"]:
                return result["Items"][0]
            return result
