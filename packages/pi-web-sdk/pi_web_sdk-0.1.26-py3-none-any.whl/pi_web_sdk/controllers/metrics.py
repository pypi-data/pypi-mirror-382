"""Controllers for metrics endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Union

from .base import BaseController

__all__ = [
    'MetricsController',
]


class MetricsController(BaseController):
    """Controller for Metrics operations."""

    def environment(self) -> Dict:
        """Get environment metrics."""
        return self.client.get("metrics/environment")

    def landing(self) -> Dict:
        """Get landing page metrics."""
        return self.client.get("metrics/landing")

    def requests(
        self,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        interval: Optional[str] = None,
    ) -> Dict:
        """Get request metrics."""
        params = {}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if interval:
            params["interval"] = interval
        return self.client.get("metrics/requests", params=params)