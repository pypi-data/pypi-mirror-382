"""Configuration primitives for the PI Web API SDK."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

__all__ = ["AuthMethod", "WebIDType", "PIWebAPIConfig"]


class AuthMethod(Enum):
    """Authentication methods supported by PI Web API."""

    BASIC = "basic"
    KERBEROS = "kerberos"
    BEARER = "bearer"
    ANONYMOUS = "anonymous"


class WebIDType(Enum):
    """WebID types for encoding format."""

    FULL = "Full"
    ID_ONLY = "IDOnly"
    PATH_ONLY = "PathOnly"
    LOCAL_ID_ONLY = "LocalIDOnly"
    DEFAULT_ID_ONLY = "DefaultIDOnly"


@dataclass
class PIWebAPIConfig:
    """Configuration for PI Web API client."""

    base_url: str
    auth_method: AuthMethod = AuthMethod.ANONYMOUS
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    verify_ssl: bool = True
    timeout: int = 30
    webid_type: WebIDType = WebIDType.FULL
