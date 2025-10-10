"""Data models for enumeration-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject


__all__ = [
    "EnumerationSet",
    "EnumerationValue",
]


@dataclass
class EnumerationSet(PIWebAPIObject):
    """PI AF Enumeration Set object."""
    
    serializable: Optional[bool] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.serializable is not None or not exclude_none:
            result['Serializable'] = self.serializable
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EnumerationSet:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            serializable=data.get('Serializable'),
        )


@dataclass
class EnumerationValue(PIWebAPIObject):
    """PI AF Enumeration Value object."""
    
    value: Optional[int] = None
    parent: Optional[str] = None
    serializable: Optional[bool] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.value is not None or not exclude_none:
            result['Value'] = self.value
        if self.parent is not None or not exclude_none:
            result['Parent'] = self.parent
        if self.serializable is not None or not exclude_none:
            result['Serializable'] = self.serializable
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EnumerationValue:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            value=data.get('Value'),
            parent=data.get('Parent'),
            serializable=data.get('Serializable'),
        )
