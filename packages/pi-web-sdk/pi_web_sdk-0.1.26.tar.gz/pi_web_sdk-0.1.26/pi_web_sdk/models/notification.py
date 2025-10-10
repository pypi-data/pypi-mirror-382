"""Data models for notification-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject


__all__ = [
    "NotificationRule",
    "NotificationContactTemplate",
]


@dataclass
class NotificationRule(PIWebAPIObject):
    """PI AF Notification Rule object."""
    
    category_names: Optional[List[str]] = None
    criteria: Optional[str] = None
    multi_trigger_event_option: Optional[str] = None
    nonrepetition_interval: Optional[str] = None
    resend_interval: Optional[str] = None
    status: Optional[str] = None
    template_name: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.category_names is not None or not exclude_none:
            result['CategoryNames'] = self.category_names
        if self.criteria is not None or not exclude_none:
            result['Criteria'] = self.criteria
        if self.multi_trigger_event_option is not None or not exclude_none:
            result['MultiTriggerEventOption'] = self.multi_trigger_event_option
        if self.nonrepetition_interval is not None or not exclude_none:
            result['NonrepetitionInterval'] = self.nonrepetition_interval
        if self.resend_interval is not None or not exclude_none:
            result['ResendInterval'] = self.resend_interval
        if self.status is not None or not exclude_none:
            result['Status'] = self.status
        if self.template_name is not None or not exclude_none:
            result['TemplateName'] = self.template_name
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NotificationRule:
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
            criteria=data.get('Criteria'),
            multi_trigger_event_option=data.get('MultiTriggerEventOption'),
            nonrepetition_interval=data.get('NonrepetitionInterval'),
            resend_interval=data.get('ResendInterval'),
            status=data.get('Status'),
            template_name=data.get('TemplateName'),
        )


@dataclass
class NotificationContactTemplate(PIWebAPIObject):
    """PI AF Notification Contact Template object."""
    
    available_notification_formats: Optional[List[str]] = None
    configuration_display_name: Optional[str] = None
    contact_template_type_name: Optional[str] = None
    delivery_format_name: Optional[str] = None
    escalation_timeout: Optional[str] = None
    has_children: Optional[bool] = None
    maximum_retries: Optional[int] = None
    minimum_acknowledgements: Optional[int] = None
    notify_option: Optional[str] = None
    notify_when_instance_ended: Optional[bool] = None
    plugin_version: Optional[str] = None
    retry_interval: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.available_notification_formats is not None or not exclude_none:
            result['AvailableNotificationFormats'] = self.available_notification_formats
        if self.configuration_display_name is not None or not exclude_none:
            result['ConfigurationDisplayName'] = self.configuration_display_name
        if self.contact_template_type_name is not None or not exclude_none:
            result['ContactTemplateTypeName'] = self.contact_template_type_name
        if self.delivery_format_name is not None or not exclude_none:
            result['DeliveryFormatName'] = self.delivery_format_name
        if self.escalation_timeout is not None or not exclude_none:
            result['EscalationTimeout'] = self.escalation_timeout
        if self.has_children is not None or not exclude_none:
            result['HasChildren'] = self.has_children
        if self.maximum_retries is not None or not exclude_none:
            result['MaximumRetries'] = self.maximum_retries
        if self.minimum_acknowledgements is not None or not exclude_none:
            result['MinimumAcknowledgements'] = self.minimum_acknowledgements
        if self.notify_option is not None or not exclude_none:
            result['NotifyOption'] = self.notify_option
        if self.notify_when_instance_ended is not None or not exclude_none:
            result['NotifyWhenInstanceEnded'] = self.notify_when_instance_ended
        if self.plugin_version is not None or not exclude_none:
            result['PlugInVersion'] = self.plugin_version
        if self.retry_interval is not None or not exclude_none:
            result['RetryInterval'] = self.retry_interval
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NotificationContactTemplate:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            available_notification_formats=data.get('AvailableNotificationFormats'),
            configuration_display_name=data.get('ConfigurationDisplayName'),
            contact_template_type_name=data.get('ContactTemplateTypeName'),
            delivery_format_name=data.get('DeliveryFormatName'),
            escalation_timeout=data.get('EscalationTimeout'),
            has_children=data.get('HasChildren'),
            maximum_retries=data.get('MaximumRetries'),
            minimum_acknowledgements=data.get('MinimumAcknowledgements'),
            notify_option=data.get('NotifyOption'),
            notify_when_instance_ended=data.get('NotifyWhenInstanceEnded'),
            plugin_version=data.get('PlugInVersion'),
            retry_interval=data.get('RetryInterval'),
        )
