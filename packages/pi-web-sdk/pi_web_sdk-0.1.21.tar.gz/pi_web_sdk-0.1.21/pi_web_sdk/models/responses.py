"""Response data classes for PI Web API endpoints.

These classes provide type-safe wrappers around PI Web API responses,
automatically parsing JSON responses into strongly-typed Python objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, TypeVar, Generic, Type, Callable


__all__ = [
    'ItemsResponse',
    'PIResponse',
    'parse_response',
    'parse_items_response',
]


T = TypeVar('T')


@dataclass
class ItemsResponse(Generic[T]):
    """Generic response wrapper for collection endpoints.
    
    PI Web API typically returns collection responses with this structure:
    {
        "Items": [...],
        "Links": {...}
    }
    """
    
    items: List[T]
    links: Optional[Dict[str, str]] = None
    
    def __len__(self) -> int:
        """Return number of items."""
        return len(self.items)
    
    def __iter__(self):
        """Iterate over items."""
        return iter(self.items)
    
    def __getitem__(self, index: int) -> T:
        """Get item by index."""
        return self.items[index]
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        item_class: Type[T],
    ) -> ItemsResponse[T]:
        """Create from PI Web API response.
        
        Args:
            data: Raw response dictionary
            item_class: Class to parse each item (must have from_dict method)
            
        Returns:
            ItemsResponse with parsed items
        """
        items_data = data.get('Items', [])
        
        # Parse items using the item_class.from_dict method
        if hasattr(item_class, 'from_dict'):
            items = [item_class.from_dict(item) for item in items_data]
        else:
            # If no from_dict method, just use the items as-is
            items = items_data
            
        return cls(
            items=items,
            links=data.get('Links'),
        )


@dataclass
class PIResponse(Generic[T]):
    """Generic response wrapper for single object endpoints.
    
    Wraps a single object response with additional metadata.
    """
    
    data: T
    links: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        data_class: Type[T],
    ) -> PIResponse[T]:
        """Create from PI Web API response.
        
        Args:
            data: Raw response dictionary
            data_class: Class to parse the data (must have from_dict method)
            
        Returns:
            PIResponse with parsed data
        """
        # Parse the data using data_class.from_dict
        if hasattr(data_class, 'from_dict'):
            parsed_data = data_class.from_dict(data)
        else:
            parsed_data = data
            
        return cls(
            data=parsed_data,
            links=data.get('Links'),
        )


def parse_response(
    response: Dict[str, Any],
    data_class: Type[T],
) -> T:
    """Parse a single object response.
    
    Helper function to parse a PI Web API response into a data class.
    
    Args:
        response: Raw response dictionary from PI Web API
        data_class: Class to parse into (must have from_dict method)
        
    Returns:
        Parsed object of type data_class
        
    Example:
        >>> response = client.data_server.get(web_id)
        >>> data_server = parse_response(response, DataServer)
        >>> print(data_server.name)
    """
    if hasattr(data_class, 'from_dict'):
        return data_class.from_dict(response)
    else:
        raise ValueError(f"{data_class.__name__} must have a from_dict class method")


def parse_items_response(
    response: Dict[str, Any],
    item_class: Type[T],
) -> ItemsResponse[T]:
    """Parse a collection response with Items array.
    
    Helper function to parse a PI Web API collection response.
    
    Args:
        response: Raw response dictionary from PI Web API
        item_class: Class to parse each item into
        
    Returns:
        ItemsResponse with parsed items
        
    Example:
        >>> response = client.data_server.get_points(web_id)
        >>> points = parse_items_response(response, Point)
        >>> for point in points:
        ...     print(point.name)
    """
    return ItemsResponse.from_dict(response, item_class)
