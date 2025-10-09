"""
Configuration management for YT Music Manager CLI (YTMM CLI).
Handles settings, validation, and environment setup.
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeConfig(BaseModel):
    """YouTube API configuration."""

    auth_method: str = Field(
        "no_auth",
        description="Authentication method: 'no_auth', 'auto_oauth', or 'manual_oauth'",
    )
    oauth_client_id: str = Field(
        "", description="OAuth client ID for Google authentication (manual_oauth only)"
    )
    oauth_client_secret: str = Field(
        "",
        description="OAuth client secret for Google authentication (manual_oauth only)",
    )

    @field_validator("auth_method")
    def validate_auth_method(cls, v):
        allowed_methods = ["no_auth", "auto_oauth", "manual_oauth"]
        if v not in allowed_methods:
            raise ValueError(
                f"Auth method must be one of: {', '.join(allowed_methods)}"
            )
        return v

    @field_validator("oauth_client_id")
    def trim_oauth_client_id(cls, v):  # Just trim; cross-field validation handled later
        return v.strip() if v else ""

    @field_validator("oauth_client_secret")
    def trim_oauth_client_secret(cls, v):
        return v.strip() if v else ""

    @model_validator(mode="after")
    def validate_manual_oauth(self):
        if self.auth_method == "manual_oauth":
            if not self.oauth_client_id:
                raise ValueError(
                    "OAuth client ID is required when using 'manual_oauth' authentication"
                )
            if not self.oauth_client_secret:
                raise ValueError(
                    "OAuth client secret is required when using 'manual_oauth' authentication"
                )
        return self


class DownloadConfig(BaseModel):
    """Download settings configuration."""

    base_path: str = Field(
        "~/Music/YouTube Playlists", description="Base download directory"
    )
    audio_format: str = Field("mp3", description="Output audio format")
    audio_quality: int = Field(320, description="Audio quality in kbps")
    naming_template: str = Field("%(title)s.%(ext)s", description="File naming pattern")

    @property
    def output_dir(self) -> str:
        """Backward-compatible alias expected by other modules."""
        return self.base_path

    @field_validator("base_path")
    def expand_path(cls, v):
        return str(Path(v).expanduser().resolve())

    @field_validator("audio_format")
    def validate_format(cls, v):
        allowed_formats = ["mp3", "aac", "ogg", "wav", "flac"]
        if v.lower() not in allowed_formats:
            raise ValueError(
                f"Audio format must be one of: {', '.join(allowed_formats)}"
            )
        return v.lower()

    @field_validator("audio_quality")
    def validate_quality(cls, v):
        if v < 64 or v > 320:
            raise ValueError("Audio quality must be between 64 and 320 kbps")
        return v


class SyncConfig(BaseModel):
    """Synchronization settings."""

    auto_sync_interval: int = Field(3600, description="Auto-sync interval in seconds")
    max_concurrent_downloads: int = Field(3, description="Maximum parallel downloads")
    check_for_updates_on_start: bool = Field(
        True, description="Check for updates on startup"
    )
    preserve_deleted_locally: bool = Field(
        False, description="Keep locally deleted files"
    )

    @field_validator("auto_sync_interval")
    def validate_interval(cls, v):
        if v < 300:  # Minimum 5 minutes
            raise ValueError(
                "Auto-sync interval must be at least 300 seconds (5 minutes)"
            )
        return v

    @field_validator("max_concurrent_downloads")
    def validate_concurrent(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Max concurrent downloads must be between 1 and 10")
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field("INFO", description="Logging level")
    log_file: str = Field("logs/yt_music_manager_cli.log", description="Log file path")
    max_log_size: str = Field("10MB", description="Maximum log file size")
    backup_count: int = Field(5, description="Number of log files to keep")

    @field_validator("level")
    def validate_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {', '.join(allowed_levels)}")
        return v.upper()

    @field_validator("backup_count")
    def validate_backup_count(cls, v):
        if v < 1 or v > 20:
            raise ValueError("Backup count must be between 1 and 20")
        return v


class AdvancedConfig(BaseModel):
    """Advanced settings."""

    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(5, description="Delay between retries in seconds")
    connection_timeout: int = Field(30, description="Network timeout in seconds")
    user_agent: str = Field(
        "yt-music-manager-cli/1.0.2", description="User agent for requests"
    )

    @field_validator("retry_attempts")
    def validate_retries(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Retry attempts must be between 1 and 10")
        return v

    @field_validator("retry_delay")
    def validate_delay(cls, v):
        if v < 1 or v > 60:
            raise ValueError("Retry delay must be between 1 and 60 seconds")
        return v

    @field_validator("connection_timeout")
    def validate_timeout(cls, v):
        if v < 5 or v > 300:
            raise ValueError("Connection timeout must be between 5 and 300 seconds")
        return v


class Settings(BaseSettings):
    """Main settings class that combines all configuration sections."""

    youtube: YouTubeConfig = Field(default_factory=YouTubeConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)

    model_config = SettingsConfigDict(
        env_prefix="YT_MUSIC_MANAGER_CLI_", env_nested_delimiter="__"
    )

    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from TOML file."""
        if config_path is None:
            config_path = Path("config/settings.toml")

        if not config_path.exists():
            # Create default config file
            cls.create_default_config(config_path)
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = toml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration from {config_path}: {e}")

    @classmethod
    def create_default_config(cls, config_path: Path) -> None:
        """Create a default configuration file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_settings = cls()
        config_dict = {
            "youtube": default_settings.youtube.model_dump(),
            "download": default_settings.download.model_dump(),
            "sync": default_settings.sync.model_dump(),
            "logging": default_settings.logging.model_dump(),
            "advanced": default_settings.advanced.model_dump(),
        }

        with open(config_path, "w", encoding="utf-8") as f:
            toml.dump(config_dict, f)

    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """Save current settings to TOML file."""
        if config_path is None:
            config_path = Path("config/settings.toml")

        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "youtube": self.youtube.model_dump(),
            "download": self.download.model_dump(),
            "sync": self.sync.model_dump(),
            "logging": self.logging.model_dump(),
            "advanced": self.advanced.model_dump(),
        }

        with open(config_path, "w", encoding="utf-8") as f:
            toml.dump(config_dict, f)

    def validate_setup(self) -> Dict[str, str]:
        """Validate that all required settings are properly configured."""
        issues = {}

        # Check YouTube authentication based on method
        if self.youtube.auth_method == "manual_oauth":
            if (
                not self.youtube.oauth_client_id
                or self.youtube.oauth_client_id.strip() == ""
            ):
                issues["oauth_client_id"] = (
                    "OAuth client ID is required for 'manual_oauth' method"
                )
            if (
                not self.youtube.oauth_client_secret
                or self.youtube.oauth_client_secret.strip() == ""
            ):
                issues["oauth_client_secret"] = (
                    "OAuth client secret is required for 'manual_oauth' method"
                )
        elif self.youtube.auth_method == "auto_oauth":
            # Check if bundled OAuth credentials are available
            try:
                from .oauth_client_config import OAuthClientConfig

                if not OAuthClientConfig.has_valid_config():
                    issues["bundled_oauth"] = (
                        "Bundled OAuth credentials not found for 'auto_oauth' method"
                    )
            except ImportError:
                issues["bundled_oauth"] = (
                    "OAuth configuration module not available for 'auto_oauth' method"
                )
        # 'no_auth' method requires no additional validation

        # Check download path
        try:
            download_path = Path(self.download.base_path)
            if not download_path.parent.exists():
                issues["download_path"] = (
                    f"Download path parent directory does not exist: {download_path.parent}"
                )
        except Exception as e:
            issues["download_path"] = f"Invalid download path: {e}"

        # Check log directory
        try:
            log_path = Path(self.logging.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues["log_path"] = f"Cannot create log directory: {e}"

        return issues


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load_from_file()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from file."""
    global _settings
    _settings = Settings.load_from_file()
    return _settings
