"""Data models for data server and point-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, Union
from .base import PIWebAPIObject


__all__ = [
    "DataServer",
    "Point",
    "TimedValue",
    "StreamValue",
    "StreamValues",
]


@dataclass
class DataServer(PIWebAPIObject):
    """PI Data Server object."""
    
    server_version: Optional[str] = None
    is_connected: Optional[bool] = None
    server_time: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.server_version is not None or not exclude_none:
            result['ServerVersion'] = self.server_version
        if self.is_connected is not None or not exclude_none:
            result['IsConnected'] = self.is_connected
        if self.server_time is not None or not exclude_none:
            result['ServerTime'] = self.server_time
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DataServer:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            server_version=data.get('ServerVersion'),
            is_connected=data.get('IsConnected'),
            server_time=data.get('ServerTime'),
        )


@dataclass
class Point(PIWebAPIObject):
    """PI Point object."""
    
    point_class: Optional[str] = None
    point_type: Optional[str] = None
    digital_set_name: Optional[str] = None
    engineering_units: Optional[str] = None
    step: Optional[bool] = None
    future: Optional[bool] = None
    display_digits: Optional[int] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.point_class is not None or not exclude_none:
            result['PointClass'] = self.point_class
        if self.point_type is not None or not exclude_none:
            result['PointType'] = self.point_type
        if self.digital_set_name is not None or not exclude_none:
            result['DigitalSetName'] = self.digital_set_name
        if self.engineering_units is not None or not exclude_none:
            result['EngineeringUnits'] = self.engineering_units
        if self.step is not None or not exclude_none:
            result['Step'] = self.step
        if self.future is not None or not exclude_none:
            result['Future'] = self.future
        if self.display_digits is not None or not exclude_none:
            result['DisplayDigits'] = self.display_digits
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Point:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            point_class=data.get('PointClass'),
            point_type=data.get('PointType'),
            digital_set_name=data.get('DigitalSetName'),
            engineering_units=data.get('EngineeringUnits'),
            step=data.get('Step'),
            future=data.get('Future'),
            display_digits=data.get('DisplayDigits'),
        )


@dataclass
class TimedValue:
    """Timed value with timestamp and value."""
    
    timestamp: str
    value: Any
    units_abbreviation: Optional[str] = None
    good: Optional[bool] = None
    questionable: Optional[bool] = None
    substituted: Optional[bool] = None
    annotated: Optional[bool] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {
            'Timestamp': self.timestamp,
            'Value': self.value,
        }
        
        if self.units_abbreviation is not None or not exclude_none:
            result['UnitsAbbreviation'] = self.units_abbreviation
        if self.good is not None or not exclude_none:
            result['Good'] = self.good
        if self.questionable is not None or not exclude_none:
            result['Questionable'] = self.questionable
        if self.substituted is not None or not exclude_none:
            result['Substituted'] = self.substituted
        if self.annotated is not None or not exclude_none:
            result['Annotated'] = self.annotated
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimedValue:
        """Create from PI Web API response."""
        return cls(
            timestamp=data['Timestamp'],
            value=data['Value'],
            units_abbreviation=data.get('UnitsAbbreviation'),
            good=data.get('Good'),
            questionable=data.get('Questionable'),
            substituted=data.get('Substituted'),
            annotated=data.get('Annotated'),
        )


@dataclass
class StreamValue:
    """Stream value object."""

    value: Any
    timestamp: Union[str, datetime, None] = None
    units_abbreviation: Optional[str] = None
    good: Optional[bool] = None
    questionable: Optional[bool] = None
    substituted: Optional[bool] = None

    def _format_time(self, time_value: Union[str, datetime, None]) -> Optional[str]:
        """Convert time value to PI Web API compatible string format."""
        if time_value is None:
            return None
        if isinstance(time_value, str):
            return time_value
        if isinstance(time_value, datetime):
            time_str = time_value.isoformat()
            # Convert +00:00 to Z for better PI Web API compatibility
            if time_str.endswith('+00:00'):
                time_str = time_str[:-6] + 'Z'
            return time_str
        raise TypeError(f"Time value must be str, datetime, or None, got {type(time_value)}")

    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {'Value': self.value}

        if self.timestamp is not None or not exclude_none:
            result['Timestamp'] = self._format_time(self.timestamp)
        if self.units_abbreviation is not None or not exclude_none:
            result['UnitsAbbreviation'] = self.units_abbreviation
        if self.good is not None or not exclude_none:
            result['Good'] = self.good
        if self.questionable is not None or not exclude_none:
            result['Questionable'] = self.questionable
        if self.substituted is not None or not exclude_none:
            result['Substituted'] = self.substituted

        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StreamValue:
        """Create from PI Web API response."""
        return cls(
            value=data['Value'],
            timestamp=data.get('Timestamp'),
            units_abbreviation=data.get('UnitsAbbreviation'),
            good=data.get('Good'),
            questionable=data.get('Questionable'),
            substituted=data.get('Substituted'),
        )


@dataclass
class StreamValues:
    """Collection of stream values."""
    
    web_id: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    items: Optional[list[TimedValue]] = None
    units_abbreviation: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {}
        
        if self.web_id is not None or not exclude_none:
            result['WebId'] = self.web_id
        if self.name is not None or not exclude_none:
            result['Name'] = self.name
        if self.path is not None or not exclude_none:
            result['Path'] = self.path
        if self.items is not None or not exclude_none:
            result['Items'] = [item.to_dict(exclude_none) for item in self.items] if self.items else []
        if self.units_abbreviation is not None or not exclude_none:
            result['UnitsAbbreviation'] = self.units_abbreviation
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StreamValues:
        """Create from PI Web API response."""
        items = None
        if 'Items' in data:
            items = [TimedValue.from_dict(item) for item in data['Items']]
            
        return cls(
            web_id=data.get('WebId'),
            name=data.get('Name'),
            path=data.get('Path'),
            items=items,
            units_abbreviation=data.get('UnitsAbbreviation'),
        )
