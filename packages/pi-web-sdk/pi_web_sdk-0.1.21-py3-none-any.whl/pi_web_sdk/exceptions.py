"""Custom exceptions for the PI Web API SDK."""

from __future__ import annotations

from typing import Dict, Optional

__all__ = ['PIWebAPIError']

class PIWebAPIError(Exception):
    """Base exception for PI Web API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)
