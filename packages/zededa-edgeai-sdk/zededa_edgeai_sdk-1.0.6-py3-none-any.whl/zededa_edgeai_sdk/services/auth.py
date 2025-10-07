"""OAuth authentication service using browser-based flows.

Manages the complete OAuth authentication process including callback
server setup, browser interaction, and token exchange.
"""

from __future__ import annotations

import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

__all__ = ["AuthService"]


class AuthService:
    """OAuth authentication service for browser-based login flows.
    
    Manages the complete OAuth authentication process including starting
    a local callback server, opening the browser for user authentication,
    handling the OAuth callback, and extracting authentication tokens.
    """

    def __init__(self, backend_url: str, ui_url: str, *,
                 debug: bool = False) -> None:
        """Initialize OAuth authentication service with endpoint URLs.
        
        Configures the service with backend API URL for authentication
        and UI URL for browser redirects, with optional debug logging
        for troubleshooting OAuth flow issues.
        """
        self.backend_url = backend_url.rstrip("/")
        self.ui_url = ui_url.rstrip("/")
        self.debug = debug
        self.oauth_result: Optional[dict] = None
        self.oauth_server: Optional[HTTPServer] = None

    def oauth_login(self, catalog_id: str | None = None) -> Optional[str]:
        """Execute complete OAuth login flow with browser interaction.
        
        Starts a local HTTP server for OAuth callbacks, opens the user's browser
        for authentication, waits for the callback with authentication tokens,
        and returns the JWT token for further API calls.
        """
        if catalog_id:
            print(f"Authenticating for catalog: {catalog_id}")
        else:
            print("Authenticating without catalog scope...")

        try:
            callback_port = self._find_available_port(start_port=8765)
            callback_url = f"http://localhost:{callback_port}/callback"
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return None

        print(f"Starting OAuth callback server on port {callback_port}...")

        server_address = ("localhost", callback_port)

        service = self

        class OAuthHandler(BaseHTTPRequestHandler):  # pragma: no cover
            def __init__(self, *_args, **_kwargs):
                """Initialize OAuth callback handler with reference to parent service.
                
                Sets up the HTTP request handler with access to the AuthService
                instance to store authentication results from OAuth callbacks.
                """
                self.service = service
                super().__init__(*_args, **_kwargs)

            def do_GET(self):
                """Process OAuth callback requests from the browser.
                
                Handles the OAuth redirect callback by parsing query parameters
                for authentication tokens or error messages, stores the results
                in the service instance, and sends appropriate HTML responses.
                """
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)

                if parsed_url.path == "/callback":
                    if "jwt" in query_params:
                        backend_jwt = query_params["jwt"][0]
                        self.service.oauth_result = {
                            "success": True, "jwt": backend_jwt
                        }
                        self._respond(self._success_html())
                    elif "error" in query_params:
                        error_msg = self.service._render_error_message(
                            query_params
                        )
                        self.service.oauth_result = {
                            "success": False, "error": error_msg
                        }
                        self._respond(self._error_html(error_msg), status=400)
                    else:
                        error_msg = (
                            "Authentication process was interrupted. "
                            "Please try again."
                        )
                        self.service.oauth_result = {
                            "success": False, "error": error_msg
                        }
                        self._respond(self._generic_error_html(error_msg),
                                    status=400)

            def _respond(self, html: str, *, status: int = 200):
                """Send HTML response to the browser with appropriate headers.
                
                Encodes the HTML content, sets proper content type and length
                headers, and sends the response back to complete the OAuth
                callback interaction.
                """
                payload = html.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def _success_html(self) -> str:  # noqa: D401 - HTML content helper
                return """<!DOCTYPE html>
<html>
<head>
    <title>Authentication Successful - Zededa EdgeAI</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 0;
            background: #F3F3F3;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 8px;
            border: 1px solid #C9C7C7;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 40px;
            text-align: center;
            max-width: 500px;
            margin: 20px;
            position: relative;
        }
        .logo {
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: #25232B;
            background: #F3F3F3;
            border-radius: 4px;
            border: 1px solid #C9C7C7;
        }
        h1 {
            color: #25232B;
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
        }
        .subtitle {
            color: #666;
            margin: 0 0 20px 0;
            font-size: 14px;
            font-weight: 500;
        }
        .success-icon {
            font-size: 48px;
            color: #28a745;
            margin-bottom: 20px;
            animation: checkmark 0.6s ease-in-out;
        }
        @keyframes checkmark {
            0% { transform: scale(0) rotate(-180deg); opacity: 0; }
            50% { transform: scale(1.2) rotate(-90deg); opacity: 0.8; }
            100% { transform: scale(1) rotate(0deg); opacity: 1; }
        }
        .message {
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
            font-size: 16px;
        }
        .close-instruction {
            background: #F8F9FA;
            border: 1px solid #C9C7C7;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            color: #495057;
            font-size: 14px;
        }
        .close-instruction strong {
            color: #ff5000;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #C9C7C7;
            color: #6c757d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Zededa</div>
        <div class="success-icon">✓</div>
        <h1>Authentication Successful</h1>
        <div class="subtitle">Zededa EdgeAI</div>
        <div class="message">
            <p>You have been successfully authenticated to the Zededa EdgeAI platform.</p>
            <p>Your session is now active and you can return to your terminal to continue working.</p>
        </div>
        <div class="close-instruction">
            <strong>You can now safely close this browser tab.</strong><br>
            Your authentication credentials have been securely transferred to your terminal session.
        </div>
        <div class="footer">
            Zededa EdgeAI SDK • Secure Authentication Complete
        </div>
    </div>
</body>
</html>"""

            def _error_html(self, error_msg: str) -> str:  # noqa: D401 - HTML helper
                return f"""<!DOCTYPE html>
<html>
<head>
    <title>Authentication Failed - Zededa EdgeAI</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 0;
            background: #F3F3F3;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            border: 1px solid #C9C7C7;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 40px;
            text-align: center;
            max-width: 500px;
            margin: 20px;
            position: relative;
        }}
        .logo {{
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: #25232B;
            background: #F3F3F3;
            border-radius: 4px;
            border: 1px solid #C9C7C7;
        }}
        h1 {{
            color: #25232B;
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .subtitle {{
            color: #666;
            margin: 0 0 20px 0;
            font-size: 14px;
            font-weight: 500;
        }}
        .error-icon {{
            font-size: 48px;
            color: #dc3545;
            margin-bottom: 20px;
        }}
        .message {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
            font-size: 16px;
        }}
        .error-details {{
            background: #FFF5F5;
            border: 1px solid #FED7D7;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            color: #C53030;
            font-size: 14px;
            text-align: left;
        }}
        .error-details strong {{
            color: #dc3545;
        }}
        .close-instruction {{
            background: #F8F9FA;
            border: 1px solid #C9C7C7;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            color: #495057;
            font-size: 14px;
        }}
        .close-instruction strong {{
            color: #ff5000;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #C9C7C7;
            color: #6c757d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Zededa</div>
        <div class="error-icon">✕</div>
        <h1>Authentication Failed</h1>
        <div class="subtitle">Zededa EdgeAI</div>
        <div class="message">
            <p>We were unable to authenticate you with the Zededa EdgeAI platform.</p>
            <p>Please check your credentials and try again.</p>
        </div>
        <div class="error-details">
            <strong>Error Details:</strong><br>
            {error_msg}
        </div>
        <div class="close-instruction">
            <strong>You can now close this browser tab.</strong><br>
            Please try the authentication process again from your terminal.
        </div>
        <div class="footer">
            Zededa EdgeAI SDK • Authentication Error
        </div>
    </div>
</body>
</html>"""

            def _generic_error_html(self, error_msg: str) -> str:  # noqa: D401
                return f"""<!DOCTYPE html>
<html>
<head>
    <title>Authentication Error - Zededa EdgeAI</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 0;
            background: #F3F3F3;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            border: 1px solid #C9C7C7;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 40px;
            text-align: center;
            max-width: 500px;
            margin: 20px;
            position: relative;
        }}
        .logo {{
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: #25232B;
            background: #F3F3F3;
            border-radius: 4px;
            border: 1px solid #C9C7C7;
        }}
        h1 {{
            color: #25232B;
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .subtitle {{
            color: #666;
            margin: 0 0 20px 0;
            font-size: 14px;
            font-weight: 500;
        }}
        .error-icon {{
            font-size: 48px;
            color: #dc3545;
            margin-bottom: 20px;
        }}
        .message {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
            font-size: 16px;
        }}
        .error-details {{
            background: #FFF5F5;
            border: 1px solid #FED7D7;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            color: #C53030;
            font-size: 14px;
            text-align: left;
        }}
        .error-details strong {{
            color: #dc3545;
        }}
        .close-instruction {{
            background: #F8F9FA;
            border: 1px solid #C9C7C7;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            color: #495057;
            font-size: 14px;
        }}
        .close-instruction strong {{
            color: #ff5000;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #C9C7C7;
            color: #6c757d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Zededa</div>
        <div class="error-icon">⚠</div>
        <h1>Authentication Error</h1>
        <div class="subtitle">Zededa EdgeAI</div>
        <div class="message">
            <p>The authentication process encountered an unexpected issue.</p>
            <p>Please return to your terminal and try the authentication process again.</p>
        </div>
        <div class="error-details">
            <strong>Error Details:</strong><br>
            {error_msg}
        </div>
        <div class="close-instruction">
            <strong>You can now close this browser tab.</strong><br>
            Please try the authentication process again from your terminal.
        </div>
        <div class="footer">
            Zededa EdgeAI SDK • Authentication Error
        </div>
    </div>
</body>
</html>"""

            def log_message(self, _format, *_args):  # pragma: no cover - silence server logs
                return

        try:
            self.oauth_server = HTTPServer(server_address, OAuthHandler)
        except OSError as exc:
            print(f"[ERROR] Failed to create OAuth callback server on port {callback_port}: {exc}")
            print("[ERROR] This might be a race condition. Please try again.")
            return None

        server_thread = threading.Thread(
            target=self.oauth_server.serve_forever
        )
        server_thread.daemon = True
        server_thread.start()

        auth_url = f"{self.ui_url}/auth?redirect_uri={callback_url}"
        if catalog_id:
            auth_url += f"&catalog_id={catalog_id}"

        print("\nOpening browser for authentication...")
        print(f"URL: {auth_url}")
        print("\nIf the browser doesn't open automatically, copy and paste "
              "the URL above.")

        try:
            webbrowser.open(auth_url)
        except Exception as exc:  # pragma: no cover - platform dependent
            print(f"Failed to open browser automatically: {exc}")

        print("\nWaiting for authentication...")

        while self.oauth_result is None:
            time.sleep(0.5)

        if self.oauth_result and self.oauth_result.get("success"):
            backend_jwt = self.oauth_result.get("jwt")
            if backend_jwt:
                print("Authentication successful!")
                return backend_jwt
            print("Authentication failed: No JWT received")
            return None

        error_msg = (
            self.oauth_result.get("error", "Unknown error")
            if self.oauth_result else "Unknown error"
        )
        print(f"Authentication failed: {error_msg}")
        return None

    # Internal helper methods
    def _find_available_port(self, start_port: int = 8765,
                           max_attempts: int = 100) -> int:
        """Locate an available port for the OAuth callback server.
        
        Attempts to bind to ports starting from start_port, incrementing
        until an available port is found. Raises RuntimeError if no
        available port is found within the attempt limit.
        """
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(("localhost", port))
                    return port
            except OSError:
                continue
        raise RuntimeError(
            f"Could not find an available port in range "
            f"{start_port}-{start_port + max_attempts - 1}"
        )

    def _render_error_message(self, query_params: dict) -> str:
        """Convert OAuth callback error parameters into user-friendly messages.
        
        Processes error codes and descriptions from OAuth callbacks to generate
        clear, actionable error messages for users, handling common error
        scenarios and providing appropriate guidance.
        """
        error_param = (query_params.get("error", [""]) or [""])[0]
        error_description = (
            (query_params.get("error_description", [""]) or [""])[0]
        )

        if error_param and error_param.strip():
            normalized_error = error_param.lower()
            if "cannot read properties" in normalized_error or "reading" in normalized_error:
                error_msg = "Authentication failed. Please check your credentials and try again."
            elif "session" in normalized_error:
                error_msg = "Session error occurred. Please try logging in again."
            elif "network" in normalized_error or "connection" in normalized_error:
                error_msg = "Network error. Please check your internet connection and try again."
            elif "timeout" in normalized_error:
                error_msg = "Request timed out. Please try again."
            elif "forbidden" in normalized_error or "403" in error_param:
                error_msg = "Access denied. You don't have permission to access this catalog."
            elif "unauthorized" in normalized_error or "401" in error_param:
                error_msg = "Authentication failed. Please check your credentials and try again."
            elif "access" in normalized_error and "denied" in normalized_error:
                error_msg = "Access denied. You don't have permission to access this catalog."
            else:
                error_msg = error_param

            if error_description and error_description.strip() and len(error_description) < 100:
                technical_terms = ["cannot read", "undefined", "null", "stack", "trace", "error code"]
                if not any(term in error_description.lower() for term in technical_terms):
                    error_msg += f": {error_description}"
            return error_msg

        error_code = (query_params.get("code", [""]) or [""])[0]
        if error_code:
            normalized_code = error_code.lower()
            if error_code == "403" or "forbidden" in normalized_code:
                return "Access denied. You don't have permission to access this catalog."
            if error_code == "401" or "unauthorized" in normalized_code:
                return "Authentication failed. Please check your credentials and try again."
            return f"Authentication failed (Error code: {error_code}). Please try again."

        return "Authentication failed. Please check your credentials and try again."
