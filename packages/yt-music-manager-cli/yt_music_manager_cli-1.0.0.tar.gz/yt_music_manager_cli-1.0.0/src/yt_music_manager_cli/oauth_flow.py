"""
Enhanced OAuth flow with improved user experience and error handling.
"""

import time
import socket
import webbrowser
from typing import Optional, Dict, Any
from urllib.parse import parse_qs, urlparse
import http.server
import socketserver
from threading import Thread, Event


class OAuthServerHandler(http.server.BaseHTTPRequestHandler):
    """Custom handler for OAuth callback server."""

    def __init__(self, *args, auth_code_event=None, auth_result=None, **kwargs):
        self.auth_code_event = auth_code_event
        self.auth_result = auth_result
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle OAuth callback GET request."""
        try:
            # Parse the authorization code from callback URL
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)

            if "code" in query_params:
                auth_code = query_params["code"][0]
                self.auth_result["code"] = auth_code
                self.auth_result["success"] = True

                # Send success response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>YT Music Manager CLI (YTMM CLI) - Authentication Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: #4CAF50; font-size: 24px; margin-bottom: 20px; }
                        .info { color: #666; font-size: 16px; }
                    </style>
                </head>
                <body>
                    <div class="success">✅ Authentication Successful!</div>
                    <div class="info">
                        <p>You have successfully signed in to YT Music Manager CLI (YTMM CLI).</p>
                        <p>You can now close this window and return to the application.</p>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(success_html.encode("utf-8"))

            elif "error" in query_params:
                error = query_params["error"][0]
                error_description = query_params.get(
                    "error_description", ["Unknown error"]
                )[0]

                self.auth_result["error"] = error
                self.auth_result["error_description"] = error_description
                self.auth_result["success"] = False

                # Send error response
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>YT Music Manager CLI (YTMM CLI) - Authentication Failed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .error {{ color: #f44336; font-size: 24px; margin-bottom: 20px; }}
                        .info {{ color: #666; font-size: 16px; }}
                    </style>
                </head>
                <body>
                    <div class="error">❌ Authentication Failed</div>
                    <div class="info">
                        <p>Error: {error}</p>
                        <p>Description: {error_description}</p>
                        <p>Please close this window and try again.</p>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(error_html.encode("utf-8"))

            # Signal that we received a callback
            if self.auth_code_event:
                self.auth_code_event.set()

        except Exception as e:
            print(f"Error handling OAuth callback: {e}")

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass


class EnhancedOAuthFlow:
    """Enhanced OAuth flow with better UX and error handling."""

    def __init__(self, port: int = 8080):
        self.port = port
        self.auth_result = {"success": False}
        self.auth_code_event = Event()

    def find_available_port(
        self, start_port: int = 8080, max_attempts: int = 10
    ) -> Optional[int]:
        """Find an available port for the OAuth callback server."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    return port
            except OSError:
                continue
        return None

    def start_callback_server(self, port: int) -> Optional[Thread]:
        """Start the OAuth callback server."""
        try:
            # Create handler with access to auth_result
            def handler_factory(*args, **kwargs):
                return OAuthServerHandler(
                    *args,
                    auth_code_event=self.auth_code_event,
                    auth_result=self.auth_result,
                    **kwargs,
                )

            httpd = socketserver.TCPServer(("localhost", port), handler_factory)

            def serve():
                httpd.serve_forever()

            server_thread = Thread(target=serve, daemon=True)
            server_thread.start()

            # Store server reference for cleanup
            self._httpd = httpd

            return server_thread

        except Exception as e:
            print(f"Failed to start callback server: {e}")
            return None

    def open_auth_url(self, auth_url: str) -> bool:
        """Open authentication URL in user's browser."""
        try:
            print(f"\n🌐 Opening authentication URL in your browser...")
            print(f"If the browser doesn't open automatically, visit:")
            print(f"{auth_url}\n")

            return webbrowser.open(auth_url)
        except Exception as e:
            print(f"Could not open browser: {e}")
            print(f"Please manually open: {auth_url}")
            return False

    def wait_for_callback(self, timeout: int = 300) -> Dict[str, Any]:
        """Wait for OAuth callback with timeout."""
        print("⏳ Waiting for authentication...")
        print("Please complete the sign-in process in your browser.")

        success = self.auth_code_event.wait(timeout)

        if success:
            return self.auth_result
        else:
            return {
                "success": False,
                "error": "timeout",
                "error_description": f"Authentication timed out after {timeout} seconds",
            }

    def cleanup(self):
        """Clean up OAuth flow resources."""
        try:
            if hasattr(self, "_httpd"):
                self._httpd.shutdown()
                self._httpd.server_close()
        except Exception as e:
            print(f"Warning: Failed to cleanup OAuth server: {e}")


def get_user_friendly_error_message(error: str, error_description: str = None) -> str:
    """Convert OAuth errors to user-friendly messages."""
    error_messages = {
        "access_denied": "You declined to authorize the application. Please try again and click 'Allow' to continue.",
        "invalid_request": "There was an issue with the authentication request. Please try again.",
        "invalid_client": "The application credentials are incorrect. Please check your OAuth configuration.",
        "invalid_grant": "The authorization code is invalid or expired. Please try signing in again.",
        "unsupported_response_type": "Authentication configuration error. Please report this issue.",
        "timeout": "Authentication timed out. Please try again and complete the process more quickly.",
    }

    user_message = error_messages.get(error, f"Authentication error: {error}")

    if error_description and error not in error_messages:
        user_message += f" ({error_description})"

    return user_message
