"""
Google OAuth authentication for accessing private YouTube playlists.
Handles OAuth flow and authenticated API requests.
"""

import logging
import json
import webbrowser
import signal
import urllib.request
import threading
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import get_settings
from .youtube_api import YouTubeAPI, YouTubeAPIError
from .oauth_client_config import OAuthClientConfig
from .oauth_security import (
    SecureTokenManager,
    OAuthSecurityValidator,
    generate_state_parameter,
)


logger = logging.getLogger(__name__)

# OAuth scopes for YouTube access
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


class YouTubeOAuth:
    """Handle Google OAuth authentication for YouTube API access."""

    def __init__(self):
        """Initialize OAuth handler."""
        self.settings = get_settings()
        self.credentials_file = Path("data/oauth_credentials.json")
        self.token_file = Path("data/oauth_token.json")
        self.secure_token_manager = SecureTokenManager()
        self.credentials: Optional[Credentials] = None
        self.service = None

    def setup_oauth(self) -> bool:
        """Set up OAuth credentials and perform authentication flow."""
        try:
            # Check if we have valid credentials
            if self._load_existing_credentials():
                logger.info("Using existing OAuth credentials")
                return True

            # Check if OAuth client config is available
            if not OAuthClientConfig.has_valid_config():
                print("\n❌ OAuth client configuration not found")
                print(OAuthClientConfig.get_setup_instructions())
                return False

            return self._perform_oauth_flow()

        except Exception as e:
            logger.error(f"OAuth setup failed: {e}")
            return False

    def _load_existing_credentials(self) -> bool:
        """Load existing OAuth credentials from secure storage."""
        try:
            # Try secure token manager first
            token_data = self.secure_token_manager.load_token()
            if token_data:
                self.credentials = Credentials.from_authorized_user_info(
                    token_data, SCOPES
                )
            elif self.token_file.exists():
                # Fall back to old token file and migrate
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), SCOPES
                )
                if self.credentials and self.credentials.valid:
                    # Migrate to secure storage
                    self._save_credentials()
                    # Remove old file
                    try:
                        self.token_file.unlink()
                    except:
                        pass
            else:
                return False

            if not self.credentials or not self.credentials.valid:
                if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
                ):
                    logger.info("Refreshing expired OAuth credentials")
                    try:
                        self.credentials.refresh(Request())
                        self._save_credentials()
                    except Exception as e:
                        logger.warning(f"Failed to refresh credentials: {e}")
                        return False
                else:
                    return False

            # Validate token security
            if self.credentials.valid:
                token_info = {
                    "access_token": self.credentials.token,
                    "refresh_token": self.credentials.refresh_token,
                    "expires_at": (
                        self.credentials.expiry.isoformat()
                        if self.credentials.expiry
                        else None
                    ),
                    "scopes": self.credentials.scopes or [],
                }

                security_issues = OAuthSecurityValidator.validate_token_security(
                    token_info
                )
                if security_issues:
                    logger.warning(f"Token security issues: {security_issues}")

            # Test the credentials
            self.service = build("youtube", "v3", credentials=self.credentials)
            return True

        except Exception as e:
            logger.warning(f"Error loading existing credentials: {e}")
            return False

    def _perform_oauth_flow(self) -> bool:
        """Perform OAuth authentication flow."""
        try:
            # Get client configuration
            client_config = OAuthClientConfig.get_client_config()

            if not client_config.get("client_id"):
                print("\n❌ OAuth client configuration is incomplete")
                print(OAuthClientConfig.get_setup_instructions())
                return False

            # Validate client configuration security
            security_issues = OAuthSecurityValidator.validate_client_config(
                client_config
            )
            if security_issues:
                logger.warning(
                    f"Client configuration security issues: {security_issues}"
                )
                for issue in security_issues[:3]:  # Show first 3 issues
                    print(f"⚠️  Security warning: {issue}")

            # Generate state parameter for CSRF protection
            state_param = generate_state_parameter()

            # Create client configuration for OAuth flow
            oauth_config = {
                "installed": {
                    "client_id": client_config["client_id"],
                    "client_secret": client_config["client_secret"],
                    "auth_uri": client_config["auth_uri"],
                    "token_uri": client_config["token_uri"],
                    "redirect_uris": client_config["redirect_uris"],
                }
            }

            # Save temporary client configuration
            temp_client_file = self.credentials_file.parent / "temp_oauth_config.json"
            temp_client_file.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_client_file, "w") as f:
                json.dump(oauth_config, f)

            try:
                # Perform OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(temp_client_file), SCOPES
                )
                flow.state = state_param  # Add CSRF protection

                print("\n🔐 Google OAuth Authentication Required")
                print("=" * 50)
                print(
                    "To access your private playlists, you need to sign in with Google."
                )
                print("Your browser will open for authentication...")
                print("After signing in, you can close the browser window.")
                print("\n⚠️  If you see a 'This app isn't verified' warning:")
                print("   Click 'Advanced' → 'Go to YT Music Manager CLI (unsafe)'")
                print("   This is normal for personal/development apps.")
                print("\n💡 Press Ctrl+C to cancel at any time.\n")

                # Use a more robust cancellation approach with threading
                # The OAuth flow blocks, so we run it in a thread and monitor for KeyboardInterrupt
                flow_result = {"credentials": None, "error": None, "cancelled": False}
                flow_thread = None

                # Helper: temporarily raise log level for noisy loggers and restore afterward
                class _TempLogLevels:
                    def __init__(self, names, level):
                        self.names = names
                        self.level = level
                        self.prev = {}

                    def __enter__(self):
                        for n in self.names:
                            lg = logging.getLogger(n)
                            self.prev[n] = lg.level
                            lg.setLevel(self.level)
                        return self

                    def __exit__(self, exc_type, exc, tb):
                        for n, lvl in self.prev.items():
                            logging.getLogger(n).setLevel(lvl)

                def run_oauth_flow():
                    try:
                        flow_result["credentials"] = flow.run_local_server(
                            port=8080,
                            prompt="consent",
                            authorization_prompt_message="Please visit this URL to authorize the application: {url}",
                            success_message="Authentication successful! You can close this window.",
                        )
                    except Exception as e:
                        flow_result["error"] = e

                flow_thread = threading.Thread(target=run_oauth_flow, daemon=True)
                flow_thread.start()

                # Wait for the thread to complete, but allow KeyboardInterrupt
                try:
                    while flow_thread.is_alive():
                        flow_thread.join(timeout=0.5)
                except KeyboardInterrupt:
                    flow_result["cancelled"] = True
                    # Use Rich console for colored output instead of raw ANSI
                    from rich.console import Console

                    console = Console()
                    console.print(
                        "\n[bold red]🚫 Authentication cancelled by user.[/bold red]"
                    )
                    # Try to stop the server by making a request
                    try:
                        with _TempLogLevels(
                            ["google_auth_oauthlib", "werkzeug"], logging.CRITICAL
                        ):
                            urllib.request.urlopen(
                                "http://localhost:8080/?error=user_cancelled", timeout=1
                            ).read()
                    except Exception:
                        pass
                    return False

                # Check results
                if flow_result["cancelled"]:
                    from rich.console import Console

                    console = Console()
                    console.print(
                        "\n[bold red]🚫 Authentication cancelled by user.[/bold red]"
                    )
                    return False

                if flow_result["error"]:
                    raise flow_result["error"]

                if not flow_result["credentials"]:
                    print("\n❌ Authentication failed - no credentials received")
                    return False

                self.credentials = flow_result["credentials"]

                # Save credentials
                self._save_credentials()

                # Create YouTube service
                self.service = build("youtube", "v3", credentials=self.credentials)

                print("\n✅ Authentication successful!")
                print("You can now access your private playlists.")

                return True

            finally:
                # Clean up temporary file
                if temp_client_file.exists():
                    temp_client_file.unlink()

        except Exception as e:
            # If the exception was due to a user-initiated cancel, provide a clean message
            if isinstance(e, KeyboardInterrupt):
                from rich.console import Console

                console = Console()
                console.print(
                    "\n[bold red]🚫 Authentication cancelled by user.[/bold red]"
                )
                # Suppress OAuth flow logging
                oauth_logger = logging.getLogger("google_auth_oauthlib")
                werkzeug_logger = logging.getLogger("werkzeug")
                oauth_logger.setLevel(logging.CRITICAL)
                werkzeug_logger.setLevel(logging.CRITICAL)
                return False
            logger.error(f"OAuth flow failed: {e}")
            print(f"\n❌ Authentication failed: {e}")
            print("\nTroubleshooting:")
            print("1. Check your internet connection")
            print("2. Ensure port 8080 is not blocked by firewall")
            print("3. Try running: ytmm auth mode auto_oauth")
            print("4. Contact support if the issue persists")
            return False

    def _save_credentials(self) -> None:
        """Save OAuth credentials to secure storage."""
        try:
            # Prepare token data
            token_data = {
                "access_token": self.credentials.token,
                "refresh_token": self.credentials.refresh_token,
                "token_uri": self.credentials.token_uri,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scopes": self.credentials.scopes,
                "expires_at": (
                    self.credentials.expiry.isoformat()
                    if self.credentials.expiry
                    else None
                ),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Save using secure token manager
            if self.secure_token_manager.save_token(token_data):
                logger.info("OAuth credentials saved securely")
            else:
                # Fall back to regular file storage
                self.token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_file, "w") as f:
                    f.write(self.credentials.to_json())
                logger.info("OAuth credentials saved to file")

        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")

    def get_authenticated_youtube_api(self) -> "YouTubeAPI":
        """Get a YouTubeAPI instance with OAuth authentication."""
        if not self.credentials or not self.service:
            raise YouTubeAPIError(
                "OAuth authentication not set up. Call setup_oauth() first."
            )

        # Create a custom YouTubeAPI instance that uses OAuth
        api = YouTubeAPI.__new__(YouTubeAPI)
        api.settings = self.settings
        api.api_key = None  # We're using OAuth, not API key
        api.service = self.service
        api.last_request_time = 0
        api.min_request_interval = 0.1
        api.quota_used = 0
        api.daily_quota_limit = 10000

        # Set cache attributes that are normally set in __init__
        from datetime import timedelta
        from pathlib import Path
        api.cache_dir = Path("data/cache")
        api.cache_dir.mkdir(parents=True, exist_ok=True)
        api.cache_ttl = timedelta(hours=1)  # Cache for 1 hour by default
        api.playlist_cache_ttl = timedelta(hours=6)  # Playlists change less frequently

        return api

    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """Get user's own playlists."""
        if not self.service:
            raise YouTubeAPIError("Not authenticated")

        try:
            request = self.service.playlists().list(
                part="snippet,contentDetails", mine=True, maxResults=50
            )

            response = request.execute()
            return response.get("items", [])

        except HttpError as e:
            raise YouTubeAPIError(f"Error fetching user playlists: {e}")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.credentials is not None and self.credentials.valid

    def revoke_authentication(self) -> bool:
        """Revoke OAuth authentication and delete stored credentials."""
        try:
            if self.credentials:
                # Revoke the credentials with Google
                try:
                    self.credentials.revoke(Request())
                except Exception as e:
                    logger.warning(f"Failed to revoke credentials with Google: {e}")

            # Delete stored credentials securely
            self.secure_token_manager.delete_token()

            # Also remove old token file if it exists
            if self.token_file.exists():
                self.token_file.unlink()

            if self.credentials_file.exists():
                self.credentials_file.unlink()

            self.credentials = None
            self.service = None

            print("✅ Authentication revoked successfully")
            return True

        except Exception as e:
            logger.error(f"Error revoking authentication: {e}")
            print(f"❌ Error revoking authentication: {e}")
            return False

    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status information."""
        if not self.is_authenticated():
            return {
                "authenticated": False,
                "method": "oauth",
                "user_email": None,
                "expires_at": None,
            }

        # Try to get user info
        user_email = None
        try:
            # This would require additional scopes, so we'll skip it for now
            pass
        except Exception:
            pass

        expires_at = None
        if self.credentials.expiry:
            expires_at = self.credentials.expiry.isoformat()

        return {
            "authenticated": True,
            "method": "oauth",
            "user_email": user_email,
            "expires_at": expires_at,
        }


def setup_oauth_instructions() -> str:
    """Get instructions for setting up OAuth."""
    return """🔧 Setting up Google OAuth for Private Playlists

To access your private playlists, you need to set up Google OAuth:

METHOD 1: Quick Setup (Recommended)
   1. Run: ytmm auth mode auto_oauth
   2. Follow the prompts to log in

METHOD 2: Manual Setup
   1. Go to Google Cloud Console (https://console.cloud.google.com/)
   2. Create a new project or select an existing one
   3. Enable the YouTube Data API v3
   4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   5. Choose "Desktop application"
   6. Copy the client_id and client_secret
   7. Run: ytmm auth mode manual_oauth


Alternative: Use 'no_auth' mode for public playlists only:
   Run: ytmm auth mode no_auth
"""
