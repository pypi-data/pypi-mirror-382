"""Data models for time rule-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import PIWebAPIObject


__all__ = [
    "TimeRule",
    "TimeRulePlugIn",
]


@dataclass
class TimeRule(PIWebAPIObject):
    """PI AF Time Rule object."""
    
    configuration_string: Optional[str] = None
    display_string: Optional[str] = None
    editor_type: Optional[str] = None
    is_configurable: Optional[bool] = None
    is_initializing: Optional[bool] = None
    merge_duplicate_events: Optional[bool] = None
    plugin_version: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.configuration_string is not None or not exclude_none:
            result['ConfigString'] = self.configuration_string
        if self.display_string is not None or not exclude_none:
            result['DisplayString'] = self.display_string
        if self.editor_type is not None or not exclude_none:
            result['EditorType'] = self.editor_type
        if self.is_configurable is not None or not exclude_none:
            result['IsConfigurable'] = self.is_configurable
        if self.is_initializing is not None or not exclude_none:
            result['IsInitializing'] = self.is_initializing
        if self.merge_duplicate_events is not None or not exclude_none:
            result['MergeDuplicateEvents'] = self.merge_duplicate_events
        if self.plugin_version is not None or not exclude_none:
            result['PlugInVersion'] = self.plugin_version
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimeRule:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            configuration_string=data.get('ConfigString'),
            display_string=data.get('DisplayString'),
            editor_type=data.get('EditorType'),
            is_configurable=data.get('IsConfigurable'),
            is_initializing=data.get('IsInitializing'),
            merge_duplicate_events=data.get('MergeDuplicateEvents'),
            plugin_version=data.get('PlugInVersion'),
        )


@dataclass
class TimeRulePlugIn(PIWebAPIObject):
    """PI AF Time Rule Plugin object."""
    
    assembly_file_name: Optional[str] = None
    assembly_id: Optional[str] = None
    assembly_load_properties: Optional[list[str]] = None
    assembly_time: Optional[str] = None
    compatibility_version: Optional[int] = None
    is_browsable: Optional[bool] = None
    is_enabled: Optional[bool] = None
    load_exception: Optional[str] = None
    plugin_version: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.assembly_file_name is not None or not exclude_none:
            result['AssemblyFileName'] = self.assembly_file_name
        if self.assembly_id is not None or not exclude_none:
            result['AssemblyID'] = self.assembly_id
        if self.assembly_load_properties is not None or not exclude_none:
            result['AssemblyLoadProperties'] = self.assembly_load_properties
        if self.assembly_time is not None or not exclude_none:
            result['AssemblyTime'] = self.assembly_time
        if self.compatibility_version is not None or not exclude_none:
            result['CompatibilityVersion'] = self.compatibility_version
        if self.is_browsable is not None or not exclude_none:
            result['IsBrowsable'] = self.is_browsable
        if self.is_enabled is not None or not exclude_none:
            result['IsEnabled'] = self.is_enabled
        if self.load_exception is not None or not exclude_none:
            result['LoadException'] = self.load_exception
        if self.plugin_version is not None or not exclude_none:
            result['PlugInVersion'] = self.plugin_version
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimeRulePlugIn:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            assembly_file_name=data.get('AssemblyFileName'),
            assembly_id=data.get('AssemblyID'),
            assembly_load_properties=data.get('AssemblyLoadProperties'),
            assembly_time=data.get('AssemblyTime'),
            compatibility_version=data.get('CompatibilityVersion'),
            is_browsable=data.get('IsBrowsable'),
            is_enabled=data.get('IsEnabled'),
            load_exception=data.get('LoadException'),
            plugin_version=data.get('PlugInVersion'),
        )
