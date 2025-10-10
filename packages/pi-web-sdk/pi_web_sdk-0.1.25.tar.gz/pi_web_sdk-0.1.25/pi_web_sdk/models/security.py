"""Data models for security-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .base import PIWebAPIObject


__all__ = [
    "SecurityIdentity",
    "SecurityMapping",
    "SecurityEntry",
]


@dataclass
class SecurityIdentity(PIWebAPIObject):
    """PI AF Security Identity object."""
    
    is_enabled: Optional[bool] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.is_enabled is not None or not exclude_none:
            result['IsEnabled'] = self.is_enabled
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SecurityIdentity:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            is_enabled=data.get('IsEnabled'),
        )


@dataclass
class SecurityMapping(PIWebAPIObject):
    """PI AF Security Mapping object."""
    
    account: Optional[str] = None
    security_identity_web_id: Optional[str] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = super().to_dict(exclude_none)
        
        if self.account is not None or not exclude_none:
            result['Account'] = self.account
        if self.security_identity_web_id is not None or not exclude_none:
            result['SecurityIdentityWebId'] = self.security_identity_web_id
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SecurityMapping:
        """Create from PI Web API response."""
        base = PIWebAPIObject.from_dict(data)
        return cls(
            web_id=base.web_id,
            id=base.id,
            name=base.name,
            description=base.description,
            path=base.path,
            links=base.links,
            account=data.get('Account'),
            security_identity_web_id=data.get('SecurityIdentityWebId'),
        )


@dataclass
class SecurityEntry:
    """Security Entry object."""
    
    name: str
    security_identity_name: str
    allow_rights: Optional[List[str]] = None
    deny_rights: Optional[List[str]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {
            'Name': self.name,
            'SecurityIdentityName': self.security_identity_name,
        }
        
        if self.allow_rights is not None or not exclude_none:
            result['AllowRights'] = self.allow_rights
        if self.deny_rights is not None or not exclude_none:
            result['DenyRights'] = self.deny_rights
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SecurityEntry:
        """Create from PI Web API response."""
        return cls(
            name=data['Name'],
            security_identity_name=data['SecurityIdentityName'],
            allow_rights=data.get('AllowRights'),
            deny_rights=data.get('DenyRights'),
        )
