import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from yt_music_manager_cli.playlist_manager import PlaylistManager
from yt_music_manager_cli.sync_engine import SyncEngine, SyncResult, SyncAction
from yt_music_manager_cli.youtube_api import PlaylistInfo, VideoInfo
from yt_music_manager_cli.download_manager import DownloadResult, DownloadProgress


@pytest.fixture
def playlist_state(tmp_path, sample_playlist):
    manager = PlaylistManager(data_dir=tmp_path / "state")
    manager.add_playlist(sample_playlist)
    return manager


def build_playlist(videos, title="Playlist"):
    return PlaylistInfo(
        playlist_id="playlist",
        title=title,
        description="desc",
        channel_title="Channel",
        channel_id="channel",
        video_count=len(videos),
        last_updated=datetime.now(timezone.utc).isoformat(),
        videos=list(videos),
    )


@pytest.mark.asyncio
async def test_sync_engine_full_flow(monkeypatch, tmp_path):
    existing_video = VideoInfo(
        video_id="vid-1",
        title="Existing",
        duration="PT3M",
        upload_date="2024-01-01",
        uploader="Uploader",
        uploader_id="channel",
        view_count=100,
        like_count=10,
        description="existing",
        thumbnail_url="https://example.com/1.jpg",
    )
    old_video = VideoInfo(
        video_id="vid-old",
        title="Old",
        duration="PT2M",
        upload_date="2023-01-01",
        uploader="Uploader",
        uploader_id="channel",
        view_count=50,
        like_count=None,
        description="old",
        thumbnail_url="https://example.com/old.jpg",
    )
    new_video = VideoInfo(
        video_id="vid-new",
        title="New",
        duration="PT4M",
        upload_date="2024-03-01",
        uploader="Uploader",
        uploader_id="channel",
        view_count=0,
        like_count=None,
        description="new",
        thumbnail_url="https://example.com/new.jpg",
    )

    stored_playlist = build_playlist([existing_video, old_video])
    playlist_manager = PlaylistManager(data_dir=tmp_path / "state")
    playlist_manager.add_playlist(stored_playlist)
    playlist_manager.update_sync_status(
        stored_playlist.playlist_id,
        last_sync=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        download_count=1,
        failed_count=0,
        local_path=str(tmp_path / "downloads" / stored_playlist.title),
    )

    obsolete_file = Path(
        tmp_path / "downloads" / stored_playlist.title / f"{old_video.title}.mp3"
    )
    obsolete_file.parent.mkdir(parents=True, exist_ok=True)
    obsolete_file.write_text("stale")

    def playlist_manager_factory():
        return playlist_manager

    class UnifiedClientStub:
        def __init__(self):
            self.calls = []

        def get_playlist_info(self, playlist_id, include_videos=True):
            self.calls.append(("info", playlist_id, include_videos))
            return build_playlist(
                [existing_video, new_video], title=stored_playlist.title
            )

        def get_quota_usage(self):
            return {"used": 10, "remaining": 9990}

        def get_auth_status(self):
            return {"mode": "api_key", "authenticated": True}

    unified_client = UnifiedClientStub()

    class DownloadManagerStub:
        def __init__(self, ffmpeg_available, progress_callback):
            self.ffmpeg_available = ffmpeg_available
            self.progress_callback = progress_callback
            self.downloaded = []
            self.base_path = Path(tmp_path / "downloads")

        def get_playlist_download_path(self, playlist_info):
            return self.base_path / playlist_info.title

        def get_video_file_path(self, video_info, playlist_info):
            return (
                self.get_playlist_download_path(playlist_info)
                / f"{video_info.title}.mp3"
            )

        def get_downloaded_videos(self, playlist_info):
            existing_file = self.get_video_file_path(existing_video, playlist_info)
            existing_file.parent.mkdir(parents=True, exist_ok=True)
            existing_file.write_text("current")
            return [existing_file]

        async def download_playlist(self, playlist_info):
            results = []
            for video in playlist_info.videos:
                path = self.get_video_file_path(video, playlist_info)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("downloaded")
                self.downloaded.append(video.video_id)
                if self.progress_callback:
                    self.progress_callback(
                        DownloadProgress(
                            video_id=video.video_id,
                            title=video.title,
                            status="completed",
                            percent=100.0,
                            file_path=str(path),
                        )
                    )
                results.append(
                    DownloadResult(
                        video_id=video.video_id,
                        success=True,
                        file_path=str(path),
                        error_message=None,
                        file_size=100,
                        duration=3.2,
                    )
                )
            return results

    download_manager_stub = DownloadManagerStub

    monkeypatch.setattr(
        "yt_music_manager_cli.sync_engine.UnifiedYouTubeClient", lambda: unified_client
    )
    monkeypatch.setattr(
        "yt_music_manager_cli.sync_engine.PlaylistManager", playlist_manager_factory
    )
    monkeypatch.setattr(
        "yt_music_manager_cli.sync_engine.DownloadManager", download_manager_stub
    )

    progress_events = []

    def progress_callback(playlist_id, progress):
        progress_events.append((playlist_id, progress.status))

    engine = SyncEngine(ffmpeg_available=True, progress_callback=progress_callback)

    plan, error = engine.plan_sync(stored_playlist.playlist_id)
    assert error is None
    assert {item.action for item in plan} >= {
        SyncAction.DOWNLOAD,
        SyncAction.REMOVE,
        SyncAction.SKIP,
    }

    dry_run_result = await engine.sync_playlist(
        stored_playlist.playlist_id, dry_run=True
    )
    assert dry_run_result.success is True
    assert dry_run_result.items_downloaded == 0

    result = await engine.sync_playlist(stored_playlist.playlist_id, dry_run=False)
    assert isinstance(result, SyncResult)
    assert result.items_downloaded == 1
    assert result.items_removed == 1
    assert result.items_failed == 0
    assert progress_events
    assert not obsolete_file.exists()

    stats = engine.get_sync_statistics()
    assert "total_playlists" in stats
    assert stats["api_quota_used"] == 10

    issues = engine.check_prerequisites()
    assert isinstance(issues, list)

    all_results = await engine.sync_all_playlists(dry_run=True)
    assert stored_playlist.playlist_id in all_results
    assert isinstance(all_results[stored_playlist.playlist_id], SyncResult)
