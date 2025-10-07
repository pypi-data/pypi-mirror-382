class ZededaSDKError(Exception):
    """Base exception for the EdgeAI SDK."""


class AuthenticationError(ZededaSDKError):
    """Raised when authentication fails."""


class CatalogNotFoundError(ZededaSDKError):
    """Raised when a requested catalog cannot be found or accessed."""


class MultipleCatalogsError(ZededaSDKError):
    """Raised when multiple catalogs require user selection."""


class UserCancelledError(ZededaSDKError):
    """Raised when a user cancels an interactive flow."""
