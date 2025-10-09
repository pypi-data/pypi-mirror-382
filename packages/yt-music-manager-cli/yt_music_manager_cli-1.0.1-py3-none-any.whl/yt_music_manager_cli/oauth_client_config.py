"""
OAuth client configuration for public distribution.
Handles secure credential distribution without hardcoding secrets.
"""

import json
import base64
from pathlib import Path
from typing import Dict, Optional

try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as resources


class OAuthClientConfig:
    """Manages OAuth client configuration for public distribution."""

    # Default OAuth client configuration for public app
    # Note: For desktop apps, the client secret provides minimal security
    # The real security comes from Google's OAuth flow itself
    _DEFAULT_CLIENT_CONFIG = {
        "client_id": "",  # Will be set during app build/packaging
        "client_secret": "",  # Will be set during app build/packaging
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8080"],
    }

    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """Get OAuth client configuration."""
        # Try to load from bundled config first
        try:
            config = cls._load_bundled_config()
            if config and config.get("client_id"):
                return config
        except Exception:
            pass

        # Fall back to user configuration
        try:
            config = cls._load_user_config()
            if config and config.get("client_id"):
                return config
        except Exception:
            pass

        # Return empty config (user needs to configure manually)
        return cls._DEFAULT_CLIENT_CONFIG.copy()

    @classmethod
    def _load_bundled_config(cls) -> Optional[Dict[str, str]]:
        """Load OAuth config bundled with the application."""
        try:
            # Try to load from package data using importlib.resources
            try:
                import yt_music_manager_cli.data

                with resources.open_text(
                    yt_music_manager_cli.data, "oauth_client_bundled.json"
                ) as f:
                    return json.load(f)
            except (FileNotFoundError, ModuleNotFoundError):
                # Try direct file path as fallback
                bundle_path = (
                    Path(__file__).parent / "data" / "oauth_client_bundled.json"
                )
                if bundle_path.exists():
                    with open(bundle_path, "r") as f:
                        return json.load(f)
                return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    @classmethod
    def _load_user_config(cls) -> Optional[Dict[str, str]]:
        """Load OAuth config from user's data directory."""
        try:
            config_path = Path("data/oauth_client.json")
            if config_path.exists():
                with open(config_path, "r") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    @classmethod
    def has_valid_config(cls) -> bool:
        """Check if valid OAuth configuration is available."""
        config = cls.get_client_config()
        return bool(config.get("client_id") and config.get("client_secret"))

    @classmethod
    def save_user_config(cls, client_id: str, client_secret: str) -> bool:
        """Save OAuth configuration to user's data directory."""
        try:
            config_path = Path("data/oauth_client.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            config = {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080"],
            }

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception:
            return False

    @classmethod
    def remove_user_config(cls) -> bool:
        """Remove OAuth configuration from user's data directory."""
        try:
            config_path = Path("data/oauth_client.json")
            if config_path.exists():
                config_path.unlink()
            return True
        except Exception:
            return False

    @classmethod
    def get_setup_instructions(cls) -> str:
        """Get instructions for OAuth setup."""
        return """
🔧 OAuth Configuration Required

To enable Google authentication, you need to set up OAuth credentials:

OPTION 1: Use built-in configuration (recommended for most users)
   • The app should work out of the box after installation
   • If you see this message, please report it as an issue

OPTION 2: Use your own Google Cloud Project (advanced users)
   1. Go to Google Cloud Console (https://console.cloud.google.com)
   2. Create a project and enable YouTube Data API v3
   3. Create OAuth 2.0 credentials (Desktop application)
   4. Run: ytmm auth mode manual_oauth
   5. Enter your client ID and secret

OPTION 3: Use configuration file
   • Save your OAuth client configuration as 'data/oauth_client.json'
   • Format: {"client_id": "...", "client_secret": "...", ...}

After setup, run: ytmm auth mode auto_oauth
"""


def create_oauth_client_template():
    """Create a template OAuth client configuration file."""
    template_path = Path("data/oauth_client_template.json")
    template_path.parent.mkdir(parents=True, exist_ok=True)

    template = {
        "_comment": "OAuth 2.0 Client Configuration Template",
        "_instructions": [
            "1. Go to Google Cloud Console",
            "2. Create a project and enable YouTube Data API v3",
            "3. Create OAuth 2.0 credentials (Desktop application)",
            "4. Copy client_id and client_secret below",
            "5. Rename this file to 'oauth_client.json'",
        ],
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8080"],
    }

    with open(template_path, "w") as f:
        json.dump(template, f, indent=2)

    return template_path
