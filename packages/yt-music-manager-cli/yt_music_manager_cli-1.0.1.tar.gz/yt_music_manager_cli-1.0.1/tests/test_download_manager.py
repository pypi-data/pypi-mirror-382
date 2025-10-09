import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from yt_music_manager_cli.download_manager import (
    DownloadManager,
    DownloadProgress,
    DownloadResult,
)
from yt_music_manager_cli.youtube_api import PlaylistInfo, VideoInfo


class FakeDownloadError(Exception):
    """Simple replacement for yt_dlp DownloadError"""


class FakeYoutubeDL:
    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def download(self, urls):
        filename_template = self.opts["outtmpl"]
        file_path = Path(filename_template.replace("%(ext)s", "mp3"))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("audio-data")

        progress_info = {
            "status": "downloading",
            "info_dict": {"id": "vid-1", "title": "Title"},
            "_percent_str": "50.0%",
            "_speed_str": "1MiB/s",
            "_eta_str": "00:10",
            "_total_bytes_str": "4.0MiB",
            "filename": str(file_path),
        }
        for hook in self.opts.get("progress_hooks", []):
            hook(progress_info)

        finish_info = {
            "status": "finished",
            "info_dict": {"id": "vid-1"},
            "filename": str(file_path),
        }
        for hook in self.opts.get("progress_hooks", []):
            hook(finish_info)

        post_info = {
            "status": "finished",
            "info_dict": {"id": "vid-1"},
            "filepath": str(file_path),
        }
        for hook in self.opts.get("postprocessor_hooks", []):
            hook(post_info)


@pytest.fixture(autouse=True)
def patch_yt_dlp(monkeypatch):
    monkeypatch.setattr(
        "yt_music_manager_cli.download_manager.DownloadError", FakeDownloadError
    )
    monkeypatch.setattr(
        "yt_music_manager_cli.download_manager.yt_dlp",
        SimpleNamespace(YoutubeDL=FakeYoutubeDL),
    )


def make_video(video_id: str, title: str) -> VideoInfo:
    return VideoInfo(
        video_id=video_id,
        title=title,
        duration="PT3M",
        upload_date="2024-01-01",
        uploader="Uploader",
        uploader_id="channel",
        view_count=120,
        like_count=10,
        description="desc",
        thumbnail_url="https://example.com/thumb.jpg",
    )


def make_playlist(videos):
    return PlaylistInfo(
        playlist_id="playlist",
        title="Playlist",
        description="desc",
        channel_title="Channel",
        channel_id="channel",
        video_count=len(videos),
        last_updated="2024-02-01T00:00:00+00:00",
        videos=list(videos),
    )


def test_download_video_success(tmp_path, reset_settings):
    events = []

    def progress_callback(progress: DownloadProgress):
        events.append(progress.status)

    manager = DownloadManager(
        ffmpeg_available=True, progress_callback=progress_callback
    )
    playlist = make_playlist([make_video("vid-1", "Song One")])

    result = manager.download_video(playlist.videos[0], playlist)

    assert result.success is True
    assert Path(result.file_path).exists()
    assert "completed" in events
    assert manager.get_active_downloads()["vid-1"].status == "completed"


def test_download_video_failure(monkeypatch, reset_settings):
    def failing_download(*args, **kwargs):
        raise FakeDownloadError("boom")

    monkeypatch.setattr(FakeYoutubeDL, "download", failing_download)

    manager = DownloadManager(ffmpeg_available=False, progress_callback=None)
    playlist = make_playlist([make_video("vid-1", "Broken")])

    result = manager.download_video(playlist.videos[0], playlist)
    assert result.success is False
    assert "boom" in result.error_message


@pytest.mark.asyncio
async def test_download_playlist_concurrent(reset_settings):
    manager = DownloadManager(ffmpeg_available=True, progress_callback=None)
    videos = [make_video(f"vid-{i}", f"Title {i}") for i in range(3)]
    playlist = make_playlist(videos)

    results = await manager.download_playlist(playlist, max_concurrent=2)
    assert len(results) == 3
    assert all(isinstance(res, DownloadResult) for res in results)
    assert sum(1 for res in results if res.success) == 3


def test_verify_and_cleanup(tmp_path, reset_settings):
    manager = DownloadManager(ffmpeg_available=True)
    playlist = make_playlist([make_video("vid-1", "Song One")])

    # Create file manually
    file_path = manager.get_video_file_path(playlist.videos[0], playlist)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"data")

    assert manager.verify_download(playlist.videos[0], playlist) is True

    # Add cleanup candidates
    temp_file = file_path.with_suffix(".part")
    temp_file.write_bytes(b"")
    empty_file = file_path.with_name("empty.mp3")
    empty_file.write_bytes(b"")

    manager.cleanup_failed_downloads(playlist)
    assert not temp_file.exists()
    assert empty_file.exists() is False


def test_get_downloaded_and_cancel(reset_settings):
    manager = DownloadManager(ffmpeg_available=True)
    playlist = make_playlist([make_video("vid-1", "Song One")])
    result = manager.download_video(playlist.videos[0], playlist)

    downloaded = manager.get_downloaded_videos(playlist)
    assert any(result.file_path.endswith(path.name) for path in downloaded)

    assert manager.cancel_download("vid-1") is True
    assert manager.cancel_download("unknown") is False


def test_sanitize_filename(reset_settings):
    manager = DownloadManager(ffmpeg_available=True)
    dirty = "Inv*alid:/Name?.mp3"
    sanitized = manager.sanitize_filename(dirty)
    assert "*" not in sanitized and ":" not in sanitized
    assert sanitized.count("_") >= 1
    assert sanitized.endswith(".mp3")
