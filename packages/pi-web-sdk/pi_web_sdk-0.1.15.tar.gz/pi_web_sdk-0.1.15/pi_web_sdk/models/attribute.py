"""Data models for attribute-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject


__all__ = [
    "Attribute",
    "AttributeCategory",
    "AttributeTemplate",
    "AttributeTrait",
]


@dataclass
class Attribute(PIWebAPIObject):
    """PI AF Attribute object."""
    
    type: Optional[str] = None
    type_qualifier: Optional[str] = None
    default_units_name: Optional[str] = None
    data_reference_plugin_name: Optional[str] = None
    config_string: Optional[str] = None
    is_configuration_item: Optional[bool] = None
    is_excluded: Optional[bool] = None
    is_hidden: Optional[bool] = None
    is_manual_data_entry: Optional[bool] = None
    has_children: Optional[bool] = None
    category_names: Optional[List[str]] = None
    step: Optional[bool] = None
    trait_name: Optional[str] = None
    default_value: Optional[Any] = None
    display_digits: Optional[int] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.type is not None or not exclude_none:
            result['Type'] = self.type
        if self.type_qualifier is not None or not exclude_none:
            result['TypeQualifier'] = self.type_qualifier
        if self.default_units_name is not None or not exclude_none:
            result['DefaultUnitsName'] = self.default_units_name
        if self.data_reference_plugin_name is not None or not exclude_none:
            result['DataReferencePlugIn'] = self.data_reference_plugin_name
        if self.config_string is not None or not exclude_none:
            result['ConfigString'] = self.config_string
        if self.is_configuration_item is not None or not exclude_none:
            result['IsConfigurationItem'] = self.is_configuration_item
        if self.is_excluded is not None or not exclude_none:
            result['IsExcluded'] = self.is_excluded
        if self.is_hidden is not None or not exclude_none:
            result['IsHidden'] = self.is_hidden
        if self.is_manual_data_entry is not None or not exclude_none:
            result['IsManualDataEntry'] = self.is_manual_data_entry
        if self.has_children is not None or not exclude_none:
            result['HasChildren'] = self.has_children
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.step is not None or not exclude_none:
            result['Step'] = self.step
        if self.trait_name is not None or not exclude_none:
            result['TraitName'] = self.trait_name
        if self.default_value is not None or not exclude_none:
            result['DefaultValue'] = self.default_value
        if self.display_digits is not None or not exclude_none:
            result['DisplayDigits'] = self.display_digits
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Attribute:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            type=data.get('Type'),
            type_qualifier=data.get('TypeQualifier'),
            default_units_name=data.get('DefaultUnitsName'),
            data_reference_plugin_name=data.get('DataReferencePlugIn'),
            config_string=data.get('ConfigString'),
            is_configuration_item=data.get('IsConfigurationItem'),
            is_excluded=data.get('IsExcluded'),
            is_hidden=data.get('IsHidden'),
            is_manual_data_entry=data.get('IsManualDataEntry'),
            has_children=data.get('HasChildren'),
            category_names=data.get('CategoryNames'),
            step=data.get('Step'),
            trait_name=data.get('TraitName'),
            default_value=data.get('DefaultValue'),
            display_digits=data.get('DisplayDigits'),
        )


@dataclass
class AttributeCategory(PIWebAPIObject):
    """PI AF Attribute Category object."""
    
    security_descriptor: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.security_descriptor is not None or not exclude_none:
            result['SecurityDescriptor'] = self.security_descriptor
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AttributeCategory:
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
class AttributeTemplate(PIWebAPIObject):
    """PI AF Attribute Template object."""
    
    type: Optional[str] = None
    type_qualifier: Optional[str] = None
    default_units_name: Optional[str] = None
    data_reference_plugin_name: Optional[str] = None
    config_string: Optional[str] = None
    is_configuration_item: Optional[bool] = None
    is_excluded: Optional[bool] = None
    is_hidden: Optional[bool] = None
    is_manual_data_entry: Optional[bool] = None
    has_children: Optional[bool] = None
    category_names: Optional[List[str]] = None
    trait_name: Optional[str] = None
    default_value: Optional[Any] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.type is not None or not exclude_none:
            result['Type'] = self.type
        if self.type_qualifier is not None or not exclude_none:
            result['TypeQualifier'] = self.type_qualifier
        if self.default_units_name is not None or not exclude_none:
            result['DefaultUnitsName'] = self.default_units_name
        if self.data_reference_plugin_name is not None or not exclude_none:
            result['DataReferencePlugIn'] = self.data_reference_plugin_name
        if self.config_string is not None or not exclude_none:
            result['ConfigString'] = self.config_string
        if self.is_configuration_item is not None or not exclude_none:
            result['IsConfigurationItem'] = self.is_configuration_item
        if self.is_excluded is not None or not exclude_none:
            result['IsExcluded'] = self.is_excluded
        if self.is_hidden is not None or not exclude_none:
            result['IsHidden'] = self.is_hidden
        if self.is_manual_data_entry is not None or not exclude_none:
            result['IsManualDataEntry'] = self.is_manual_data_entry
        if self.has_children is not None or not exclude_none:
            result['HasChildren'] = self.has_children
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.trait_name is not None or not exclude_none:
            result['TraitName'] = self.trait_name
        if self.default_value is not None or not exclude_none:
            result['DefaultValue'] = self.default_value
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AttributeTemplate:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            type=data.get('Type'),
            type_qualifier=data.get('TypeQualifier'),
            default_units_name=data.get('DefaultUnitsName'),
            data_reference_plugin_name=data.get('DataReferencePlugIn'),
            config_string=data.get('ConfigString'),
            is_configuration_item=data.get('IsConfigurationItem'),
            is_excluded=data.get('IsExcluded'),
            is_hidden=data.get('IsHidden'),
            is_manual_data_entry=data.get('IsManualDataEntry'),
            has_children=data.get('HasChildren'),
            category_names=data.get('CategoryNames'),
            trait_name=data.get('TraitName'),
            default_value=data.get('DefaultValue'),
        )


@dataclass
class AttributeTrait(PIWebAPIObject):
    """PI AF Attribute Trait object."""
    
    abbreviation: Optional[str] = None
    allow_child_attributes: Optional[bool] = None
    allow_data_reference: Optional[bool] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.abbreviation is not None or not exclude_none:
            result['Abbreviation'] = self.abbreviation
        if self.allow_child_attributes is not None or not exclude_none:
            result['AllowChildAttributes'] = self.allow_child_attributes
        if self.allow_data_reference is not None or not exclude_none:
            result['AllowDataReference'] = self.allow_data_reference
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AttributeTrait:
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
            allow_child_attributes=data.get('AllowChildAttributes'),
            allow_data_reference=data.get('AllowDataReference'),
        )
