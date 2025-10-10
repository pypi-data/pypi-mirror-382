"""Data models for table-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import PIWebAPIObject


__all__ = [
    "Table",
    "TableCategory",
    "TableData",
]


@dataclass
class Table(PIWebAPIObject):
    """PI AF Table object."""
    
    category_names: Optional[list[str]] = None
    converted_data_type: Optional[str] = None
    default_value: Optional[Any] = None
    time_zone: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.converted_data_type is not None or not exclude_none:
            result['ConvertedDataType'] = self.converted_data_type
        if self.default_value is not None or not exclude_none:
            result['DefaultValue'] = self.default_value
        if self.time_zone is not None or not exclude_none:
            result['TimeZone'] = self.time_zone
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Table:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            category_names=data.get('CategoryNames'),
            converted_data_type=data.get('ConvertedDataType'),
            default_value=data.get('DefaultValue'),
            time_zone=data.get('TimeZone'),
        )


@dataclass
class TableCategory(PIWebAPIObject):
    """PI AF Table Category object."""
    
    security_descriptor: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.security_descriptor is not None or not exclude_none:
            result['SecurityDescriptor'] = self.security_descriptor
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TableCategory:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            security_descriptor=data.get('SecurityDescriptor'),
        )


@dataclass
class TableData:
    """Table data object."""
    
    columns: Optional[Dict[str, Any]] = None
    rows: Optional[list[Dict[str, Any]]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {}
        
        if self.columns is not None or not exclude_none:
            result['Columns'] = self.columns
        if self.rows is not None or not exclude_none:
            result['Rows'] = self.rows
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TableData:
        """Create from PI Web API response."""
        return cls(
            columns=data.get('Columns'),
            rows=data.get('Rows'),
        )
