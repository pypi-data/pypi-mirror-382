"""Environment variable management for EdgeAI credentials and settings.

Provides utilities to apply authentication credentials to the shell
environment and sanitize sensitive data for display purposes.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any, Dict, Optional

__all__ = [
    "APPLIED_ENVIRONMENT_KEYS",
    "apply_environment",
    "clear_environment",
    "sanitize_credentials",
]

APPLIED_ENVIRONMENT_KEYS = [
    "EDGEAI_CURRENT_CATALOG",
    "EDGEAI_ACCESS_TOKEN",
    "MLFLOW_TRACKING_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "MLFLOW_S3_ENDPOINT_URL",
    "MLFLOW_TRACKING_URI",
    "MINIO_BUCKET",
    "EDGEAI_BACKEND_URL",
]


def apply_environment(
    credentials: Dict[str, str], catalog_id: str
) -> Dict[str, Optional[str]]:
    """Populate OS environment variables based on provided credentials.

    Parameters
    ----------
    credentials:
        Raw credential payload returned by the backend/login workflow.
    catalog_id:
        Catalog identifier for the current session.

    Returns
    -------
    dict
        Mapping of environment variable names to the values that were applied.
    """

    env_vars = {
        "EDGEAI_CURRENT_CATALOG": catalog_id,
        "EDGEAI_ACCESS_TOKEN": credentials.get("backend_jwt"),
        "MLFLOW_TRACKING_TOKEN": credentials.get("backend_jwt"),
        "AWS_ACCESS_KEY_ID": credentials.get("aws_access_key_id"),
        "AWS_SECRET_ACCESS_KEY": credentials.get("aws_secret_access_key"),
        "MLFLOW_S3_ENDPOINT_URL": credentials.get("endpoint_url"),
        "MLFLOW_TRACKING_URI": credentials.get("mlflow_tracking_uri"),
        "MINIO_BUCKET": credentials.get("bucket"),
        "EDGEAI_BACKEND_URL": credentials.get("service_url"),
    }

    for key, value in env_vars.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(value)

    return env_vars


def clear_environment() -> None:
    """Remove all SDK-specific environment variables from the current process."""

    for key in APPLIED_ENVIRONMENT_KEYS:
        os.environ.pop(key, None)


def sanitize_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of ``credentials`` with sensitive values obfuscated for display."""

    sanitized = deepcopy(credentials)

    sensitive_keys = {
        "backend_jwt",
        "access_token",
        "aws_access_key_id",
        "aws_secret_access_key",
        "secret_key",
        "token",
        "password",
    }

    for key in sensitive_keys:
        value = sanitized.get(key)
        if not value:
            continue
        value_str = str(value)
        sanitized[key] = _mask_string(value_str)

    env_payload = sanitized.get("environment")
    if isinstance(env_payload, dict):
        for key, value in list(env_payload.items()):
            if value is None:
                continue
            if any(sensitive in key.upper() for sensitive in ["TOKEN", "KEY", "SECRET"]):
                env_payload[key] = _mask_string(str(value))

    return sanitized


def _mask_string(value: str) -> str:
    """Mask sensitive string values for safe display in logs and output.
    
    Returns a masked version of the string showing only the first 6 and last 4
    characters for longer values, or '***' for shorter strings, preventing
    credential exposure while maintaining some identifiability.
    """
    if len(value) <= 10:
        return "***"
    return f"{value[:6]}...{value[-4:]}"
