"""Authentication command providing login functionality.

Implements both browser-based and credential-based authentication
workflows with environment setup for MLflow and storage access.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import textwrap
from getpass import getpass
from typing import Any, Dict, Optional

import requests

from ..config import get_service_url
from ..zededa_edgeai_sdk import ZededaEdgeAISDK
from ..environment import (
    APPLIED_ENVIRONMENT_KEYS,
    apply_environment,
    sanitize_credentials,
)
from ..exceptions import AuthenticationError
from . import CommandSpec


def execute_login(
    catalog_id: Optional[str] = None,
    *,
    email: Optional[str] = None,
    password: Optional[str] = None,
    prompt_password: bool = False,
    service_url: Optional[str] = None,
    prompt_on_multiple: bool = True,
    debug: bool = False,
    sdk: ZededaEdgeAISDK | None = None,
) -> Dict[str, Any]:
    """Execute the complete login workflow and configure environment variables.
    
    Performs authentication using either browser OAuth or email/password credentials,
    handles catalog selection, retrieves storage credentials, and applies them to
    the current environment. Returns sanitized credentials for display.
    """

    if sdk is not None:
        service_url = sdk.edgeai_backend_url
    else:
        service_url = (service_url or get_service_url()).rstrip("/")
        sdk = ZededaEdgeAISDK(service_url, ui_url=service_url, debug=debug)

    assert sdk is not None  # Satisfy type-checkers
    normalized_catalog = _normalize_catalog(catalog_id)

    if email and not password and prompt_password:
        password = getpass("Password: ")

    if email and not password:
        raise ValueError(
            "Password is required when email is provided. "
            "Use prompt_password=True to be prompted for password."
        )
    if password and not email:
        raise ValueError("Email is required when password is provided")

    if email:
        raw_credentials = _login_with_credentials(
            sdk,
            service_url,
            normalized_catalog,
            email,
            password or "",
            prompt_on_multiple=prompt_on_multiple,
        )
    else:
        raw_credentials = _login_with_browser(
            sdk,
            normalized_catalog,
            prompt_on_multiple=prompt_on_multiple,
        )

    catalog_id = raw_credentials.get("catalog_id")
    env_vars = apply_environment(raw_credentials, catalog_id)
    raw_credentials["environment"] = env_vars
    return sanitize_credentials(raw_credentials)


def handle_cli(args: argparse.Namespace) -> None:  # pragma: no cover
    """Handle the login command when invoked from the CLI.
    
    Processes command-line arguments, executes the login workflow, and
    launches an interactive shell with authentication credentials applied
    to the environment variables.
    """
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)

    try:
        credentials = execute_login(
            args.catalog,
            email=getattr(args, "email", None),
            password=getattr(args, "password", None),
            prompt_password=getattr(args, "prompt_password", False),
            service_url=service_url,
            prompt_on_multiple=True,
            debug=debug,
        )
        applied_env = {
            key: os.environ.get(key) for key in APPLIED_ENVIRONMENT_KEYS
        }
        print("Login successful. Launching interactive shell...")
        _launch_shell(applied_env)
    except KeyboardInterrupt:
        print("\nLogin cancelled by user.")
        raise SystemExit(1)
    except AuthenticationError as exc:
        print(f"Login failed: {exc}")
        raise SystemExit(1) from exc
    except ValueError as exc:
        print(exc)
        raise SystemExit(1) from exc
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Unexpected error: {exc}")
        if debug:
            import traceback

            traceback.print_exc()
        raise SystemExit(1) from exc


def _normalize_catalog(catalog_id: Optional[str]) -> Optional[str]:
    """Clean and validate catalog ID input.
    
    Strips whitespace from catalog ID strings and returns None for
    empty or None values, ensuring consistent catalog ID handling.
    """
    if isinstance(catalog_id, str) and catalog_id.strip():
        return catalog_id.strip()
    return None


def _login_with_credentials(
    sdk: ZededaEdgeAISDK,
    service_url: str,
    catalog_id: Optional[str],
    email: str,
    password: str,
    *,
    prompt_on_multiple: bool,
) -> Dict[str, Any]:
    """Authenticate using email and password credentials.
    
    Sends login request to the backend API, handles catalog selection if needed,
    retrieves MinIO credentials, and returns complete authentication data
    including permissions and tokens.
    """
    url = f"{service_url}/api/v1/auth/login"
    payload = {"email": email, "password": password}
    if catalog_id:
        payload["catalog_id"] = catalog_id

    try:
        response = sdk._send_request(  # pylint: disable=protected-access
            "POST", url, json=payload
        )
    except requests.RequestException as exc:  # pragma: no cover
        raise AuthenticationError(f"Login request failed: {exc}") from exc

    if response.status_code != 200:
        raise AuthenticationError(
            f"Login failed with status {response.status_code}: "
            f"{response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise AuthenticationError("Login response is not valid JSON") from exc

    token = data.get("access_token")
    if not token:
        raise AuthenticationError("Login response missing access_token")

    selected_catalog, scoped_token = (
        sdk._resolve_catalog_selection(  # pylint: disable=protected-access
            token,
            catalog_id,
            prompt_on_multiple=prompt_on_multiple,
        )
    )

    if not selected_catalog or not scoped_token:
        raise AuthenticationError("Catalog selection failed or was cancelled")

    minio_credentials = sdk._get_minio_credentials(  # pylint: disable=protected-access
        scoped_token, selected_catalog
    )
    if not minio_credentials:
        raise AuthenticationError("Failed to fetch MinIO credentials")

    minio_credentials["catalog_id"] = selected_catalog
    minio_credentials["backend_jwt"] = scoped_token
    minio_credentials["token_type"] = data.get("token_type", "bearer")
    minio_credentials["expires_in"] = data.get("expires_in")
    minio_credentials["service_url"] = sdk.edgeai_backend_url
    return minio_credentials


def _login_with_browser(
    sdk: ZededaEdgeAISDK,
    catalog_id: Optional[str],
    *,
    prompt_on_multiple: bool,
) -> Dict[str, Any]:
    """Authenticate using browser-based OAuth flow.
    
    Opens a browser for user authentication, handles the OAuth callback,
    manages catalog selection when multiple catalogs are available, and
    returns complete credentials including storage access tokens.
    """
    credentials = sdk.login_with_browser(
        catalog_id, prompt_on_multiple=prompt_on_multiple
    )
    if not credentials:
        raise AuthenticationError("Browser login failed")
    credentials["service_url"] = sdk.edgeai_backend_url
    return credentials


def _mask(value: Optional[str], show: int = 4) -> Optional[str]:
    """Mask sensitive string values for safe console output.
    
    Obscures the middle portion of sensitive strings while preserving
    the beginning and end characters for identification purposes.
    Returns the original value if it's None or shorter than the show parameter.
    """
    if not value:
        return value
    if len(value) <= show:
        return value
    return f"{value[:show]}...{value[-2:]}"


def _launch_shell(env_vars: Dict[str, Optional[str]]) -> None:  # pragma: no cover
    """Start an interactive bash shell with authentication environment configured.
    
    Applies authentication credentials to environment variables, displays
    the configured variables to the user, and spawns a child shell process
    with the credentials available for MLflow and other tools.
    """
    env = os.environ.copy()
    env.update({k: v for k, v in env_vars.items() if v is not None})
    env["ZEDEDA_EDGEAI_LOGIN_SHELL"] = "1"

    for venv_var in ("VIRTUAL_ENV", "CONDA_PREFIX"):
        if venv_var in os.environ:
            env[venv_var] = os.environ[venv_var]

    rc_file = _create_login_rcfile()
    env["ZEDEDA_EDGEAI_RCFILE"] = rc_file

    print("You are now in a shell with the following environment "
          "variables set:")
    print(f"  MLFLOW_TRACKING_TOKEN={_mask(env.get('MLFLOW_TRACKING_TOKEN'))}")
    print(f"  AWS_ACCESS_KEY_ID={_mask(env.get('AWS_ACCESS_KEY_ID'))}")
    print(f"  AWS_SECRET_ACCESS_KEY={_mask(env.get('AWS_SECRET_ACCESS_KEY'))}")
    print(f"  MLFLOW_S3_ENDPOINT_URL={env.get('MLFLOW_S3_ENDPOINT_URL')}")
    print(f"  MLFLOW_TRACKING_URI={env.get('MLFLOW_TRACKING_URI')}")
    print(f"  MINIO_BUCKET={env.get('MINIO_BUCKET')}")
    if env.get("ZEDEDA_CURRENT_CATALOG"):
        print(f"  ZEDEDA_CURRENT_CATALOG={env.get('ZEDEDA_CURRENT_CATALOG')}")
    print("Type 'zededa-edgeai logout' to clear credentials or 'exit' to leave this shell.")

    try:
        subprocess.call(["bash", "--rcfile", rc_file, "-i"], env=env)
    finally:
        try:
            os.unlink(rc_file)
        except FileNotFoundError:
            pass


def _create_login_rcfile() -> str:
    """Create a temporary bash rcfile that wraps the CLI within the login shell."""

    unset_body = "\n".join(
        f"                unset {key}" for key in APPLIED_ENVIRONMENT_KEYS
    )

    rc_contents = textwrap.dedent(
        f"""\
        #!/usr/bin/env bash
        __zededa_edgeai_cleanup() {{
            if [ -n "$ZEDEDA_EDGEAI_RCFILE" ] && [ -f "$ZEDEDA_EDGEAI_RCFILE" ]; then
                rm -f "$ZEDEDA_EDGEAI_RCFILE"
            fi
        }}
        trap '__zededa_edgeai_cleanup' EXIT

        if [ -f ~/.bashrc ]; then
            source ~/.bashrc
        fi

        zededa-edgeai() {{
            if [ "$#" -gt 0 ] && [ "$1" = "logout" ]; then
                command zededa-edgeai "$@"
                local status=$?
                if [ "$status" -eq 0 ]; then
{unset_body}
                    unset ZEDEDA_EDGEAI_LOGIN_SHELL
                    unset ZEDEDA_EDGEAI_RCFILE
                    __zededa_edgeai_cleanup
                fi
                return $status
            fi
            command zededa-edgeai "$@"
            return $?
        }}
        export -f zededa-edgeai
        """
    )

    with tempfile.NamedTemporaryFile("w", delete=False, prefix="zededa_edgeai_login_", suffix=".sh") as tmp:
        tmp.write(rc_contents)
        return tmp.name


def _register(subparsers: argparse._SubParsersAction) -> None:
    """Configure argparse with login command options and arguments.
    
    Defines all command-line options for the login command including
    catalog selection, authentication methods, service URL configuration,
    and debug settings.
    """
    parser = subparsers.add_parser(
        "login",
        help="Authenticate and configure environment",
        description="Authenticate with Zededa EdgeAI and start a shell "
                   "with credentials applied.",
    )
    parser.add_argument("--catalog",
                       help="Catalog ID to authenticate against")
    parser.add_argument("--email",
                       help="Email for programmatic login (no browser)")
    parser.add_argument("--password",
                       help="Password for programmatic login (no browser)")
    parser.add_argument(
        "--prompt-password",
        action="store_true",
        help="Prompt for password if --email is provided and "
             "--password is omitted",
    )
    parser.add_argument(
        "--service-url",
        help="EdgeAI service URL (default: "
             "https://studio.edgeai.zededa.dev)"
    )
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.set_defaults(_command_handler=handle_cli)


LOGIN_COMMAND = CommandSpec(
    name="login",
    help="Authenticate and configure environment",
    register=_register,
)
