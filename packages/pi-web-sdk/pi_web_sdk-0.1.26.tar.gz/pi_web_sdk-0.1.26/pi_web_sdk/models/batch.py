"""Data models for batch-related PI Web API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


__all__ = [
    "Batch",
    "BatchRequest",
]


@dataclass
class BatchRequest:
    """Batch request object for batch operations."""
    
    method: str
    resource: str
    content: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[List[str]] = None
    parent_ids: Optional[List[str]] = None
    request_template: Optional[Dict[str, Any]] = None
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        result = {
            'Method': self.method,
            'Resource': self.resource,
        }
        
        if self.content is not None or not exclude_none:
            result['Content'] = self.content
        if self.headers is not None or not exclude_none:
            result['Headers'] = self.headers
        if self.parameters is not None or not exclude_none:
            result['Parameters'] = self.parameters
        if self.parent_ids is not None or not exclude_none:
            result['ParentIds'] = self.parent_ids
        if self.request_template is not None or not exclude_none:
            result['RequestTemplate'] = self.request_template
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BatchRequest:
        """Create from PI Web API response."""
        return cls(
            method=data['Method'],
            resource=data['Resource'],
            content=data.get('Content'),
            headers=data.get('Headers'),
            parameters=data.get('Parameters'),
            parent_ids=data.get('ParentIds'),
            request_template=data.get('RequestTemplate'),
        )


@dataclass
class Batch:
    """Batch object containing multiple requests."""
    
    requests: List[BatchRequest]
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to PI Web API format."""
        return {
            'Requests': [req.to_dict(exclude_none) for req in self.requests]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Batch:
        """Create from PI Web API response."""
        requests = [BatchRequest.from_dict(req) for req in data.get('Requests', [])]
        return cls(requests=requests)
