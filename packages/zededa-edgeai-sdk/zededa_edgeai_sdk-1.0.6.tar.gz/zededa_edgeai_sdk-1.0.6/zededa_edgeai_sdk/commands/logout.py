"""Logout command providing environment cleanup functionality.

Implements logout workflow that clears all SDK-related environment
variables to clean up the authentication state.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

import requests

from ..config import get_service_url
from ..environment import clear_environment
from ..services.http import HTTPService
from . import CommandSpec

__all__ = ["execute_logout", "handle_cli", "_register"]


def execute_logout(
    *,
    service_url: str | None = None,
    token: str | None = None,
    sdk: Any | None = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Execute logout workflow by clearing SDK environment and calling backend API.

    Parameters
    ----------
    service_url:
        Optional service URL to use for the backend logout request. If omitted,
        the function falls back to the environment variable ``EDGEAI_BACKEND_URL``
        or the default service URL from configuration.
    token:
        Optional access token to send to the backend logout endpoint. If omitted,
        the function uses the ``EDGEAI_ACCESS_TOKEN`` environment value.
    sdk:
        Optional ``ZededaEdgeAISDK`` instance whose HTTP client will be reused
        for the backend logout call. When omitted, a new ``HTTPService`` is
        instantiated using the provided ``debug`` flag.
    debug:
        Enables debug logging when a new ``HTTPService`` needs to be created.

    Returns
    -------
    dict
        Dictionary describing the outcome of the logout workflow, including
        backend call results when attempted.
    """

    backend_url = (service_url or os.environ.get("EDGEAI_BACKEND_URL") or get_service_url()).rstrip("/")
    access_token = token or os.environ.get("EDGEAI_ACCESS_TOKEN")

    backend_details: Dict[str, Any] = {
        "attempted": False,
        "success": False,
        "status_code": None,
        "message": "Backend logout not attempted",
    }

    if access_token:
        backend_details = _perform_backend_logout(
            backend_url,
            access_token,
            sdk=sdk,
            debug=debug,
        )
    else:
        backend_details["message"] = "No active access token; skipped backend logout"

    clear_environment()

    if backend_details["attempted"] and not backend_details["success"]:
        status = "partial"
        message = "Local credentials cleared, but backend logout failed"
    else:
        status = "success"
        message = "Successfully logged out and cleared environment variables"

    return {
        "status": status,
        "message": message,
        "backend": backend_details,
    }


def _perform_backend_logout(
    service_url: str,
    token: str,
    *,
    sdk: Any | None = None,
    debug: bool,
) -> Dict[str, Any]:
    """Issue a backend logout request and return structured result details."""

    http_client = getattr(sdk, "_http", None)
    if http_client is None:
        http_client = HTTPService(debug=debug)

    url = f"{service_url.rstrip('/')}/api/v1/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = http_client.request("POST", url, headers=headers)
        status_code = getattr(response, "status_code", None)
        success = status_code in (200, 204)
        message = "Backend logout succeeded" if success else (
            f"Backend logout returned status {status_code}"
        )
        return {
            "attempted": True,
            "success": success,
            "status_code": status_code,
            "message": message,
        }
    except requests.RequestException as exc:
        return {
            "attempted": True,
            "success": False,
            "status_code": None,
            "message": f"Backend logout request failed: {exc}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "attempted": True,
            "success": False,
            "status_code": None,
            "message": f"Unexpected backend logout error: {exc}",
        }


def handle_cli(args: argparse.Namespace) -> None:  # pragma: no cover
    """Handle the logout command when invoked from the CLI.
    
    Processes command-line arguments, executes the logout workflow, and
    displays appropriate success or error messages to the user.
    """
    debug = getattr(args, "debug", False)
    try:
        result = execute_logout(debug=debug)
        print(result["message"])

        backend = result.get("backend", {})
        if backend.get("attempted"):
            if backend.get("success"):
                print("Backend session terminated successfully.")
            else:
                detail = backend.get("message")
                if detail:
                    print(f"Warning: {detail}")
                else:
                    print("Warning: Backend logout could not be completed.")
    except Exception as exc:
        print(f"Logout failed: {exc}")
        raise SystemExit(1) from exc


def _register(subparsers: argparse._SubParsersAction) -> None:
    """Configure argparse with logout command options and arguments.
    
    Defines the logout subcommand with appropriate help text and
    options for the CLI interface.
    """
    parser = subparsers.add_parser(
        "logout",
        help="Clear authentication session and environment variables",
        description="Remove all SDK-related environment variables, "
                   "effectively logging out the current user session.",
    )
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.set_defaults(_command_handler=handle_cli)


# Export command specification for registration
LOGOUT_COMMAND = CommandSpec(
    name="logout",
    help="Clear authentication session and environment variables",
    register=_register,
)