"""High-level client interface for EdgeAI authentication.

Provides a simplified Python API for authentication workflows,
wrapping the underlying command system in a user-friendly interface.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .commands.login import execute_login
from .config import get_service_url
from .zededa_edgeai_sdk import ZededaEdgeAISDK
from .exceptions import AuthenticationError


class ZededaEdgeAIClient:
    """High-level Python client interface for EdgeAI authentication.
    
    Provides a simplified, user-friendly API for authentication workflows
    including both browser-based and programmatic login methods. Wraps
    the underlying SDK and command system in an easy-to-use interface.
    """

    def __init__(
        self,
        service_url: Optional[str] = None,
        *,
        debug: bool = False,
    ) -> None:
        """Initialize the EdgeAI client with service configuration.
        
        Sets up the client with the backend service URL and debug settings,
        creating an internal SDK instance for handling authentication
        operations and service communication.
        """
        default_service_url = get_service_url()
        self.service_url = (service_url or default_service_url).rstrip("/")
        self.debug = debug
        self._sdk = ZededaEdgeAISDK(self.service_url, ui_url=self.service_url,
                                   debug=debug)

    def login(
        self,
        catalog_id: Optional[str] = None,
        *,
        email: Optional[str] = None,
        password: Optional[str] = None,
        prompt_password: bool = False,
    ) -> Dict[str, str]:
        """Authenticate and configure environment variables for the specified catalog.
        
        Performs authentication using either browser OAuth (when no email/password
        provided) or credential-based login. Automatically sets up environment
        variables for MLflow and storage access upon successful authentication.
        """
        try:
            credentials = execute_login(
                catalog_id,
                email=email,
                password=password,
                prompt_password=prompt_password,
                service_url=self.service_url,
                prompt_on_multiple=True,
                debug=self.debug,
                sdk=self._sdk,
            )
            print("\nLogin completed successfully.\n")
            return credentials
        except ValueError as exc:
            print(f"Error: {exc}")
            return {}
        except AuthenticationError as exc:
            print(f"Authentication failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during login: {exc}")
            return {}

    def logout(self) -> Dict[str, Any]:
        """Terminate authenticated session locally and on the backend."""

        try:
            from .commands.logout import execute_logout

            result = execute_logout(
                service_url=self.service_url,
                sdk=self._sdk,
                debug=self.debug,
            )

            print(result.get("message", ""))

            backend = result.get("backend", {})
            if backend.get("attempted") and not backend.get("success"):
                detail = backend.get("message")
                if detail:
                    print(f"Warning: {detail}")

            return result
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Logout failed: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "backend": {
                    "attempted": False,
                    "success": False,
                    "status_code": None,
                    "message": "Logout raised exception",
                },
            }

    def browser_login(
        self,
        catalog_id: Optional[str] = None,
        *,
        prompt_on_multiple: bool = True,
    ) -> Dict[str, str]:
        """Authenticate using browser-based OAuth flow with catalog selection.
        
        Opens the user's browser for OAuth authentication, handles catalog
        selection when multiple catalogs are available, and configures
        environment variables for successful authentication.
        """

        try:
            return execute_login(
                catalog_id,
                service_url=self.service_url,
                prompt_on_multiple=prompt_on_multiple,
                debug=self.debug,
                sdk=self._sdk,
            )
        except AuthenticationError as exc:
            print(f"Authentication failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during browser login: {exc}")
            return {}

    def list_catalogs(self, formatted: bool = True) -> Optional[Dict[str, Any]]:
        """List all available catalogs for the authenticated user.
        
        Retrieves and returns information about all catalogs that the user
        has access to, including the currently selected catalog.
        
        Parameters
        ----------
        formatted : bool, optional
            If True, prints formatted output to console and returns None.
            If False, returns raw dictionary with catalog data.
            Default is True.
        
        Returns
        -------
        Optional[Dict[str, Any]]
            None when formatted=True.
            Dictionary containing available catalogs list and user info
            when formatted=False.
            
        Raises
        ------
        AuthenticationError
            If user is not logged in or catalog listing fails
        """
        try:
            from .commands.catalogs import execute_catalog_list
            result = execute_catalog_list(
                service_url=self.service_url,
                debug=self.debug,
                sdk=self._sdk,
            )
            
            if formatted:
                self._print_catalog_list(result)
                return None
            return result
        except AuthenticationError as exc:
            print(f"Failed to list catalogs: {exc}")
            return None if formatted else {}
        except Exception as exc:
            print(f"Unexpected error during catalog listing: {exc}")
            return None if formatted else {}
    
    def _print_catalog_list(self, result: Dict[str, Any]) -> None:
        """Print catalog list in a formatted way."""
        available_catalogs = result.get("available_catalogs", [])
        current_catalog = result.get("current_catalog")
        user_info = result.get("user_info", {})
        total_count = result.get("total_count", 0)
        
        print("Available Catalogs:")
        print("==================")
        
        if not available_catalogs:
            print("No catalogs available for this user.")
            return
            
        for i, catalog in enumerate(available_catalogs, 1):
            marker = " (current)" if catalog == current_catalog else ""
            print(f" {i}. {catalog}{marker}")
        
        print(f"\nTotal: {total_count} catalog{'s' if total_count != 1 else ''}")
        
        if current_catalog:
            print(f"Current catalog: {current_catalog}")
        else:
            print("No catalog currently selected")
            
        # Show user context if available
        if user_info.get("email"):
            print(f"User: {user_info['email']}")

    def switch_catalog(self, catalog_id: str) -> Dict[str, str]:
        """Switch to a different catalog and update environment variables.
        
        Switches the current catalog context while maintaining the existing
        authentication session. Updates environment variables with catalog-
        specific credentials for MLflow and storage access.
        
        Parameters
        ----------
        catalog_id : str
            The ID of the catalog to switch to
            
        Returns
        -------
        Dict[str, str]
            Sanitized credentials and environment information
            
        Raises
        ------
        AuthenticationError
            If user is not logged in or catalog switching fails
        ValueError
            If catalog_id is invalid or missing
        """
        try:
            from .commands.catalogs import execute_catalog_switch
            credentials = execute_catalog_switch(
                catalog_id,
                service_url=self.service_url,
                debug=self.debug,
                sdk=self._sdk,
            )
            print(f"\nSuccessfully switched to catalog: {catalog_id}")
            return credentials
        except ValueError as exc:
            print(f"Error: {exc}")
            return {}
        except AuthenticationError as exc:
            print(f"Catalog switch failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during catalog switch: {exc}")
            return {}

    # Module-level convenience functions

def login(
    catalog_id: Optional[str] = None,
    *,
    email: Optional[str] = None,
    password: Optional[str] = None,
    prompt_password: bool = False,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, str]:
    """Convenience function for authentication without creating a client instance.
    
    Provides a simple module-level interface for authentication that internally
    creates a ZededaEdgeAIClient and executes the login workflow with the
    specified parameters.
    """
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.login(catalog_id, email=email, password=password,
                       prompt_password=prompt_password)


def list_catalogs(
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
    formatted: bool = True,
) -> Optional[Dict[str, Any]]:
    """Convenience function for listing catalogs without creating a client instance.
    
    Provides a simple module-level interface for catalog listing that internally
    uses the catalog listing workflow with the specified parameters.
    
    Parameters
    ----------
    service_url : str, optional
        EdgeAI service URL override
    debug : bool, optional
        Enable debug logging
    formatted : bool, optional
        If True, prints formatted output to console and returns None.
        If False, returns raw dictionary with catalog data.
        Default is True.
        
    Returns
    -------
    Optional[Dict[str, Any]]
        None when formatted=True.
        Dictionary containing available catalogs list and user info
        when formatted=False.
    """
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_catalogs(formatted=formatted)


def switch_catalog(
    catalog_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, str]:
    """Convenience function for catalog switching without creating a client instance.
    
    Provides a simple module-level interface for catalog switching that internally
    uses the catalog switching workflow with the specified parameters.
    
    Parameters
    ----------
    catalog_id : str
        The ID of the catalog to switch to
    service_url : str, optional
        EdgeAI service URL override
    debug : bool, optional
        Enable debug logging
        
    Returns
    -------
    Dict[str, str]
        Sanitized credentials and environment information
    """
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.switch_catalog(catalog_id)


def logout(
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Convenience function for terminating the active session."""

    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.logout()
