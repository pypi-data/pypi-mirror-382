"""Base data models for PI Web API."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class PIWebAPIObject:
    """Base class for all PI Web API objects."""
    
    web_id: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None
    links: Optional[Dict[str, str]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format expected by PI Web API.
        
        Args:
            exclude_none: If True, exclude None values from output
        """
        result = {}
        
        # Map Python field names to PI Web API field names
        field_mapping = {
            'web_id': 'WebId',
            'id': 'Id',
            'name': 'Name',
            'description': 'Description',
            'path': 'Path',
            'links': 'Links',
        }
        
        for python_name, api_name in field_mapping.items():
            value = getattr(self, python_name, None)
            if value is not None or not exclude_none:
                result[api_name] = value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PIWebAPIObject:
        """Create instance from PI Web API response data."""
        return cls(
            web_id=data.get('WebId'),
            id=data.get('Id'),
            name=data.get('Name'),
            description=data.get('Description'),
            path=data.get('Path'),
            links=data.get('Links'),
        )


@dataclass
class WebIdInfo:
    """Information about a WebID."""
    
    web_id: str
    object_type: str
    path: Optional[str] = None
    owner_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'WebId': self.web_id,
            'Type': self.object_type,
            'Path': self.path,
            'OwnerType': self.owner_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WebIdInfo:
        """Create from dictionary."""
        return cls(
            web_id=data['WebId'],
            object_type=data['Type'],
            path=data.get('Path'),
            owner_type=data.get('OwnerType'),
        )


@dataclass
class SecurityRights:
    """Security rights for a PI Web API object."""
    
    owner_web_id: str
    security_item: str
    user_identity: str
    can_read: bool = False
    can_write: bool = False
    can_delete: bool = False
    can_read_data: bool = False
    can_write_data: bool = False
    can_execute: bool = False
    can_annotate: bool = False
    can_subscribe: bool = False
    can_subscribe_others: bool = False
    has_admin: bool = False
    rights: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'OwnerWebId': self.owner_web_id,
            'SecurityItem': self.security_item,
            'UserIdentity': self.user_identity,
            'CanRead': self.can_read,
            'CanWrite': self.can_write,
            'CanDelete': self.can_delete,
            'CanReadData': self.can_read_data,
            'CanWriteData': self.can_write_data,
            'CanExecute': self.can_execute,
            'CanAnnotate': self.can_annotate,
            'CanSubscribe': self.can_subscribe,
            'CanSubscribeOthers': self.can_subscribe_others,
            'HasAdmin': self.has_admin,
            'Rights': self.rights,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SecurityRights:
        """Create from dictionary."""
        return cls(
            owner_web_id=data['OwnerWebId'],
            security_item=data['SecurityItem'],
            user_identity=data['UserIdentity'],
            can_read=data.get('CanRead', False),
            can_write=data.get('CanWrite', False),
            can_delete=data.get('CanDelete', False),
            can_read_data=data.get('CanReadData', False),
            can_write_data=data.get('CanWriteData', False),
            can_execute=data.get('CanExecute', False),
            can_annotate=data.get('CanAnnotate', False),
            can_subscribe=data.get('CanSubscribe', False),
            can_subscribe_others=data.get('CanSubscribeOthers', False),
            has_admin=data.get('HasAdmin', False),
            rights=data.get('Rights'),
        )


@dataclass
class Links:
    """Links to related resources."""
    
    self: Optional[str] = None
    parent: Optional[str] = None
    database: Optional[str] = None
    server: Optional[str] = None
    template: Optional[str] = None
    categories: Optional[str] = None
    attributes: Optional[str] = None
    elements: Optional[str] = None
    security: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.self:
            result['Self'] = self.self
        if self.parent:
            result['Parent'] = self.parent
        if self.database:
            result['Database'] = self.database
        if self.server:
            result['Server'] = self.server
        if self.template:
            result['Template'] = self.template
        if self.categories:
            result['Categories'] = self.categories
        if self.attributes:
            result['Attributes'] = self.attributes
        if self.elements:
            result['Elements'] = self.elements
        if self.security:
            result['Security'] = self.security
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Links:
        """Create from dictionary."""
        return cls(
            self=data.get('Self'),
            parent=data.get('Parent'),
            database=data.get('Database'),
            server=data.get('Server'),
            template=data.get('Template'),
            categories=data.get('Categories'),
            attributes=data.get('Attributes'),
            elements=data.get('Elements'),
            security=data.get('Security'),
        )


def to_pi_web_api_dict(obj: Any, exclude_none: bool = True) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a PI Web API compatible dictionary.
    
    Args:
        obj: The dataclass instance to convert
        exclude_none: If True, exclude None values from output
        
    Returns:
        Dictionary with proper PI Web API field names
    """
    if hasattr(obj, 'to_dict'):
        return obj.to_dict(exclude_none=exclude_none)
    elif hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    else:
        return obj
