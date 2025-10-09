"""Data models for analysis-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject


__all__ = [
    "Analysis",
    "AnalysisTemplate",
    "AnalysisCategory",
    "AnalysisRule",
]


@dataclass
class Analysis(PIWebAPIObject):
    """PI AF Analysis object."""
    
    analysis_rule_plugin_name: Optional[str] = None
    auto_created: Optional[bool] = None
    category_names: Optional[List[str]] = None
    group_id: Optional[int] = None
    has_notification_template: Optional[bool] = None
    has_target: Optional[bool] = None
    has_template: Optional[bool] = None
    is_configured: Optional[bool] = None
    is_time_rule_defined_by_template: Optional[bool] = None
    maximum_queue_size: Optional[int] = None
    output_time: Optional[str] = None
    priority: Optional[str] = None
    publish_results: Optional[bool] = None
    status: Optional[str] = None
    target_web_id: Optional[str] = None
    template_name: Optional[str] = None
    time_rule_plugin_name: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.analysis_rule_plugin_name is not None or not exclude_none:
            result['AnalysisRulePlugInName'] = self.analysis_rule_plugin_name
        if self.auto_created is not None or not exclude_none:
            result['AutoCreated'] = self.auto_created
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.group_id is not None or not exclude_none:
            result['GroupId'] = self.group_id
        if self.has_notification_template is not None or not exclude_none:
            result['HasNotificationTemplate'] = self.has_notification_template
        if self.has_target is not None or not exclude_none:
            result['HasTarget'] = self.has_target
        if self.has_template is not None or not exclude_none:
            result['HasTemplate'] = self.has_template
        if self.is_configured is not None or not exclude_none:
            result['IsConfigured'] = self.is_configured
        if self.is_time_rule_defined_by_template is not None or not exclude_none:
            result['IsTimeRuleDefinedByTemplate'] = self.is_time_rule_defined_by_template
        if self.maximum_queue_size is not None or not exclude_none:
            result['MaximumQueueSize'] = self.maximum_queue_size
        if self.output_time is not None or not exclude_none:
            result['OutputTime'] = self.output_time
        if self.priority is not None or not exclude_none:
            result['Priority'] = self.priority
        if self.publish_results is not None or not exclude_none:
            result['PublishResults'] = self.publish_results
        if self.status is not None or not exclude_none:
            result['Status'] = self.status
        if self.target_web_id is not None or not exclude_none:
            result['TargetWebId'] = self.target_web_id
        if self.template_name is not None or not exclude_none:
            result['TemplateName'] = self.template_name
        if self.time_rule_plugin_name is not None or not exclude_none:
            result['TimeRulePlugInName'] = self.time_rule_plugin_name
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Analysis:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            analysis_rule_plugin_name=data.get('AnalysisRulePlugInName'),
            auto_created=data.get('AutoCreated'),
            category_names=data.get('CategoryNames'),
            group_id=data.get('GroupId'),
            has_notification_template=data.get('HasNotificationTemplate'),
            has_target=data.get('HasTarget'),
            has_template=data.get('HasTemplate'),
            is_configured=data.get('IsConfigured'),
            is_time_rule_defined_by_template=data.get('IsTimeRuleDefinedByTemplate'),
            maximum_queue_size=data.get('MaximumQueueSize'),
            output_time=data.get('OutputTime'),
            priority=data.get('Priority'),
            publish_results=data.get('PublishResults'),
            status=data.get('Status'),
            target_web_id=data.get('TargetWebId'),
            template_name=data.get('TemplateName'),
            time_rule_plugin_name=data.get('TimeRulePlugInName'),
        )


@dataclass
class AnalysisTemplate(PIWebAPIObject):
    """PI AF Analysis Template object."""
    
    analysis_rule_plugin_name: Optional[str] = None
    category_names: Optional[List[str]] = None
    create_enabled: Optional[bool] = None
    group_id: Optional[int] = None
    has_notification_template: Optional[bool] = None
    output_time: Optional[str] = None
    target_name: Optional[str] = None
    time_rule_plugin_name: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.analysis_rule_plugin_name is not None or not exclude_none:
            result['AnalysisRulePlugInName'] = self.analysis_rule_plugin_name
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.create_enabled is not None or not exclude_none:
            result['CreateEnabled'] = self.create_enabled
        if self.group_id is not None or not exclude_none:
            result['GroupId'] = self.group_id
        if self.has_notification_template is not None or not exclude_none:
            result['HasNotificationTemplate'] = self.has_notification_template
        if self.output_time is not None or not exclude_none:
            result['OutputTime'] = self.output_time
        if self.target_name is not None or not exclude_none:
            result['TargetName'] = self.target_name
        if self.time_rule_plugin_name is not None or not exclude_none:
            result['TimeRulePlugInName'] = self.time_rule_plugin_name
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AnalysisTemplate:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            analysis_rule_plugin_name=data.get('AnalysisRulePlugInName'),
            category_names=data.get('CategoryNames'),
            create_enabled=data.get('CreateEnabled'),
            group_id=data.get('GroupId'),
            has_notification_template=data.get('HasNotificationTemplate'),
            output_time=data.get('OutputTime'),
            target_name=data.get('TargetName'),
            time_rule_plugin_name=data.get('TimeRulePlugInName'),
        )


@dataclass
class AnalysisCategory(PIWebAPIObject):
    """PI AF Analysis Category object."""
    
    security_descriptor: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.security_descriptor is not None or not exclude_none:
            result['SecurityDescriptor'] = self.security_descriptor
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AnalysisCategory:
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
class AnalysisRule(PIWebAPIObject):
    """PI AF Analysis Rule object."""
    
    configuration_string: Optional[str] = None
    display_string: Optional[str] = None
    editor_type: Optional[str] = None
    has_children: Optional[bool] = None
    is_configurable: Optional[bool] = None
    is_initializing: Optional[bool] = None
    plugin_version: Optional[str] = None
    supported_behaviors: Optional[List[str]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.configuration_string is not None or not exclude_none:
            result['ConfigString'] = self.configuration_string
        if self.display_string is not None or not exclude_none:
            result['DisplayString'] = self.display_string
        if self.editor_type is not None or not exclude_none:
            result['EditorType'] = self.editor_type
        if self.has_children is not None or not exclude_none:
            result['HasChildren'] = self.has_children
        if self.is_configurable is not None or not exclude_none:
            result['IsConfigurable'] = self.is_configurable
        if self.is_initializing is not None or not exclude_none:
            result['IsInitializing'] = self.is_initializing
        if self.plugin_version is not None or not exclude_none:
            result['PlugInVersion'] = self.plugin_version
        if self.supported_behaviors is not None or not exclude_none:
            result['SupportedBehaviors'] = self.supported_behaviors
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AnalysisRule:
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
            has_children=data.get('HasChildren'),
            is_configurable=data.get('IsConfigurable'),
            is_initializing=data.get('IsInitializing'),
            plugin_version=data.get('PlugInVersion'),
            supported_behaviors=data.get('SupportedBehaviors'),
        )
