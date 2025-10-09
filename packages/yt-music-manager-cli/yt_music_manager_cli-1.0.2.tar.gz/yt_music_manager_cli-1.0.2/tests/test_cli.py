import asyncio
import io
from pathlib import Path

import click
from click.testing import CliRunner
import pytest

from yt_music_manager_cli import cli, config
from yt_music_manager_cli.sync_engine import SyncResult
from yt_music_manager_cli.youtube_api import PlaylistInfo, VideoInfo


class StubPlaylistState:
    def __init__(self, playlist_info: PlaylistInfo):
        self.playlist_info = playlist_info
        self.last_sync = None
        self.download_count = 0
        self.failed_count = 0
        self.local_path = "stub"
        self.sync_errors = []


class StubPlaylistManager:
    store = {}

    def __init__(self, *args, **kwargs):
        pass

    def add_playlist(self, playlist_info: PlaylistInfo):
        self.store[playlist_info.playlist_id] = StubPlaylistState(playlist_info)

    def get_playlist(self, playlist_id: str):
        return self.store.get(playlist_id)

    def get_all_playlists(self):
        return dict(self.store)

    def remove_playlist(self, playlist_id: str):
        self.store.pop(playlist_id, None)
        return True

    def update_playlist_info(
        self, playlist_id: str, playlist_info: PlaylistInfo, save: bool = True
    ):
        if playlist_id in self.store:
            self.store[playlist_id].playlist_info = playlist_info

    def update_sync_status(self, playlist_id: str, **kwargs):
        if playlist_id in self.store:
            state = self.store[playlist_id]
            state.last_sync = kwargs.get("last_sync", state.last_sync)
            state.download_count = kwargs.get("download_count", state.download_count)
            state.failed_count = kwargs.get("failed_count", state.failed_count)
            state.local_path = kwargs.get("local_path", state.local_path)
            state.sync_errors = kwargs.get("sync_errors", state.sync_errors)

    def save(self):
        pass

    def get_statistics(self):
        return {
            "total_playlists": len(self.store),
            "total_videos": sum(
                len(state.playlist_info.videos) for state in self.store.values()
            ),
            "total_downloaded": sum(
                state.download_count for state in self.store.values()
            ),
            "total_failed": sum(state.failed_count for state in self.store.values()),
            "never_synced": sum(
                1 for state in self.store.values() if state.last_sync is None
            ),
            "recently_synced": 0,
        }


class StubSyncEngine:
    def __init__(self, *args, **kwargs):
        self.ffmpeg_available = kwargs.get("ffmpeg_available", True)

    def analyze_playlist_changes(self, *args, **kwargs):
        return []

    async def sync_playlist(self, playlist_id: str, **kwargs):
        return SyncResult(
            playlist_id=playlist_id,
            success=True,
            items_downloaded=1,
            items_removed=0,
            items_skipped=0,
            items_failed=0,
            errors=[],
            duration_seconds=0.1,
        )

    async def sync_all_playlists(self, *args, **kwargs):
        return {
            "playlist": SyncResult(
                playlist_id="playlist",
                success=True,
                items_downloaded=1,
                items_removed=0,
                items_skipped=0,
                items_failed=0,
                errors=[],
                duration_seconds=0.1,
            )
        }

    def get_sync_statistics(self):
        return {"total": 1}

    def check_prerequisites(self):
        return []


class StubYouTubeClient:
    def __init__(self):
        self.playlist = PlaylistInfo(
            playlist_id="playlist",
            title="Playlist",
            description="desc",
            channel_title="Channel",
            channel_id="channel",
            video_count=1,
            last_updated="2024-01-01T00:00:00+00:00",
            videos=[
                VideoInfo(
                    video_id="vid",
                    title="Song",
                    duration="PT3M",
                    upload_date="2024-01-01",
                    uploader="Uploader",
                    uploader_id="channel",
                    view_count=1,
                    like_count=1,
                    description="desc",
                    thumbnail_url="https://example.com/thumb.jpg",
                )
            ],
        )

    def validate_api_access(self):
        return True

    def get_supported_features(self):
        return {"public_playlists": True, "private_playlists": True}

    def get_auth_info(self):
        return {
            "method": "auto_oauth",
            "authenticated": True,
            "user_email": "user@example.com",
        }

    def get_quota_usage(self):
        return {"used": 1, "remaining": 9999, "limit": 10000}

    def extract_playlist_id(self, url: str):
        return "playlist"

    def get_playlist_info(self, playlist_id: str, include_videos: bool = True):
        return self.playlist

    def get_playlist_videos(self, playlist_id: str):
        return self.playlist.videos

    def check_playlist_updates(self, playlist_id: str, last_check=None):
        return self.playlist.videos, set()

    def get_user_playlists(self):
        return [self.playlist]

    def validate_playlist_access(self, playlist_id: str):
        return True


