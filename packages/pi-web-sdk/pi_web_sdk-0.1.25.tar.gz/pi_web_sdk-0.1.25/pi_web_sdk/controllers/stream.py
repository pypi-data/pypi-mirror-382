"""Controllers for stream and stream set endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from .base import BaseController

__all__ = [
    'StreamController',
    'StreamSetController',
    'BufferOption',
    'UpdateOption',
]


class BufferOption(Enum):
    """Buffer options for value updates.

    Indicates how to buffer value updates when writing to PI points or attributes.
    """
    DO_NOT_BUFFER = "DoNotBuffer"  # Update values without buffering
    BUFFER_IF_POSSIBLE = "BufferIfPossible"  # Attempt buffering, fallback to no buffer if fails
    BUFFER = "Buffer"  # Update values with buffering


class UpdateOption(Enum):
    """Update options for handling duplicate values.

    Indicates how to treat duplicate values when supported by the data reference.
    Client applications are responsible for understanding how these options interact
    with their attributes' data reference.
    """
    REPLACE = "Replace"  # Add the value, overwriting if exists at specified time (default)
    INSERT = "Insert"  # Add the value, preserving any existing values at specified time
    NO_REPLACE = "NoReplace"  # Add only if no value exists at specified time
    REPLACE_ONLY = "ReplaceOnly"  # Overwrite if exists, ignore if doesn't exist
    INSERT_NO_COMPRESSION = "InsertNoCompression"  # Insert without compression
    REMOVE = "Remove"  # Remove the value if one exists at specified time

class StreamController(BaseController):
    """Controller for Stream operations."""

    def get_value(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
        time: Union[str, datetime, None] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get current stream value."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        time_str = self._format_time(time)
        if time_str:
            params["time"] = time_str
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get(f"streams/{web_id}/value", params=params)

    def get_recorded(
        self,
        web_id: str,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        boundary_type: Optional[str] = None,
        max_count: Optional[int] = None,
        include_filtered_values: bool = False,
        filter_expression: Optional[str] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get recorded values."""
        params = {"includeFilteredValues": include_filtered_values}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if boundary_type:
            params["boundaryType"] = boundary_type
        if max_count:
            params["maxCount"] = max_count
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units

        return self.client.get(f"streams/{web_id}/recorded", params=params)

    def get_interpolated(
        self,
        web_id: str,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        interval: Optional[str] = None,
        filter_expression: Optional[str] = None,
        include_filtered_values: bool = False,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
        sync_time: Union[str, datetime, None] = None,
        sync_time_boundary_type: Optional[str] = None,
    ) -> Dict:
        """Get interpolated values."""
        params = {"includeFilteredValues": include_filtered_values}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if interval:
            params["interval"] = interval
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units
        sync_time_str = self._format_time(sync_time)
        if sync_time_str:
            params["syncTime"] = sync_time_str
        if sync_time_boundary_type:
            params["syncTimeBoundaryType"] = sync_time_boundary_type

        return self.client.get(f"streams/{web_id}/interpolated", params=params)

    def get_plot(
        self,
        web_id: str,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        intervals: Optional[int] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get plot values."""
        params = {}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if intervals:
            params["intervals"] = intervals
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units

        return self.client.get(f"streams/{web_id}/plot", params=params)

    def get_summary(
        self,
        web_id: str,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        summary_type: Optional[List[str]] = None,
        summary_duration: Optional[str] = None,
        calculation_basis: Optional[str] = None,
        time_type: Optional[str] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        filter_expression: Optional[str] = None,
    ) -> Dict:
        """Get summary values."""
        params = {}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if summary_type:
            params["summaryType"] = summary_type
        if summary_duration:
            params["summaryDuration"] = summary_duration
        if calculation_basis:
            params["calculationBasis"] = calculation_basis
        if time_type:
            params["timeType"] = time_type
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if filter_expression:
            params["filterExpression"] = filter_expression

        return self.client.get(f"streams/{web_id}/summary", params=params)

    def update_value(
        self,
        web_id: str,
        value: Dict,
        buffer_option: Optional[Union[str, BufferOption]] = None,
        update_option: Optional[Union[str, UpdateOption]] = None,
    ) -> Dict:
        """Update stream value.

        Args:
            web_id: WebID of the stream
            value: Dictionary with 'Value' and optional 'Timestamp' keys
            buffer_option: How to buffer the update (DoNotBuffer, BufferIfPossible, Buffer)
            update_option: How to handle duplicates (Replace, Insert, NoReplace, ReplaceOnly, InsertNoCompression, Remove)

        Returns:
            Response dictionary
        """
        params = {}
        if buffer_option:
            params["bufferOption"] = buffer_option.value if isinstance(buffer_option, BufferOption) else buffer_option
        if update_option:
            params["updateOption"] = update_option.value if isinstance(update_option, UpdateOption) else update_option
        return self.client.put(f"streams/{web_id}/value", data=value, params=params)

    def update_values(
        self,
        web_id: str,
        values: List[Dict],
        buffer_option: Optional[Union[str, BufferOption]] = None,
        update_option: Optional[Union[str, UpdateOption]] = None,
    ) -> Dict:
        """Update multiple stream values.

        Args:
            web_id: WebID of the stream
            values: List of dictionaries with 'Value' and 'Timestamp' keys
            buffer_option: How to buffer the updates (DoNotBuffer, BufferIfPossible, Buffer)
            update_option: How to handle duplicates (Replace, Insert, NoReplace, ReplaceOnly, InsertNoCompression, Remove)

        Returns:
            Response dictionary
        """
        params = {}
        if buffer_option:
            params["bufferOption"] = buffer_option.value if isinstance(buffer_option, BufferOption) else buffer_option
        if update_option:
            params["updateOption"] = update_option.value if isinstance(update_option, UpdateOption) else update_option
        return self.client.post(f"streams/{web_id}/recorded", data=values, params=params)

    def register_update(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Register for stream updates.

        Registers a stream for incremental updates. Returns a marker that can be used
        to retrieve updates via retrieve_update().

        Args:
            web_id: WebID of the stream
            selected_fields: Optional comma-separated list of fields to include

        Returns:
            Dictionary with LatestMarker and registration status
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.post(f"streams/{web_id}/updates", params=params)

    def retrieve_update(
        self,
        marker: str,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Retrieve stream updates using a marker.

        Gets incremental updates since the last marker position. Response includes
        a new LatestMarker for subsequent queries.

        Args:
            marker: Marker from previous register_update or retrieve_update call
            selected_fields: Optional comma-separated list of fields to include
            desired_units: Optional unit of measure for returned values

        Returns:
            Dictionary with Items (updates) and LatestMarker
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get(f"streams/updates/{marker}", params=params)

    def get_end(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get the last recorded value for a stream.

        Args:
            web_id: WebID of the stream
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned value

        Returns:
            Dictionary with the last recorded value
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get(f"streams/{web_id}/end", params=params)

    def get_recorded_at_time(
        self,
        web_id: str,
        time: Union[str, datetime],
        retrieval_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> Dict:
        """Get a single recorded value at a specific time.

        Args:
            web_id: WebID of the stream
            time: Timestamp for the value
            retrieval_mode: How to retrieve the value (Auto, At, Before, After, AtOrBefore, AtOrAfter)
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned value
            time_zone: Optional time zone

        Returns:
            Dictionary with the recorded value at the specified time
        """
        params = {"time": self._format_time(time)}
        if retrieval_mode:
            params["retrievalMode"] = retrieval_mode
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        return self.client.get(f"streams/{web_id}/recordedattime", params=params)

    def get_recorded_at_times(
        self,
        web_id: str,
        times: List[Union[str, datetime]],
        retrieval_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict:
        """Get recorded values at multiple specific times.

        Args:
            web_id: WebID of the stream
            times: List of timestamps for the values
            retrieval_mode: How to retrieve the values (Auto, At, Before, After, AtOrBefore, AtOrAfter)
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values
            time_zone: Optional time zone
            sort_order: Sort order (Ascending or Descending)

        Returns:
            Dictionary with Items array containing recorded values at the specified times
        """
        # Format all times
        formatted_times = [self._format_time(t) for t in times]
        params = {"time": formatted_times}
        if retrieval_mode:
            params["retrievalMode"] = retrieval_mode
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        if sort_order:
            params["sortOrder"] = sort_order
        return self.client.get(f"streams/{web_id}/recordedattimes", params=params)

    def get_interpolated_at_times(
        self,
        web_id: str,
        times: List[Union[str, datetime]],
        filter_expression: Optional[str] = None,
        include_filtered_values: bool = False,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict:
        """Get interpolated values at multiple specific times.

        Args:
            web_id: WebID of the stream
            times: List of timestamps for interpolation
            filter_expression: Optional filter expression
            include_filtered_values: Include filtered values in the response
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values
            time_zone: Optional time zone
            sort_order: Sort order (Ascending or Descending)

        Returns:
            Dictionary with Items array containing interpolated values at the specified times
        """
        # Format all times
        formatted_times = [self._format_time(t) for t in times]
        params = {
            "time": formatted_times,
            "includeFilteredValues": include_filtered_values,
        }
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        if sort_order:
            params["sortOrder"] = sort_order
        return self.client.get(f"streams/{web_id}/interpolatedattimes", params=params)

    def get_channel(
        self,
        web_id: str,
        include_initial_values: bool = False,
        heartbeat_rate: Optional[int] = None,
        web_id_type: Optional[str] = None,
    ) -> Dict:
        """Open a channel for streaming updates.

        Opens a WebSocket or Server-Sent Events channel for real-time value updates.

        Args:
            web_id: WebID of the stream
            include_initial_values: Include initial values when opening the channel
            heartbeat_rate: Heartbeat rate in seconds (default: 30)
            web_id_type: WebID type to use

        Returns:
            Dictionary with channel information
        """
        params = {"includeInitialValues": include_initial_values}
        if heartbeat_rate is not None:
            params["heartbeatRate"] = heartbeat_rate
        if web_id_type:
            params["webIdType"] = web_id_type
        return self.client.get(f"streams/{web_id}/channel", params=params)


class StreamSetController(BaseController):
    """Controller for Stream Set operations."""

    def get_values(
        self,
        web_ids: List[str],
        selected_fields: Optional[str] = None,
        time: Union[str, datetime, None] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get current values for multiple streams."""
        params = {"webId": web_ids}
        if selected_fields:
            params["selectedFields"] = selected_fields
        time_str = self._format_time(time)
        if time_str:
            params["time"] = time_str
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get("streamsets/value", params=params)

    def get_recorded(
        self,
        web_ids: List[str],
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        boundary_type: Optional[str] = None,
        max_count: Optional[int] = None,
        include_filtered_values: bool = False,
        filter_expression: Optional[str] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get recorded values for multiple streams."""
        params = {"webId": web_ids, "includeFilteredValues": include_filtered_values}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if boundary_type:
            params["boundaryType"] = boundary_type
        if max_count:
            params["maxCount"] = max_count
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units

        return self.client.get("streamsets/recorded", params=params)

    def get_interpolated(
        self,
        web_ids: List[str],
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        interval: Optional[str] = None,
        filter_expression: Optional[str] = None,
        include_filtered_values: bool = False,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
        sync_time: Union[str, datetime, None] = None,
        sync_time_boundary_type: Optional[str] = None,
    ) -> Dict:
        """Get interpolated values for multiple streams."""
        params = {"webId": web_ids, "includeFilteredValues": include_filtered_values}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if interval:
            params["interval"] = interval
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units
        sync_time_str = self._format_time(sync_time)
        if sync_time_str:
            params["syncTime"] = sync_time_str
        if sync_time_boundary_type:
            params["syncTimeBoundaryType"] = sync_time_boundary_type

        return self.client.get("streamsets/interpolated", params=params)

    def get_plot(
        self,
        web_ids: List[str],
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        intervals: Optional[int] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get plot values for multiple streams."""
        params = {"webId": web_ids}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if intervals:
            params["intervals"] = intervals
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if desired_units:
            params["desiredUnits"] = desired_units

        return self.client.get("streamsets/plot", params=params)

    def get_summaries(
        self,
        web_ids: List[str],
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        summary_type: Optional[List[str]] = None,
        summary_duration: Optional[str] = None,
        calculation_basis: Optional[str] = None,
        time_type: Optional[str] = None,
        selected_fields: Optional[str] = None,
        time_zone: Optional[str] = None,
        filter_expression: Optional[str] = None,
    ) -> Dict:
        """Get summary values for multiple streams."""
        params = {"webId": web_ids}
        start_time_str = self._format_time(start_time)
        if start_time_str:
            params["startTime"] = start_time_str
        end_time_str = self._format_time(end_time)
        if end_time_str:
            params["endTime"] = end_time_str
        if summary_type:
            params["summaryType"] = summary_type
        if summary_duration:
            params["summaryDuration"] = summary_duration
        if calculation_basis:
            params["calculationBasis"] = calculation_basis
        if time_type:
            params["timeType"] = time_type
        if selected_fields:
            params["selectedFields"] = selected_fields
        if time_zone:
            params["timeZone"] = time_zone
        if filter_expression:
            params["filterExpression"] = filter_expression

        return self.client.get("streamsets/summaries", params=params)

    def update_values(self, updates: List[Dict]) -> Dict:
        """Update values for multiple streams.

        Args:
            updates: List of dicts with 'WebId' and 'Value' keys
        """
        return self.client.put("streamsets/value", data=updates)

    def register_updates(
        self,
        web_ids: List[str],
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Register multiple streams for updates.

        Registers multiple streams for incremental updates. Returns markers that can be used
        to retrieve updates via retrieve_updates().

        Args:
            web_ids: List of stream WebIDs to register
            selected_fields: Optional comma-separated list of fields to include

        Returns:
            Dictionary with Items containing registration status for each stream and LatestMarker
        """
        params = {"webId": web_ids}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.post("streamsets/updates", params=params)

    def retrieve_updates(
        self,
        marker: str,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Retrieve updates for multiple streams using a marker.

        Gets incremental updates for all registered streams since the last marker position.
        Response includes a new LatestMarker for subsequent queries.

        Args:
            marker: Marker from previous register_updates or retrieve_updates call
            selected_fields: Optional comma-separated list of fields to include
            desired_units: Optional unit of measure for returned values

        Returns:
            Dictionary with Items (updates per stream) and LatestMarker
        """
        params = {"marker": marker}
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get("streamsets/updates", params=params)

    def get_end(
        self,
        web_ids: List[str],
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
    ) -> Dict:
        """Get the last recorded values for multiple streams.

        Args:
            web_ids: List of stream WebIDs
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values

        Returns:
            Dictionary with Items array containing last recorded value for each stream
        """
        params = {"webId": web_ids}
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        return self.client.get("streamsets/end", params=params)

    def get_recorded_at_time(
        self,
        web_ids: List[str],
        time: Union[str, datetime],
        retrieval_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> Dict:
        """Get recorded values at a specific time for multiple streams.

        Args:
            web_ids: List of stream WebIDs
            time: Timestamp for the values
            retrieval_mode: How to retrieve the values (Auto, At, Before, After, AtOrBefore, AtOrAfter)
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values
            time_zone: Optional time zone

        Returns:
            Dictionary with Items array containing recorded value for each stream at the specified time
        """
        params = {"webId": web_ids, "time": self._format_time(time)}
        if retrieval_mode:
            params["retrievalMode"] = retrieval_mode
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        return self.client.get("streamsets/recordedattime", params=params)

    def get_recorded_at_times(
        self,
        web_ids: List[str],
        times: List[Union[str, datetime]],
        retrieval_mode: Optional[str] = None,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict:
        """Get recorded values at multiple specific times for multiple streams.

        Args:
            web_ids: List of stream WebIDs
            times: List of timestamps for the values
            retrieval_mode: How to retrieve the values (Auto, At, Before, After, AtOrBefore, AtOrAfter)
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values
            time_zone: Optional time zone
            sort_order: Sort order (Ascending or Descending)

        Returns:
            Dictionary with Items array containing recorded values for each stream at the specified times
        """
        formatted_times = [self._format_time(t) for t in times]
        params = {"webId": web_ids, "time": formatted_times}
        if retrieval_mode:
            params["retrievalMode"] = retrieval_mode
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        if sort_order:
            params["sortOrder"] = sort_order
        return self.client.get("streamsets/recordedattimes", params=params)

    def get_interpolated_at_times(
        self,
        web_ids: List[str],
        times: List[Union[str, datetime]],
        filter_expression: Optional[str] = None,
        include_filtered_values: bool = False,
        selected_fields: Optional[str] = None,
        desired_units: Optional[str] = None,
        time_zone: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict:
        """Get interpolated values at multiple specific times for multiple streams.

        Args:
            web_ids: List of stream WebIDs
            times: List of timestamps for interpolation
            filter_expression: Optional filter expression
            include_filtered_values: Include filtered values in the response
            selected_fields: Optional semicolon-delimited list of fields to include
            desired_units: Optional unit of measure for returned values
            time_zone: Optional time zone
            sort_order: Sort order (Ascending or Descending)

        Returns:
            Dictionary with Items array containing interpolated values for each stream at the specified times
        """
        formatted_times = [self._format_time(t) for t in times]
        params = {
            "webId": web_ids,
            "time": formatted_times,
            "includeFilteredValues": include_filtered_values,
        }
        if filter_expression:
            params["filterExpression"] = filter_expression
        if selected_fields:
            params["selectedFields"] = selected_fields
        if desired_units:
            params["desiredUnits"] = desired_units
        if time_zone:
            params["timeZone"] = time_zone
        if sort_order:
            params["sortOrder"] = sort_order
        return self.client.get("streamsets/interpolatedattimes", params=params)

    def get_channel(
        self,
        web_ids: List[str],
        include_initial_values: bool = False,
        heartbeat_rate: Optional[int] = None,
        web_id_type: Optional[str] = None,
    ) -> Dict:
        """Open a channel for streaming updates for multiple streams.

        Args:
            web_ids: List of stream WebIDs
            include_initial_values: Include initial values when opening the channel
            heartbeat_rate: Heartbeat rate in seconds (default: 30)
            web_id_type: WebID type to use

        Returns:
            Dictionary with channel information
        """
        params = {"webId": web_ids, "includeInitialValues": include_initial_values}
        if heartbeat_rate is not None:
            params["heartbeatRate"] = heartbeat_rate
        if web_id_type:
            params["webIdType"] = web_id_type
        return self.client.get("streamsets/channel", params=params)
