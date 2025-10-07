"""Core SDK facade coordinating authentication and service access.

Provides the main interface for EdgeAI operations by orchestrating
the various service components for authentication and data access.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .services import AuthService, CatalogService, HTTPService, StorageService


class ZededaEdgeAISDK:
    """Main SDK facade coordinating authentication and service access.
    
    Provides the primary interface for EdgeAI operations by orchestrating
    various service components including authentication, catalog management,
    and storage access. Maintains backward compatibility while delegating
    to the modular service layer.
    """

    def __init__(self, edgeai_backend_url: str, ui_url: str | None = None,
                 debug: bool = False):
        """Initialize the EdgeAI SDK with backend configuration and service dependencies.
        
        Sets up the SDK with the backend API URL, optional UI URL for OAuth flows,
        and debug settings. Initializes all service layer components including
        HTTP, authentication, catalog, and storage services.
        """
        self.edgeai_backend_url = edgeai_backend_url.rstrip("/")
        self.ui_url = (ui_url or edgeai_backend_url).rstrip("/")
        self.debug = debug

        # State attributes for compatibility
        self.jwt: Optional[str] = None
        self.session_id: Optional[str] = None
        self.s3_credentials: Optional[Dict[str, Any]] = None

        # Service layer collaborators
        self._http = HTTPService(debug=debug)
        self._auth = AuthService(self.edgeai_backend_url, self.ui_url,
                               debug=debug)
        self._catalogs = CatalogService(self.edgeai_backend_url, self._http)
        self._storage = StorageService(self.edgeai_backend_url, self._http)

    # Properties for compatibility with existing code
    @property
    def oauth_result(self) -> Optional[dict]:
        """Get the OAuth authentication result from the auth service.
        
        Returns the current OAuth flow result containing success status,
        JWT tokens, or error information from the most recent authentication attempt.
        """
        return self._auth.oauth_result

    @oauth_result.setter
    def oauth_result(self, value: Optional[dict]) -> None:
        """Set the OAuth authentication result in the auth service.
        
        Updates the OAuth flow result, typically used internally during
        the authentication process to store callback results.
        """
        self._auth.oauth_result = value

    @property
    def oauth_server(self):  # pragma: no cover - accessor
        """Get the OAuth callback server instance from the auth service.
        
        Returns the HTTP server used for handling OAuth callbacks during
        browser-based authentication flows.
        """
        return self._auth.oauth_server

    @oauth_server.setter
    def oauth_server(self, value) -> None:  # pragma: no cover - accessor
        """Set the OAuth callback server instance in the auth service.
        
        Updates the HTTP server reference, typically used internally
        during OAuth flow setup and cleanup operations.
        """
        self._auth.oauth_server = value

    def oauth_login(self, catalog_id: str | None = None) -> Optional[str]:
        """Perform OAuth login flow via browser with optional catalog targeting.
        
        Delegates to the auth service to execute the complete OAuth flow
        including browser interaction and callback handling. Returns JWT
        token on success or None if authentication fails.
        """
        return self._auth.oauth_login(catalog_id)

    def login_with_browser(
        self,
        catalog_id: str | None = None,
        *,
        prompt_on_multiple: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Execute complete browser login workflow with catalog selection and credential retrieval.
        
        Performs OAuth authentication, handles catalog selection when multiple
        catalogs are available, retrieves MinIO storage credentials, and returns
        complete authentication data ready for environment configuration.
        """
        backend_jwt = self.oauth_login(catalog_id)
        if not backend_jwt:
            return None

        selected_catalog, scoped_token = self._resolve_catalog_selection(
            backend_jwt,
            catalog_id,
            prompt_on_multiple=prompt_on_multiple,
        )

        if not selected_catalog or not scoped_token:
            return None

        minio_credentials = self._get_minio_credentials(scoped_token, selected_catalog)
        if not minio_credentials:
            return None

        minio_credentials["catalog_id"] = selected_catalog
        return minio_credentials

    # Internal helpers for backward compatibility
    def _send_request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str] | None = None,
        json: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        timeout: int = 30,
    ):
        """Proxy HTTP requests through the HTTP service."""
        return self._http.request(
            method,
            url,
            headers=headers,
            json=json,
            params=params,
            timeout=timeout,
        )

    def _get_minio_credentials(self, backend_jwt: str,
                              catalog_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve MinIO storage credentials through the storage service.
        
        Delegates to the storage service to fetch S3-compatible credentials
        including access keys, endpoints, and bucket information for the
        specified catalog.
        """
        return self._storage.get_minio_credentials(backend_jwt, catalog_id)

    def _get_catalogs(self, backend_jwt: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve catalog information through the catalog service.
        
        Delegates to the catalog service to fetch both available_catalogs
        (what user has access to) and all_catalogs (complete list for
        selection UI) with metadata and permission information.
        """
        return self._catalogs.get_catalogs(backend_jwt)

    def _get_catalog_scoped_token(self, backend_jwt: str,
                                 catalog_id: str) -> Optional[Dict[str, Any]]:
        """Obtain catalog-specific authentication token through the catalog service.
        
        Delegates to the catalog service to exchange a general authentication
        token for a catalog-scoped token with permissions limited to the
        specified catalog.
        """
        return self._catalogs.get_catalog_scoped_token(backend_jwt,
                                                      catalog_id)

    def _resolve_catalog_selection(
        self,
        backend_jwt: str,
        catalog_id: str | None = None,
        *,
        prompt_on_multiple: bool = True,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Handle catalog selection logic including interactive prompts and token scoping.
        
        Manages catalog selection by either using a provided catalog ID, auto-selecting
        when only one catalog is available, or prompting the user when multiple catalogs
        exist. Returns selected catalog and scoped token. Always checks for multiple
        catalogs and prompts user to select when more than one is available, even if
        catalog_id is provided.
        """
        selected_catalog = catalog_id
        scoped_token = backend_jwt

        # Get both available and all catalogs to determine selection strategy
        catalog_info = self._get_catalogs(backend_jwt)
        available_catalogs = catalog_info.get("available_catalogs", [])
        all_catalogs = catalog_info.get("all_catalogs", [])
        
        if not available_catalogs:
            print("[ERROR] No catalogs available for this user.")
            return None, None

        if len(available_catalogs) == 1:
            # User has access to only one catalog - auto-select it
            selected_catalog = available_catalogs[0].get("catalog_id")
            if not selected_catalog:
                print("[ERROR] Catalog information is missing catalog_id.")
                return None, None
        else:
            # User has access to multiple catalogs - prompt to select from all_catalogs
            if not prompt_on_multiple:
                print("[ERROR] Multiple catalogs available and interactive prompt disabled.")
                return None, None
            
            # Use all_catalogs for the selection prompt (complete list)
            selection_catalogs = all_catalogs if all_catalogs else available_catalogs
            print("Multiple catalogs available. Please select one:")
            for idx, catalog in enumerate(selection_catalogs, 1):
                catalog_identifier = catalog.get("catalog_id") or "(unknown)"
                description = catalog.get("description") or ""
                if description:
                    print(f"  {idx}. {catalog_identifier} - {description}")
                else:
                    print(f"  {idx}. {catalog_identifier}")

            while True:
                try:
                    choice = input(f"Enter selection (1-{len(selection_catalogs)}): ").strip()
                    index = int(choice) - 1
                    if 0 <= index < len(selection_catalogs):
                        selected_catalog = selection_catalogs[index].get("catalog_id")
                        if selected_catalog:
                            # Verify the selected catalog is in available_catalogs
                            available_catalog_ids = [c.get("catalog_id") for c in available_catalogs]
                            if selected_catalog in available_catalog_ids:
                                break
                            else:
                                print(f"You don't have access to catalog '{selected_catalog}'. Please choose from your available catalogs.")
                                continue
                        print("Selected catalog is missing catalog_id. Please choose another.")
                        continue
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\nLogin cancelled by user.")
                    return None, None

        if not selected_catalog:
            print("[ERROR] Catalog selection failed.")
            return None, None

        # Always get a catalog-scoped token for security
        scoped = self._get_catalog_scoped_token(backend_jwt, selected_catalog)
        if not scoped:
            return None, None

        scoped_token = scoped.get("access_token")
        if not scoped_token:
            print("[ERROR] Unable to acquire catalog scoped token.")
            return None, None

        return selected_catalog, scoped_token