class StubOAuthClientConfig:
    @staticmethod
    def has_valid_config():
        return True

    @staticmethod
    def save_user_config(client_id: str, client_secret: str):
        return True

    @staticmethod
    def remove_user_config():
        return True

    @staticmethod
    def get_client_config():
        return {
            "client_id": "client",
            "client_secret": "secret",
            "auth_uri": "https://example.com/auth",
            "token_uri": "https://example.com/token",
            "redirect_uris": ["http://localhost"],
        }


class StubYouTubeOAuth:
    def __init__(self):
        self.called_setup = False
        self.authenticated = True

    def setup_oauth(self):
        self.called_setup = True
        return True

    def get_authenticated_youtube_api(self):
        return StubYouTubeClient()

    def _load_existing_credentials(self):
        return True

    def get_user_playlists(self):
        return [
            {
                "id": "playlist",
                "snippet": {
                    "title": "Playlist",
                    "description": "desc",
                    "channelTitle": "Channel",
                    "channelId": "channel",
                    "privacyStatus": "public",
                },
                "contentDetails": {"itemCount": 1},
            }
        ]

    def get_auth_status(self):
        return {"authenticated": self.authenticated, "user_email": "user@example.com"}

    def _perform_oauth_flow(self):
        return True

    def revoke_authentication(self):
        return True


