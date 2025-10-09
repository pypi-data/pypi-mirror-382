from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from yt_music_manager_cli.playlist_manager import PlaylistManager, PlaylistState
from yt_music_manager_cli.youtube_api import PlaylistInfo, VideoInfo


@pytest.fixture
def playlist_manager(data_dir):
    return PlaylistManager(data_dir=data_dir)


def test_add_get_remove_playlist(playlist_manager, sample_playlist):
    playlist_manager.add_playlist(sample_playlist)
    state = playlist_manager.get_playlist(sample_playlist.playlist_id)
    assert isinstance(state, PlaylistState)
    assert state.playlist_info.title == sample_playlist.title
    assert state.download_count == 0

    playlist_manager.update_sync_status(
        sample_playlist.playlist_id,
        last_sync=datetime.now(timezone.utc).isoformat(),
        download_count=3,
        failed_count=1,
        local_path="/tmp/path",
        sync_errors=["err"],
    )
    updated = playlist_manager.get_playlist(sample_playlist.playlist_id)
    assert updated.download_count == 3
    assert updated.failed_count == 1
    assert updated.sync_errors == ["err"]

    playlist_manager.remove_playlist(sample_playlist.playlist_id)
    assert playlist_manager.get_playlist(sample_playlist.playlist_id) is None


def test_get_all_and_statistics(playlist_manager, sample_playlist, tmp_path):
    playlist_manager.add_playlist(sample_playlist)
    stats = playlist_manager.get_statistics()
    assert stats["total_playlists"] == 1
    assert stats["total_videos"] == len(sample_playlist.videos)
    assert stats["never_synced"] == 1

    playlist_manager.update_sync_status(
        sample_playlist.playlist_id,
        last_sync=datetime.now(timezone.utc).isoformat(),
        download_count=2,
        failed_count=0,
        local_path=str(tmp_path / "downloads"),
    )
    stats = playlist_manager.get_statistics()
    assert stats["recently_synced"] == 1


def test_get_stale_playlists(playlist_manager, sample_playlist):
    playlist_manager.add_playlist(sample_playlist)
    stale = playlist_manager.get_stale_playlists()
    assert any(
        p.playlist_info.playlist_id == sample_playlist.playlist_id for p in stale
    )

    old_time = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    playlist_manager.update_sync_status(sample_playlist.playlist_id, last_sync=old_time)
    stale = playlist_manager.get_stale_playlists(max_age_hours=10)
    assert len(stale) == 1


def test_export_and_import(playlist_manager, sample_playlist, tmp_path):
    playlist_manager.add_playlist(sample_playlist)
    export_path = tmp_path / "export.json"
    playlist_manager.export_playlists(export_path)
    assert export_path.exists()

    # Create a new manager and import
    new_manager = PlaylistManager(data_dir=tmp_path / "imported")
    imported = new_manager.import_playlists(export_path)
    assert imported == 1
    assert new_manager.get_playlist(sample_playlist.playlist_id) is not None


def test_import_merge_skip_existing(playlist_manager, sample_playlist, tmp_path):
    playlist_manager.add_playlist(sample_playlist)
    export_path = tmp_path / "export.json"
    playlist_manager.export_playlists(export_path)

    other_manager = PlaylistManager(data_dir=tmp_path / "other")
    other_manager.import_playlists(export_path)
    assert len(other_manager.get_all_playlists()) == 1

    # Import again with merge=False should skip existing playlist
    imported = other_manager.import_playlists(export_path, merge=False)
    assert imported == 0


def test_cleanup_orphaned_data(playlist_manager):
    assert playlist_manager.cleanup_orphaned_data() == 0


def test_get_playlist_by_url_uses_extractor(
    playlist_manager, sample_playlist, monkeypatch
):
    playlist_manager.add_playlist(sample_playlist)

    class DummyUnifiedClient:
        def extract_playlist_id(self, url: str) -> str:
            assert "playlist" in url
            return sample_playlist.playlist_id

    monkeypatch.setattr("yt_music_manager_cli.unified_youtube_client.get_youtube_client", lambda: DummyUnifiedClient())
    found = playlist_manager.get_playlist_by_url(
        "https://www.youtube.com/playlist?list=abc"
    )
    assert isinstance(found, PlaylistState)
    assert found.playlist_info.playlist_id == sample_playlist.playlist_id
