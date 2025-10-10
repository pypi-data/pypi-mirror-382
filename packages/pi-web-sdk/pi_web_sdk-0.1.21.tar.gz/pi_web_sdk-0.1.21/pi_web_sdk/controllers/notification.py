"""Controllers for notification-related endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from .base import BaseController

__all__ = [
    'NotificationContactTemplateController',
    'NotificationPlugInController',
    'NotificationRuleController',
    'NotificationRuleSubscriberController',
    'NotificationRuleTemplateController',
]


class NotificationContactTemplateController(BaseController):
    """Controller for Notification Contact Template operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification contact template by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationcontacttemplates/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification contact template by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationcontacttemplates/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, template: Dict) -> Dict:
        """Update a notification contact template."""
        return self.client.patch(f"notificationcontacttemplates/{web_id}", data=template)

    def delete(self, web_id: str) -> Dict:
        """Delete a notification contact template."""
        return self.client.delete(f"notificationcontacttemplates/{web_id}")

    def create_security_entry(self, web_id: str, security_entry: Dict) -> Dict:
        """Create a security entry for the notification contact template."""
        return self.client.post(
            f"notificationcontacttemplates/{web_id}/securityentries", data=security_entry
        )

    def delete_security_entry(self, web_id: str, name: str) -> Dict:
        """Delete a security entry from the notification contact template."""
        return self.client.delete(
            f"notificationcontacttemplates/{web_id}/securityentries/{self._encode_path(name)}"
        )

    def get_notification_contact_templates(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get notification contact templates."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationcontacttemplates/{web_id}/notificationcontacttemplates", params=params
        )

    def get_notification_contact_templates_query(
        self,
        web_id: str,
        query: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Query notification contact templates."""
        params = {"q": query}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationcontacttemplates/{web_id}/notificationcontacttemplates/search",
            params=params
        )

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a notification contact template."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationcontacttemplates/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a notification contact template."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationcontacttemplates/{web_id}/securityentries", params=params
        )

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a notification contact template."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationcontacttemplates/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def update_security_entry(self, web_id: str, name: str, security_entry: Dict) -> Dict:
        """Update a security entry for the notification contact template."""
        return self.client.put(
            f"notificationcontacttemplates/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry
        )


class NotificationPlugInController(BaseController):
    """Controller for Notification PlugIn operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification plugin by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationplugins/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification plugin by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationplugins/path/{self._encode_path(path)}", params=params
        )


class NotificationRuleController(BaseController):
    """Controller for Notification Rule operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationrules/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrules/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, rule: Dict) -> Dict:
        """Update a notification rule."""
        return self.client.patch(f"notificationrules/{web_id}", data=rule)

    def delete(self, web_id: str) -> Dict:
        """Delete a notification rule."""
        return self.client.delete(f"notificationrules/{web_id}")

    def create_notification_rule_subscriber(self, web_id: str, subscriber: Dict) -> Dict:
        """Create a notification rule subscriber."""
        return self.client.post(
            f"notificationrules/{web_id}/notificationrulesubscribers", data=subscriber
        )

    def create_security_entry(self, web_id: str, security_entry: Dict) -> Dict:
        """Create a security entry for the notification rule."""
        return self.client.post(
            f"notificationrules/{web_id}/securityentries", data=security_entry
        )

    def delete_security_entry(self, web_id: str, name: str) -> Dict:
        """Delete a security entry from the notification rule."""
        return self.client.delete(
            f"notificationrules/{web_id}/securityentries/{self._encode_path(name)}"
        )

    def get_notification_rules_query(
        self,
        web_id: str,
        query: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Query notification rules."""
        params = {"q": query}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrules/{web_id}/notificationrules/search", params=params
        )

    def get_notification_rule_subscribers(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get notification rule subscribers."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrules/{web_id}/notificationrulesubscribers", params=params
        )

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a notification rule."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationrules/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a notification rule."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationrules/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a notification rule."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrules/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def update_security_entry(self, web_id: str, name: str, security_entry: Dict) -> Dict:
        """Update a security entry for the notification rule."""
        return self.client.put(
            f"notificationrules/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry
        )


class NotificationRuleSubscriberController(BaseController):
    """Controller for Notification Rule Subscriber operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule subscriber by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationrulesubscribers/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule subscriber by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrulesubscribers/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, subscriber: Dict) -> Dict:
        """Update a notification rule subscriber."""
        return self.client.patch(f"notificationrulesubscribers/{web_id}", data=subscriber)

    def delete(self, web_id: str) -> Dict:
        """Delete a notification rule subscriber."""
        return self.client.delete(f"notificationrulesubscribers/{web_id}")

    def get_notification_rule_subscribers(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get notification rule subscribers."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationrulesubscribers/{web_id}/notificationrulesubscribers", params=params
        )


class NotificationRuleTemplateController(BaseController):
    """Controller for Notification Rule Template operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule template by WebID."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationruletemplates/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get notification rule template by path."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationruletemplates/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, template: Dict) -> Dict:
        """Update a notification rule template."""
        return self.client.patch(f"notificationruletemplates/{web_id}", data=template)

    def delete(self, web_id: str) -> Dict:
        """Delete a notification rule template."""
        return self.client.delete(f"notificationruletemplates/{web_id}")

    def create_notification_rule_template_subscriber(self, web_id: str, subscriber: Dict) -> Dict:
        """Create a notification rule template subscriber."""
        return self.client.post(
            f"notificationruletemplates/{web_id}/notificationruletemplatesubscribers",
            data=subscriber
        )

    def create_security_entry(self, web_id: str, security_entry: Dict) -> Dict:
        """Create a security entry for the notification rule template."""
        return self.client.post(
            f"notificationruletemplates/{web_id}/securityentries", data=security_entry
        )

    def delete_security_entry(self, web_id: str, name: str) -> Dict:
        """Delete a security entry from the notification rule template."""
        return self.client.delete(
            f"notificationruletemplates/{web_id}/securityentries/{self._encode_path(name)}"
        )

    def get_notification_rule_templates_query(
        self,
        web_id: str,
        query: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Query notification rule templates."""
        params = {"q": query}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationruletemplates/{web_id}/notificationruletemplates/search",
            params=params
        )

    def get_notification_rule_template_subscribers(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get notification rule template subscribers."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationruletemplates/{web_id}/notificationruletemplatesubscribers",
            params=params
        )

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for a notification rule template."""
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"notificationruletemplates/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for a notification rule template."""
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationruletemplates/{web_id}/securityentries", params=params
        )

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for a notification rule template."""
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"notificationruletemplates/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def update_security_entry(self, web_id: str, name: str, security_entry: Dict) -> Dict:
        """Update a security entry for the notification rule template."""
        return self.client.put(
            f"notificationruletemplates/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry
        )