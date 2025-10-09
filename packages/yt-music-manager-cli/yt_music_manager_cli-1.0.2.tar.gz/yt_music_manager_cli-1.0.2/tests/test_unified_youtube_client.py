import pytest

from yt_music_manager_cli import config
from yt_music_manager_cli.unified_youtube_client import UnifiedYouTubeClient
from yt_music_manager_cli.youtube_api import PlaylistInfo, VideoInfo


def make_playlist():
    video = VideoInfo(
        video_id="vid-1",
        title="Song",
        duration="PT3M",
        upload_date="2024-01-01",
        uploader="Uploader",
        uploader_id="channel",
        view_count=10,
        like_count=None,
        description="desc",
        thumbnail_url="https://example.com/1.jpg",
    )
    return PlaylistInfo(
        playlist_id="playlist",
        title="Playlist",
        description="desc",
        channel_title="Channel",
        channel_id="channel",
        video_count=1,
        last_updated="2024-02-01T00:00:00+00:00",
        videos=[video],
    )


def test_no_auth_uses_extractor(monkeypatch):
    config._settings.youtube.auth_method = "no_auth"

    class ExtractorStub:
        def __init__(self):
            self.calls = []

        def get_playlist_info(self, playlist_id, include_videos=True):
            self.calls.append(("info", playlist_id, include_videos))
            return make_playlist()

        def get_playlist_videos(self, playlist_id):
            self.calls.append(("videos", playlist_id))
            return make_playlist().videos

        def check_playlist_updates(self, playlist_id, last_check=None):
            self.calls.append(("updates", playlist_id, last_check))
            return make_playlist().videos, set()

        def validate_playlist_access(self, playlist_id):
            return True

    extractor = ExtractorStub()
    monkeypatch.setattr(
        "yt_music_manager_cli.unified_youtube_client.YouTubeExtractor",
        lambda: extractor,
    )

    client = UnifiedYouTubeClient()
    info = client.get_playlist_info("playlist")
    assert info.title == "Playlist"
    assert client.validate_api_access() is True
    assert client.get_supported_features()["public_playlists"] is True


def test_auto_oauth_initialization(monkeypatch):
    config._settings.youtube.auth_method = "auto_oauth"

    playlist = make_playlist()

    class OAuthStub:
        def __init__(self):
            self.setup_called = True

        def setup_oauth(self):
            return True

        def get_authenticated_youtube_api(self):
            class API:
                def get_playlist_info(self, playlist_id, include_videos=True):
                    return playlist

                def get_playlist_videos(self, playlist_id):
                    return playlist.videos

                def check_playlist_updates(self, playlist_id, last_check=None):
                    return playlist.videos, set()

                def validate_api_key(self):
                    return True

                def get_quota_usage(self):
                    return {"used": 10, "remaining": 9990}

            return API()

        def get_user_playlists(self):
            return [playlist.to_dict()]

        def get_auth_status(self):
            return {
                "method": "oauth",
                "authenticated": True,
                "user_email": "user@example.com",
            }

    oauth = OAuthStub()
    monkeypatch.setattr(
        "yt_music_manager_cli.unified_youtube_client.YouTubeOAuth", lambda: oauth
    )

    client = UnifiedYouTubeClient()
    info = client.get_playlist_info("playlist")
    assert info.title == playlist.title
    auth_info = client.get_auth_info()
    assert auth_info["authenticated"] is True
    assert client.get_quota_usage()["used"] == 10


def test_extract_playlist_id_fallback():
    config._settings.youtube.auth_method = "no_auth"
    client = UnifiedYouTubeClient()
    playlist_id = client.extract_playlist_id(
        "https://www.youtube.com/playlist?list=PL1234"
    )
    assert playlist_id == "PL1234"

    with pytest.raises(Exception):
        client.extract_playlist_id("https://www.invalid.com")
