"""Controllers for batch and related operations."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Union

from .base import BaseController

__all__ = [
    'BatchController',
    'CalculationController',
    'ChannelController',
]

class BatchController(BaseController):
    """Controller for Batch operations."""

    def execute(self, requests: List[Dict]) -> Dict:
        """Execute multiple API requests in a single batch call.

        Args:
            requests: List of request dictionaries with keys:
                - Method: HTTP method (GET, POST, PUT, etc.)
                - Resource: API endpoint path
                - Parameters: Optional query parameters
                - Content: Optional request body
                - Headers: Optional additional headers
        """
        return self.client.post("batch", data=requests)

    def replace_time_range_values(
        self, point_webid: str, start_time: Union[str, datetime], end_time: Union[str, datetime], new_values: List[Dict]
    ) -> Dict:
        """Delete all values in a time range and write new ones.

        Args:
            point_webid: WebID of the point
            start_time: Start of time range (string or datetime object)
            end_time: End of time range (string or datetime object)
            new_values: List of value dicts with Timestamp, Value, etc.
        """
        # First, get existing values in the time range
        existing_data = self.client.stream.get_recorded(
            web_id=point_webid,
            start_time=self._format_time(start_time),
            end_time=self._format_time(end_time),
            max_count=10_000,  # Adjust as needed
        )

        requests = []

        # Add delete requests for each existing timestamp
        for item in existing_data.get("Items", []):
            timestamp = item.get("Timestamp")
            if timestamp:
                requests.append(
                    {
                        "Method": "PUT",
                        "Resource": f"streams/{point_webid}/value",
                        "Content": {"Timestamp": timestamp, "Value": None},
                        "Parameters": {"updateOption": "Remove"},
                    }
                )

        # Add write requests for new values
        for value in new_values:
            requests.append(
                {
                    "Method": "PUT",
                    "Resource": f"streams/{point_webid}/value",
                    "Content": value,
                    "Parameters": {"updateOption": "Replace"},
                }
            )

        return self.execute(requests)


class CalculationController(BaseController):
    """Controller for Calculation operations."""

    def get(self, web_id: str) -> Dict:
        """Get calculation by WebID."""
        return self.client.get(f"calculations/{web_id}")

    def get_by_path(self, path: str) -> Dict:
        """Get calculation by path."""
        return self.client.get(f"calculations/path/{self._encode_path(path)}")

    def update(self, web_id: str, calculation: Dict) -> Dict:
        """Update a calculation."""
        return self.client.patch(f"calculations/{web_id}", data=calculation)

    def delete(self, web_id: str) -> Dict:
        """Delete a calculation."""
        return self.client.delete(f"calculations/{web_id}")


class ChannelController(BaseController):
    """Controller for Channel operations."""

    def get(self, web_id: str) -> Dict:
        """Get channel by WebID."""
        return self.client.get(f"channels/{web_id}")

    def get_by_path(self, path: str) -> Dict:
        """Get channel by path."""
        return self.client.get(f"channels/path/{self._encode_path(path)}")

    def update(self, web_id: str, channel: Dict) -> Dict:
        """Update a channel."""
        return self.client.patch(f"channels/{web_id}", data=channel)

    def delete(self, web_id: str) -> Dict:
        """Delete a channel."""
        return self.client.delete(f"channels/{web_id}")