@pytest.fixture
def cli_environment(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    StubPlaylistManager.store = {}

    fake_console = cli.Console(file=io.StringIO(), force_terminal=False, width=120)
    monkeypatch.setattr(cli, "console", fake_console)
    monkeypatch.setattr(cli.static_ffmpeg, "add_paths", lambda: None)
    monkeypatch.setattr(cli.shutil, "which", lambda name: "ffmpeg")
    monkeypatch.setattr(cli, "setup_logging", lambda: None)
    monkeypatch.setattr(cli, "get_youtube_client", lambda: StubYouTubeClient())
    monkeypatch.setattr(cli, "PlaylistManager", StubPlaylistManager)
    monkeypatch.setattr(cli, "SyncEngine", StubSyncEngine)
    monkeypatch.setattr(cli, "YouTubeOAuth", StubYouTubeOAuth)
    from yt_music_manager_cli import oauth_handler as oauth_handler_module

    monkeypatch.setattr(oauth_handler_module, "YouTubeOAuth", StubYouTubeOAuth)
    monkeypatch.setattr(cli, "OAuthClientConfig", StubOAuthClientConfig)
    monkeypatch.setattr(
        cli, "create_oauth_client_template", lambda: Path("oauth_template.json")
    )
    monkeypatch.setattr(cli, "setup_oauth_instructions", lambda: "instructions")
    monkeypatch.setattr(cli, "show_warning", lambda message: None)
    confirm_responses = {
        "Do you want to reconfigure?": True,
    }

    def fake_confirm(message, default=False):
        return confirm_responses.get(message, False)

    monkeypatch.setattr(cli.click, "confirm", fake_confirm)
    return runner


def invoke_command(runner: CliRunner, args: list[str], **kwargs):
    console_stream = getattr(cli.console, "file", None)

    if console_stream is not None:
        reset = getattr(console_stream, "seek", None)
        truncate = getattr(console_stream, "truncate", None)

        if callable(reset):
            reset(0)
        if callable(truncate):
            truncate(0)

    result = runner.invoke(cli.main, args, **kwargs)

    console_output = ""
    if console_stream is not None:
        get_value = getattr(console_stream, "getvalue", None)
        if callable(get_value):
            console_output = get_value()

    console_output = (console_output or "") + (result.output or "")

    assert result.exit_code == 0, console_output or result.output
    return result, console_output


def test_main_help_and_version(cli_environment):
    runner = cli_environment
    _, output = invoke_command(runner, ["--help"])
    assert "YT Music Manager CLI" in output

    _, version_output = invoke_command(runner, ["--version"])
    assert "YT Music Manager CLI (YTMM CLI) v" in version_output


def test_init_command(cli_environment):
    runner = cli_environment
    _, output = invoke_command(runner, ["init"])
    assert "Initializing YT Music Manager CLI" in output


def test_config_and_list_commands(cli_environment):
    runner = cli_environment
    _, output = invoke_command(runner, ["config"])
    assert "Configuration" in output

    _, list_output = invoke_command(runner, ["list-playlists"])
    assert "No playlists are currently being tracked" in list_output

    _, detailed_output = invoke_command(runner, ["list-playlists", "--detailed"])
    assert "No playlists are currently being tracked" in detailed_output


def test_add_sync_remove_status(cli_environment):
    runner = cli_environment
    _, add_output = invoke_command(
        runner, ["add-playlist", "https://www.youtube.com/playlist?list=PL123"]
    )
    assert "Added playlist" in add_output

    _, sync_output = invoke_command(runner, ["sync", "playlist", "--dry-run"])
    assert "Sync completed" in sync_output

    _, sync_all_output = invoke_command(runner, ["sync", "--all", "--dry-run"])
    assert "Sync Summary" in sync_all_output

    _, status_output = invoke_command(runner, ["status"])
    assert "YT Music Manager CLI" in status_output and "Status" in status_output

    _, remove_output = invoke_command(runner, ["remove-playlist", "playlist"])
    assert "Playlist removed" in remove_output


def test_config_set_and_list(cli_environment, tmp_path):
    runner = cli_environment
    settings_file = Path("config/settings.toml")
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text('[youtube]\nauth_method = "no_auth"\n')

    _, set_output = invoke_command(
        runner, ["config", "set", "youtube.auth_method", "manual_oauth"]
    )
    assert "Set youtube.auth_method" in set_output

    _, get_output = invoke_command(runner, ["config", "list", "youtube.auth_method"])
    assert "manual_oauth" in get_output

    _, get_all_output = invoke_command(runner, ["config", "list"])
    assert "Current Configuration" in get_all_output


def test_auth_commands(cli_environment, tmp_path):
    runner = cli_environment

    # Test auth status
    _, auth_status_output = invoke_command(runner, ["auth", "status"])
    assert "Authentication Status" in auth_status_output

    # Test setting to no_auth mode
    _, auth_mode_no_auth_output = invoke_command(runner, ["auth", "mode", "no_auth"])
    assert "No additional setup required" in auth_mode_no_auth_output

    # Test setting to auto_oauth mode (should prompt for sign-in)
    _, auth_mode_auto_oauth_output = invoke_command(
        runner, ["auth", "mode", "auto_oauth"], input="n\n"
    )
    assert "Setting authentication method to: auto_oauth" in auth_mode_auto_oauth_output

    # Test auth remove for login tokens
    _, auth_remove_login_output = invoke_command(
        runner, ["auth", "remove", "login", "-y"]
    )
    assert (
        "Successfully signed out" in auth_remove_login_output
        or "No active authentication found" in auth_remove_login_output
    )


def test_list_user_playlists(cli_environment):
    runner = cli_environment
    _, output = invoke_command(runner, ["list-user-playlists", "--simple"])
    assert "Your YouTube Playlists" in output


def test_config_validation_cli(cli_environment, tmp_path):
    runner = cli_environment
    settings_file = Path("config/settings.toml")
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    config.Settings.create_default_config(settings_file)

    _, output = invoke_command(
        runner, ["config", "set", "download.audio_quality", "192"]
    )
    assert "Set download.audio_quality" in output

    _, invalid_output = invoke_command(
        runner, ["config", "set", "youtube.auth_method", "unsupported"]
    )
    assert "Invalid auth_method" in invalid_output

    # Test invalid audio_quality (too high)
    _, invalid_quality_output = invoke_command(
        runner, ["config", "set", "download.audio_quality", "900"]
    )
    assert (
        "Invalid audio quality. Must be between 64 and 320 kbps"
        in invalid_quality_output
    )

    # Test invalid audio_quality (non-integer)
    _, invalid_quality_type_output = invoke_command(
        runner, ["config", "set", "download.audio_quality", "abc"]
    )
    assert "Audio quality must be a valid integer" in invalid_quality_type_output

    # Test invalid audio_format
    _, invalid_format_output = invoke_command(
        runner, ["config", "set", "download.audio_format", "invalid"]
    )
    assert (
        "Invalid audio format 'invalid'. Must be one of: mp3, aac, ogg, wav, flac"
        in invalid_format_output
    )


@pytest.mark.asyncio
async def test_sync_single_playlist_function(monkeypatch):
    monkeypatch.setattr(cli, "SyncEngine", StubSyncEngine)
    monkeypatch.setattr(cli, "PlaylistManager", StubPlaylistManager)
    monkeypatch.setattr(
        cli, "console", cli.Console(file=io.StringIO(), force_terminal=False)
    )
    StubPlaylistManager.store = {
        "playlist": StubPlaylistState(StubYouTubeClient().playlist)
    }
    result = await cli.sync_single_playlist(
        "playlist", dry_run=True, ffmpeg_available=True
    )
    assert isinstance(result, SyncResult)
    assert result.success is True


@pytest.mark.asyncio
async def test_sync_all_playlists_function(monkeypatch):
    monkeypatch.setattr(cli, "SyncEngine", StubSyncEngine)
    monkeypatch.setattr(cli, "PlaylistManager", StubPlaylistManager)
    monkeypatch.setattr(
        cli, "console", cli.Console(file=io.StringIO(), force_terminal=False)
    )
    console_stream = cli.console.file
    console_stream.seek(0)
    console_stream.truncate(0)
    StubPlaylistManager.store = {
        "playlist": StubPlaylistState(StubYouTubeClient().playlist)
    }
    results = await cli.sync_all_playlists(dry_run=True, ffmpeg_available=True)
    output = console_stream.getvalue()
    assert results is None
    assert "Sync Summary" in output
    assert "Playlist: 1 downloaded" in output
