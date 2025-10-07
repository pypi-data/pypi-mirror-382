"""Catalog management command providing catalog listing and switching functionality.

Implements comprehensive catalog operations including listing available catalogs
and switching between different catalogs while maintaining authentication session.
The catalog service retrieves catalog information from the 'all_catalogs' field
in the API response to provide complete catalog access.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, Optional

from ..config import get_service_url
from ..zededa_edgeai_sdk import ZededaEdgeAISDK
from ..environment import (
    APPLIED_ENVIRONMENT_KEYS,
    apply_environment,
    sanitize_credentials,
)
from ..exceptions import AuthenticationError
from . import CommandSpec


def execute_catalog_list(
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
    sdk: ZededaEdgeAISDK | None = None,
) -> Dict[str, Any]:
    """List all available catalogs for the authenticated user.
    
    Retrieves and displays all catalogs that the user has access to
    from the backend API, showing catalog names and basic information.
    
    Parameters
    ----------
    service_url : str, optional
        EdgeAI service URL override
    debug : bool, optional
        Enable debug logging
    sdk : ZededaEdgeAISDK, optional
        Existing SDK instance to use
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing list of available catalogs and user info
        
    Raises
    ------
    AuthenticationError
        If user is not logged in or catalog listing fails
    """
    # Check if user is already logged in
    existing_token = os.environ.get("EDGEAI_ACCESS_TOKEN")
    if not existing_token:
        raise AuthenticationError(
            "Not logged in. Please run 'zededa-edgeai login' first."
        )
    
    if sdk is not None:
        service_url = sdk.edgeai_backend_url
    else:
        service_url = (service_url or get_service_url()).rstrip("/")
        sdk = ZededaEdgeAISDK(service_url, ui_url=service_url, debug=debug)

    assert sdk is not None  # Satisfy type-checkers
    
    # Get user info which contains available catalogs
    url = f"{service_url}/api/v1/user-info"
    headers = {"Authorization": f"Bearer {existing_token}"}
    
    try:
        response = sdk._send_request("GET", url, headers=headers)
    except Exception as exc:
        raise AuthenticationError(f"Failed to fetch catalog list: {exc}") from exc
    
    if response.status_code != 200:
        raise AuthenticationError(
            f"Failed to fetch catalog list: {response.status_code} {response.text}"
        )
    
    try:
        data = response.json() or {}
    except ValueError as exc:
        raise AuthenticationError("Invalid response from catalog list API") from exc
    
    if not isinstance(data, dict):
        raise AuthenticationError("Invalid response format from catalog list API")
    
    # Extract all catalogs that user has access to
    all_catalogs = data.get("all_catalogs", [])
    if not isinstance(all_catalogs, list):
        all_catalogs = []
    
    # Extract user info for context
    user_info = {
        "user_id": data.get("user_id"),
        "email": data.get("email"), 
        "name": data.get("name"),
        "organization_role": data.get("organization_role"),
    }
    
    # Get current catalog from environment
    current_catalog = os.environ.get("EDGEAI_CURRENT_CATALOG")
    
    return {
        "available_catalogs": all_catalogs,
        "current_catalog": current_catalog,
        "user_info": user_info,
        "total_count": len(all_catalogs)
    }


def execute_catalog_switch(
    catalog_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
    sdk: ZededaEdgeAISDK | None = None,
) -> Dict[str, Any]:
    """Execute catalog switching workflow and update environment variables.
    
    Switches to a different catalog using existing authentication, retrieves
    catalog-specific credentials, and applies them to the current environment.
    Returns sanitized credentials for display.
    
    Parameters
    ----------
    catalog_id : str
        The ID of the catalog to switch to
    service_url : str, optional
        EdgeAI service URL override
    debug : bool, optional
        Enable debug logging
    sdk : ZededaEdgeAISDK, optional
        Existing SDK instance to use
        
    Returns
    -------
    Dict[str, Any]
        Sanitized credentials and environment information
        
    Raises
    ------
    AuthenticationError
        If user is not logged in or catalog switching fails
    ValueError
        If catalog_id is invalid or missing
    """
    if not catalog_id or not catalog_id.strip():
        raise ValueError("Catalog ID is required and cannot be empty")
    
    catalog_id = catalog_id.strip()
    
    # Check if user is already logged in
    existing_token = os.environ.get("EDGEAI_ACCESS_TOKEN")
    if not existing_token:
        raise AuthenticationError(
            "Not logged in. Please run 'zededa-edgeai login' first."
        )
    
    if sdk is not None:
        service_url = sdk.edgeai_backend_url
    else:
        service_url = (service_url or get_service_url()).rstrip("/")
        sdk = ZededaEdgeAISDK(service_url, ui_url=service_url, debug=debug)

    assert sdk is not None  # Satisfy type-checkers
    
    # Get catalog-scoped token for the new catalog
    scoped_response = sdk._get_catalog_scoped_token(existing_token, catalog_id)
    if not scoped_response:
        raise AuthenticationError(
            f"Failed to switch to catalog '{catalog_id}'. "
            "Please check that the catalog exists and you have access to it."
        )
    
    scoped_token = scoped_response.get("access_token")
    if not scoped_token:
        raise AuthenticationError(
            "Catalog switch failed: unable to acquire catalog-scoped token"
        )
    
    # Get MinIO credentials for the new catalog
    minio_credentials = sdk._get_minio_credentials(scoped_token, catalog_id)
    if not minio_credentials:
        raise AuthenticationError(
            f"Failed to retrieve storage credentials for catalog '{catalog_id}'"
        )
    
    # Add catalog and permission information
    minio_credentials["catalog_id"] = catalog_id
    minio_credentials["backend_jwt"] = scoped_token
    
    # Add token metadata
    minio_credentials["token_type"] = scoped_response.get("token_type", "bearer")
    minio_credentials["expires_in"] = scoped_response.get("expires_in")
    
    # Apply environment variables
    env_vars = apply_environment(minio_credentials, catalog_id)
    minio_credentials["environment"] = env_vars
    
    return sanitize_credentials(minio_credentials)


def handle_cli(args: argparse.Namespace) -> None:  # pragma: no cover
    """Handle the catalog command when invoked from the CLI.
    
    Processes command-line arguments and executes catalog listing workflow.
    """
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    list_catalogs = getattr(args, "list", False)
    
    # Only handle list operation
    if list_catalogs:
        _handle_list_command(service_url, debug)
    else:
        print("Error: --list parameter is required")
        print("Use 'zededa-edgeai set-catalog-context <catalog>' to switch catalogs")
        raise SystemExit(1)


def _handle_list_command(service_url: str, debug: bool) -> None:
    """Handle the catalog list subcommand."""
    try:
        result = execute_catalog_list(
            service_url=service_url,
            debug=debug,
        )
        
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
            print(f"{i:2d}. {catalog}{marker}")
        
        print(f"\nTotal: {total_count} catalog{'s' if total_count != 1 else ''}")
        
        if current_catalog:
            print(f"Current catalog: {current_catalog}")
        else:
            print("No catalog currently selected")
            
        # Show user context if available
        if user_info.get("email"):
            print(f"User: {user_info['email']}")
        
    except KeyboardInterrupt:
        print("\nCatalog list cancelled by user.")
        raise SystemExit(1)
    except AuthenticationError as exc:
        print(f"Failed to list catalogs: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Unexpected error during catalog listing: {exc}")
        if debug:
            import traceback
            traceback.print_exc()
        raise SystemExit(1) from exc


def _mask_value(value: str) -> str:
    """Mask sensitive values for display in console output.
    
    Returns a masked version showing only first and last few characters
    to prevent credential exposure while maintaining identifiability.
    """
    if len(value) <= 10:
        return "***"
    return f"{value[:6]}...{value[-4:]}"


def _register(subparsers: argparse._SubParsersAction) -> None:
    """Configure argparse with catalogs command options and arguments.
    
    Defines the catalog listing command with service URL override and debug settings.
    """
    parser = subparsers.add_parser(
        "catalog",
        help="List available catalogs",
        description="List available catalogs for the authenticated user.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available catalogs for the current user"
    )
    parser.add_argument(
        "--service-url",
        help="EdgeAI service URL override (default: use EDGEAI_SERVICE_URL "
             "environment variable or https://studio.edgeai.zededa.dev)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.set_defaults(_command_handler=handle_cli)


CATALOGS_COMMAND = CommandSpec(
    name="catalog",
    help="List available catalogs",
    register=_register,
)
