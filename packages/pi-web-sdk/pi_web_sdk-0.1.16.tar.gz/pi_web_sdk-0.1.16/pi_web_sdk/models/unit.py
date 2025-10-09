"""Data models for unit-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import PIWebAPIObject


__all__ = [
    "Unit",
    "UnitClass",
]


@dataclass
class Unit(PIWebAPIObject):
    """PI AF Unit of Measure object."""
    
    abbreviation: Optional[str] = None
    factor: Optional[float] = None
    offset: Optional[float] = None
    reference_factor: Optional[float] = None
    reference_offset: Optional[float] = None
    reference_unit_abbreviation: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.abbreviation is not None or not exclude_none:
            result['Abbreviation'] = self.abbreviation
        if self.factor is not None or not exclude_none:
            result['Factor'] = self.factor
        if self.offset is not None or not exclude_none:
            result['Offset'] = self.offset
        if self.reference_factor is not None or not exclude_none:
            result['ReferenceFactor'] = self.reference_factor
        if self.reference_offset is not None or not exclude_none:
            result['ReferenceOffset'] = self.reference_offset
        if self.reference_unit_abbreviation is not None or not exclude_none:
            result['ReferenceUnitAbbreviation'] = self.reference_unit_abbreviation
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Unit:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            abbreviation=data.get('Abbreviation'),
            factor=data.get('Factor'),
            offset=data.get('Offset'),
            reference_factor=data.get('ReferenceFactor'),
            reference_offset=data.get('ReferenceOffset'),
            reference_unit_abbreviation=data.get('ReferenceUnitAbbreviation'),
        )


@dataclass
class UnitClass(PIWebAPIObject):
    """PI AF Unit Class object."""
    
    canonical_unit_name: Optional[str] = None
    canonical_unit_abbreviation: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.canonical_unit_name is not None or not exclude_none:
            result['CanonicalUnitName'] = self.canonical_unit_name
        if self.canonical_unit_abbreviation is not None or not exclude_none:
            result['CanonicalUnitAbbreviation'] = self.canonical_unit_abbreviation
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UnitClass:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            canonical_unit_name=data.get('CanonicalUnitName'),
            canonical_unit_abbreviation=data.get('CanonicalUnitAbbreviation'),
        )
