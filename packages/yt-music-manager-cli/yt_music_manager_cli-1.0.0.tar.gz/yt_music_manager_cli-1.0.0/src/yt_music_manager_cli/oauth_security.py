"""
Security utilities for OAuth token management and protection.
"""

import os
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform


class SecureTokenManager:
    """Secure token storage and management."""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data")
        self.token_file = self.data_dir / "oauth_token_secure.json"
        self.key_file = self.data_dir / ".key_store"
        self._encryption_key = None

    def _get_machine_id(self) -> str:
        """Get a machine-specific identifier for key derivation."""
        try:
            # Use various machine-specific information
            machine_info = [
                platform.node(),  # hostname
                platform.machine(),  # architecture
                platform.platform(),  # platform info
            ]

            # Add MAC address if available
            try:
                import uuid

                machine_info.append(str(uuid.getnode()))
            except:
                pass

            # Create a hash of all machine info
            combined = "|".join(machine_info).encode("utf-8")
            return hashlib.sha256(combined).hexdigest()[:32]
        except:
            # Fallback to a static value (less secure but works)
            return "yt_music_manager_cli_default_key_2024"

    def _derive_key(self, password: str = None) -> bytes:
        """Derive encryption key from machine info and optional password."""
        if password is None:
            password = self._get_machine_id()

        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"yt_music_manager_cli_salt_2024",  # Fixed salt for consistency
            iterations=100000,
        )

        return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        if self._encryption_key is None:
            self._encryption_key = self._derive_key()
        return self._encryption_key

    def save_token(self, token_data: Dict[str, Any]) -> bool:
        """Save OAuth token with encryption."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Encrypt the token data
            fernet = Fernet(self._get_encryption_key())
            token_json = json.dumps(token_data)
            encrypted_data = fernet.encrypt(token_json.encode("utf-8"))

            # Add metadata
            secure_data = {
                "version": 1,
                "encrypted_token": base64.b64encode(encrypted_data).decode("utf-8"),
                "created_at": token_data.get("created_at"),
                "expires_at": token_data.get("expires_at"),
            }

            # Save to file with restricted permissions
            with open(self.token_file, "w") as f:
                json.dump(secure_data, f, indent=2)

            # Set file permissions (owner read/write only)
            try:
                os.chmod(self.token_file, 0o600)
            except:
                pass  # Windows doesn't support chmod

            return True

        except Exception as e:
            print(f"Error saving secure token: {e}")
            return False

    def load_token(self) -> Optional[Dict[str, Any]]:
        """Load and decrypt OAuth token."""
        try:
            if not self.token_file.exists():
                return None

            with open(self.token_file, "r") as f:
                secure_data = json.load(f)

            # Check version
            if secure_data.get("version") != 1:
                return None

            # Decrypt token data
            fernet = Fernet(self._get_encryption_key())
            encrypted_data = base64.b64decode(secure_data["encrypted_token"])
            decrypted_json = fernet.decrypt(encrypted_data).decode("utf-8")

            return json.loads(decrypted_json)

        except Exception as e:
            print(f"Error loading secure token: {e}")
            return None

    def delete_token(self) -> bool:
        """Securely delete stored token."""
        try:
            if self.token_file.exists():
                # Overwrite file with random data before deletion
                file_size = self.token_file.stat().st_size
                with open(self.token_file, "wb") as f:
                    f.write(secrets.token_bytes(file_size))

                self.token_file.unlink()

            return True
        except Exception as e:
            print(f"Error deleting secure token: {e}")
            return False

    def token_exists(self) -> bool:
        """Check if token file exists."""
        return self.token_file.exists()


class OAuthSecurityValidator:
    """Validates OAuth security requirements and best practices."""

    @staticmethod
    def validate_client_config(client_config: Dict[str, str]) -> Dict[str, str]:
        """Validate OAuth client configuration for security issues."""
        issues = []

        # Check client ID format (should look like a Google client ID)
        client_id = client_config.get("client_id", "")
        if client_id and not client_id.endswith(".apps.googleusercontent.com"):
            issues.append(
                "Client ID doesn't appear to be a valid Google OAuth client ID"
            )

        # Check redirect URIs
        redirect_uris = client_config.get("redirect_uris", [])
        if not redirect_uris:
            issues.append("No redirect URIs specified")
        else:
            for uri in redirect_uris:
                if not uri.startswith("http://localhost:") and not uri.startswith(
                    "https://"
                ):
                    issues.append(f"Insecure redirect URI: {uri}")

        # Check for development/testing indicators
        if "test" in client_id.lower() or "dev" in client_id.lower():
            issues.append("Client ID appears to be for development/testing only")

        return issues

    @staticmethod
    def validate_token_security(token_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate OAuth token for security issues."""
        issues = []

        # Check token expiration
        if "expires_at" in token_data:
            try:
                from datetime import datetime

                expires_at = datetime.fromisoformat(
                    token_data["expires_at"].replace("Z", "+00:00")
                )
                if expires_at < datetime.now():
                    issues.append("Token has expired")
            except:
                issues.append("Invalid token expiration format")

        # Check for refresh token
        if not token_data.get("refresh_token"):
            issues.append("No refresh token available (token cannot be renewed)")

        # Check scopes
        scopes = token_data.get("scopes", [])
        required_scopes = [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]

        for required_scope in required_scopes:
            if required_scope not in scopes:
                issues.append(f"Missing required scope: {required_scope}")

        return issues


def create_secure_data_directory() -> Path:
    """Create secure data directory with appropriate permissions."""
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Set directory permissions (owner access only)
    try:
        os.chmod(data_dir, 0o700)
    except:
        pass  # Windows doesn't support chmod

    return data_dir


def generate_state_parameter() -> str:
    """Generate a secure state parameter for OAuth flow."""
    return secrets.token_urlsafe(32)


def validate_state_parameter(received_state: str, expected_state: str) -> bool:
    """Validate OAuth state parameter to prevent CSRF attacks."""
    return secrets.compare_digest(received_state, expected_state)
