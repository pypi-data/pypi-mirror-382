from pathlib import Path

import pytest

from yt_music_manager_cli import config
from yt_music_manager_cli.config import (
    AdvancedConfig,
    DownloadConfig,
    LoggingConfig,
    Settings,
    SyncConfig,
    YouTubeConfig,
)


def test_youtube_config_validation_manual_oauth():
    cfg = YouTubeConfig(auth_method="no_auth")
    assert cfg.auth_method == "no_auth"

    with pytest.raises(ValueError):
        YouTubeConfig(auth_method="unsupported")

    with pytest.raises(ValueError):
        YouTubeConfig(
            auth_method="manual_oauth", oauth_client_id="", oauth_client_secret="secret"
        )

    with pytest.raises(ValueError):
        YouTubeConfig(
            auth_method="manual_oauth", oauth_client_id="client", oauth_client_secret=""
        )

    manual = YouTubeConfig(
        auth_method="manual_oauth",
        oauth_client_id="client",
        oauth_client_secret="secret",
    )
    assert manual.oauth_client_id == "client"


def test_download_config_validation(tmp_path):
    cfg = DownloadConfig(
        base_path=str(tmp_path), audio_format="mp3", audio_quality="192"
    )
    assert cfg.audio_format == "mp3"

    with pytest.raises(ValueError):
        DownloadConfig(audio_format="unsupported")

    with pytest.raises(ValueError):
        DownloadConfig(audio_quality="20")


def test_sync_config_validation():
    cfg = SyncConfig()
    assert cfg.max_concurrent_downloads == 3

    with pytest.raises(ValueError):
        SyncConfig(auto_sync_interval=100)

    with pytest.raises(ValueError):
        SyncConfig(max_concurrent_downloads=20)


def test_logging_and_advanced_config_validation():
    log_cfg = LoggingConfig()
    assert log_cfg.level == "INFO"

    with pytest.raises(ValueError):
        LoggingConfig(level="verbose")

    adv_cfg = AdvancedConfig()
    assert adv_cfg.retry_attempts == 3

    with pytest.raises(ValueError):
        AdvancedConfig(retry_attempts=0)

    with pytest.raises(ValueError):
        AdvancedConfig(retry_delay=0)

    with pytest.raises(ValueError):
        AdvancedConfig(connection_timeout=1)


def test_settings_file_round_trip(tmp_path):
    config_path = tmp_path / "settings.toml"
    Settings.create_default_config(config_path)
    assert config_path.exists()

    settings = Settings.load_from_file(config_path)
    assert settings.youtube.auth_method == "no_auth"

    settings.download.audio_format = "ogg"
    settings.save_to_file(config_path)

    loaded = Settings.load_from_file(config_path)
    assert loaded.download.audio_format == "ogg"


def test_settings_validation_and_reload(reset_settings, tmp_path, monkeypatch):
    settings = Settings()
    settings.download.base_path = str(tmp_path / "downloads")
    settings.youtube.auth_method = "manual_oauth"
    settings.youtube.oauth_client_id = ""
    settings.youtube.oauth_client_secret = ""

    config._settings = settings
    issues = settings.validate_setup()
    assert "oauth_client_id" in issues
    assert "oauth_client_secret" in issues

    config_path = tmp_path / "cfg.toml"
    settings.save_to_file(config_path)
    monkeypatch.setattr(config, "Settings", Settings)

    config._settings = None
    reloaded = config.reload_settings()
    assert isinstance(reloaded, Settings)


def test_get_settings_creates_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings_path = Path("config/settings.toml")
    assert not settings_path.exists()

    config._settings = None
    cfg = config.get_settings()
    assert settings_path.exists()
    assert isinstance(cfg, Settings)
