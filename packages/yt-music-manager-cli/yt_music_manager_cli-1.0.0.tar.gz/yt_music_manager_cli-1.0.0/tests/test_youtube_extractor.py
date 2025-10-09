from types import SimpleNamespace

import pytest

from yt_music_manager_cli.youtube_extractor import YouTubeExtractor, YouTubeAPIError


class FakeExtractorError(Exception):
    pass


class FakeYoutubeDL:
    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=False):
        if "private" in url:
            raise FakeExtractorError("Private playlist")
        if "missing" in url:
            raise FakeExtractorError("Playlist not found")

        if "watch?v" in url:
            return {
                "id": "vid-1",
                "title": "Video Title",
                "duration": 120,
                "upload_date": "20240101",
                "uploader": "Uploader",
                "uploader_id": "channel",
                "view_count": 123,
                "like_count": 5,
                "description": "desc",
                "thumbnails": [
                    {
                        "url": "https://example.com/thumb.jpg",
                        "width": 640,
                        "height": 480,
                    }
                ],
            }

        return {
            "title": "My Playlist",
            "description": "Playlist description",
            "uploader": "Channel",
            "uploader_id": "channel",
            "entries": [
                {
                    "id": "vid-1",
                    "title": "Video Title",
                    "duration": 120,
                    "upload_date": "20240101",
                    "uploader": "Uploader",
                    "uploader_id": "channel",
                    "view_count": 123,
                    "like_count": 5,
                    "description": "desc",
                    "thumbnails": [
                        {
                            "url": "https://example.com/thumb.jpg",
                            "width": 640,
                            "height": 480,
                        }
                    ],
                }
            ],
            "thumbnails": [
                {"url": "https://example.com/playlist.jpg", "width": 800, "height": 600}
            ],
        }


@pytest.fixture(autouse=True)
def patch_yt_dlp(monkeypatch):
    monkeypatch.setattr(
        "yt_music_manager_cli.youtube_extractor.ExtractorError", FakeExtractorError
    )
    monkeypatch.setattr(
        "yt_music_manager_cli.youtube_extractor.yt_dlp",
        SimpleNamespace(YoutubeDL=FakeYoutubeDL),
    )


def test_get_playlist_info_success(monkeypatch):
    warnings = []
    monkeypatch.setattr(
        "yt_music_manager_cli.youtube_extractor.show_warning",
        lambda msg: warnings.append(msg),
    )

    extractor = YouTubeExtractor()
    info = extractor.get_playlist_info("PL123")
    assert info.title == "My Playlist"
    assert len(info.videos) == 1
    assert info.videos[0].title == "Video Title"


def test_private_playlist_error():
    extractor = YouTubeExtractor()
    with pytest.raises(YouTubeAPIError):
        extractor.get_playlist_info("private")


def test_missing_playlist_error():
    extractor = YouTubeExtractor()
    with pytest.raises(YouTubeAPIError):
        extractor.get_playlist_info("missing")


def test_extract_playlist_id():
    extractor = YouTubeExtractor()
    playlist_id = extractor.extract_playlist_id(
        "https://youtube.com/playlist?list=PL123"
    )
    assert playlist_id == "PL123"

    with pytest.raises(YouTubeAPIError):
        extractor.extract_playlist_id("invalid-url")


def test_validate_playlist_access(monkeypatch):
    calls = []

    class ValidateDL(FakeYoutubeDL):
        def extract_info(self, url, download=False):
            calls.append(url)
            return {"title": "ok"}

    monkeypatch.setattr(
        "yt_music_manager_cli.youtube_extractor.yt_dlp",
        SimpleNamespace(YoutubeDL=ValidateDL),
    )

    extractor = YouTubeExtractor()
    assert extractor.validate_playlist_access("PL123") is True
    assert calls
