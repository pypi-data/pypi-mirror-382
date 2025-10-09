"""Data models for stream-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import PIWebAPIObject


__all__ = [
    "Stream",
    "StreamSet",
]


@dataclass
class Stream(PIWebAPIObject):
    """PI Stream object."""
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        return super().to_dict(exclude_none)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Stream:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
        )


@dataclass
class StreamSet(PIWebAPIObject):
    """PI Stream Set object."""
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        return super().to_dict(exclude_none)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StreamSet:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
        )
