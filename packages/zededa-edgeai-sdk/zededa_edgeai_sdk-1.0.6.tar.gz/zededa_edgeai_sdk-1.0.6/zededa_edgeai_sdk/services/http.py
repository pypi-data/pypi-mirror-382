"""HTTP service providing debug-aware request handling.

Wraps the requests library with automatic logging of request/response
data while masking sensitive information for security.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

__all__ = ["HTTPService"]


class HTTPService:
    """HTTP client with debug logging and sensitive data masking.
    
    Wraps the requests library to provide consistent HTTP functionality
    with optional debug output that safely masks sensitive information
    like tokens, passwords, and keys in request/response logs.
    """

    _SENSITIVE_TERMS = {
        "password",
        "secret",
        "token",
        "authorization",
        "access_key",
        "jwt",
    }

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize HTTP service with optional debug logging enabled.
        
        When debug is True, all HTTP requests and responses will be
        logged to the console with sensitive data automatically masked.
        """
        self.debug = debug

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str] | None = None,
        json: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        timeout: int = 30,
    ):
        """Execute HTTP request with automatic debug logging and error handling.
        
        Sends HTTP requests using the requests library while providing
        debug output when enabled. All sensitive data in requests and
        responses is automatically masked for security.
        """

        self._print_debug(method, url, payload=json, headers=headers, params=params)
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=json,
                params=params,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - passthrough
            if self.debug:
                print(f"[DEBUG] Request failed: {exc}")
            raise

        self._log_response(response)
        return response

    # Internal helper methods
    def _print_debug(
        self,
        method: str,
        url: str,
        *,
        payload: Dict[str, Any] | None = None,
        headers: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
    ) -> None:
        """Output debug information for HTTP requests when debug mode is active.
        
        Logs the HTTP method, URL, and request details including headers,
        parameters, and payload while automatically masking sensitive values
        to prevent credential exposure in logs.
        """
        if not self.debug:
            return

        print(f"[DEBUG] {method.upper()} {url}")

        if params:
            print(f"[DEBUG] Params: {self._sanitize_for_debug(params)}")
        if payload:
            print(f"[DEBUG] Payload: {self._sanitize_for_debug(payload)}")
        if headers:
            print(f"[DEBUG] Headers: {self._sanitize_for_debug(headers)}")

    def _sanitize_for_debug(self, data: Any, *, key_hint: str = "") -> Any:
        """Recursively sanitize data structures by masking sensitive values.
        
        Walks through dictionaries, lists, and tuples to identify and mask
        sensitive information based on key names, ensuring debug output
        doesn't expose credentials or other sensitive data.
        """
        if isinstance(data, dict):
            return {
                key: self._sanitize_for_debug(value, key_hint=key)
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [self._sanitize_for_debug(item, key_hint=key_hint) for item in data]
        if isinstance(data, tuple):
            return tuple(self._sanitize_for_debug(item, key_hint=key_hint) for item in data)
        return self._mask_sensitive_value(key_hint, data)

    def _mask_sensitive_value(self, key: str, value: Any) -> Any:
        """Determine if a value should be masked based on its key name.
        
        Checks if the key contains sensitive terms like 'password', 'token',
        'secret', etc., and returns a masked version of the value to prevent
        sensitive data from appearing in debug logs.
        """
        if value is None:
            return value
        key_lower = (key or "").lower()
        if any(term in key_lower for term in self._SENSITIVE_TERMS):
            value_str = str(value)
            if len(value_str) > 10:
                return f"{value_str[:4]}...{value_str[-4:]}"
            return "***"
        return value

    def _log_response(self, response) -> None:  # pragma: no cover - console logging
        """Log HTTP response details with sensitive data masking.
        
        Outputs response status, headers, and body content when debug mode
        is enabled, with automatic sanitization of sensitive values in
        JSON responses to prevent credential leakage.
        """
        if not self.debug:
            return

        status_reason = getattr(response, "reason", "")
        print(f"[DEBUG] Response: {response.status_code} {status_reason}")

        content_type = ""
        try:
            content_type = response.headers.get("Content-Type", "")
        except AttributeError:
            pass

        if "json" in content_type:
            try:
                sanitized = self._sanitize_for_debug(response.json())
                print(f"[DEBUG] Response Body: {sanitized}")
                return
            except ValueError:
                pass

        try:
            text = response.text
        except AttributeError:
            text = None

        if text:
            preview = text if len(text) <= 500 else f"{text[:500]}..."
            print(f"[DEBUG] Response Body: {preview}")
