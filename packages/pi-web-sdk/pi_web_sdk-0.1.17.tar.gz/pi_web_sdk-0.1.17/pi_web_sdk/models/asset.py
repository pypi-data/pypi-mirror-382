"""Data models for asset-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject, to_pi_web_api_dict


__all__ = [
    "AssetServer",
    "AssetDatabase",
    "Element",
    "ElementCategory",
    "ElementTemplate",
]


@dataclass
class AssetServer(PIWebAPIObject):
    """PI AF Asset Server object."""
    
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
    def from_dict(cls, data: Dict[str, Any]) -> AssetServer:
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
class AssetDatabase(PIWebAPIObject):
    """PI AF Asset Database object."""
    
    extended_properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.extended_properties is not None or not exclude_none:
            result['ExtendedProperties'] = self.extended_properties
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetDatabase:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            extended_properties=data.get('ExtendedProperties'),
        )


@dataclass
class Element(PIWebAPIObject):
    """PI AF Element object."""
    
    template_name: Optional[str] = None
    has_children: Optional[bool] = None
    category_names: Optional[List[str]] = None
    extended_properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.template_name is not None or not exclude_none:
            result['TemplateName'] = self.template_name
        if self.has_children is not None or not exclude_none:
            result['HasChildren'] = self.has_children
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.extended_properties is not None or not exclude_none:
            result['ExtendedProperties'] = self.extended_properties
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Element:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            template_name=data.get('TemplateName'),
            has_children=data.get('HasChildren'),
            category_names=data.get('CategoryNames'),
            extended_properties=data.get('ExtendedProperties'),
        )


@dataclass
class ElementCategory(PIWebAPIObject):
    """PI AF Element Category object."""
    
    security_descriptor: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.security_descriptor is not None or not exclude_none:
            result['SecurityDescriptor'] = self.security_descriptor
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ElementCategory:
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
class ElementTemplate(PIWebAPIObject):
    """PI AF Element Template object."""
    
    allow_element_to_extend: Optional[bool] = None
    base_template: Optional[str] = None
    category_names: Optional[List[str]] = None
    instance_type: Optional[str] = None
    naming_pattern: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.allow_element_to_extend is not None or not exclude_none:
            result['AllowElementToExtend'] = self.allow_element_to_extend
        if self.base_template is not None or not exclude_none:
            result['BaseTemplate'] = self.base_template
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.instance_type is not None or not exclude_none:
            result['InstanceType'] = self.instance_type
        if self.naming_pattern is not None or not exclude_none:
            result['NamingPattern'] = self.naming_pattern
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ElementTemplate:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            allow_element_to_extend=data.get('AllowElementToExtend'),
            base_template=data.get('BaseTemplate'),
            category_names=data.get('CategoryNames'),
            instance_type=data.get('InstanceType'),
            naming_pattern=data.get('NamingPattern'),
        )
