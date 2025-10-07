"""Zededa EdgeAI SDK package."""

from .client import ZededaEdgeAIClient, login, logout, list_catalogs, switch_catalog
from .exceptions import (
    ZededaSDKError,
    AuthenticationError,
    CatalogNotFoundError,
    MultipleCatalogsError,
    UserCancelledError,
)

__all__ = [
    "ZededaEdgeAIClient",
    "login",
    "logout",
    "list_catalogs",
    "switch_catalog",
    "ZededaSDKError",
    "AuthenticationError",
    "CatalogNotFoundError",
    "MultipleCatalogsError",
    "UserCancelledError",
]
