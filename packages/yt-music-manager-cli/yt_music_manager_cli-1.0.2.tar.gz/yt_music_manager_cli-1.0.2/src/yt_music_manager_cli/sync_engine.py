"""
Synchronization engine for YouTube playlists.
Handles detecting changes, updating local files, and maintaining sync state.
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Callable
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from .config import get_settings
from .unified_youtube_client import UnifiedYouTubeClient
from .youtube_api import PlaylistInfo, VideoInfo  # Keep these for type hints
from .download_manager import DownloadManager, DownloadResult, DownloadProgress
from .playlist_manager import PlaylistManager, PlaylistState


logger = logging.getLogger(__name__)


class SyncAction(Enum):
    """Types of sync actions that can be performed."""

    DOWNLOAD = "download"
    REMOVE = "remove"
    SKIP = "skip"
    UPDATE_METADATA = "update_metadata"


@dataclass
class SyncItem:
    """Represents a single sync action to be performed."""

    action: SyncAction
    video_info: VideoInfo
    reason: str
    local_file_path: Optional[Path] = None


@dataclass
class SyncResult:
    """Result of a playlist synchronization operation."""

    playlist_id: str
    success: bool
    items_processed: int = 0
    items_downloaded: int = 0
    items_removed: int = 0
    items_skipped: int = 0
    items_failed: int = 0
    errors: List[str] = None
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SyncEngine:
    """Handles synchronization of YouTube playlists with local files."""

    def __init__(
        self,
        ffmpeg_available: bool,
        progress_callback: Optional[Callable[[str, DownloadProgress], None]] = None,
    ):
        """Initialize sync engine."""
        self.settings = get_settings()
        self.youtube_client = UnifiedYouTubeClient()
        self.download_manager = DownloadManager(
            ffmpeg_available=ffmpeg_available,
            progress_callback=self._download_progress_wrapper,
        )
        self.playlist_manager = PlaylistManager()

        self.progress_callback = progress_callback
        self._current_playlist_id: Optional[str] = None

        # Lazy loading cache for playlist info
        self._playlist_cache: Dict[str, PlaylistInfo] = {}
        self._playlist_cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl_minutes = 30  # Cache playlist data for 30 minutes

    def _download_progress_wrapper(self, progress: DownloadProgress) -> None:
        """Wrapper for download progress callback."""
        if self.progress_callback and self._current_playlist_id:
            self.progress_callback(self._current_playlist_id, progress)

    def _get_cached_playlist_info(
        self, playlist_id: str, force_refresh: bool = False
    ) -> Optional[PlaylistInfo]:
        """Get playlist info from cache or API with lazy loading."""
        current_time = datetime.now(timezone.utc)

        # Check if we have cached data and it's still valid
        if (
            not force_refresh
            and playlist_id in self._playlist_cache
            and playlist_id in self._playlist_cache_timestamps
        ):

            cache_age = current_time - self._playlist_cache_timestamps[playlist_id]
            if cache_age.total_seconds() < (self._cache_ttl_minutes * 60):
                logger.debug(f"Using cached playlist info for {playlist_id}")
                return self._playlist_cache[playlist_id]

        # Cache miss or expired - fetch from API
        try:
            logger.debug(f"Fetching fresh playlist info for {playlist_id}")
            playlist_info = self.youtube_client.get_playlist_info(
                playlist_id, include_videos=True
            )

            # Update cache
            self._playlist_cache[playlist_id] = playlist_info
            self._playlist_cache_timestamps[playlist_id] = current_time

            return playlist_info
        except Exception as e:
            logger.error(f"Failed to fetch playlist info for {playlist_id}: {e}")
            # Return cached version if available, even if expired
            return self._playlist_cache.get(playlist_id)

    def _get_cached_playlist_info_lightweight(
        self, playlist_id: str
    ) -> Optional[PlaylistInfo]:
        """Get playlist info without videos for lightweight operations."""
        try:
            # First check if we have full cached data
            cached_info = self._get_cached_playlist_info(playlist_id)
            if cached_info and cached_info.videos:
                # Return a copy without videos for lightweight operations
                lightweight_info = PlaylistInfo(
                    playlist_id=cached_info.playlist_id,
                    title=cached_info.title,
                    description=cached_info.description,
                    channel_title=cached_info.channel_title,
                    channel_id=cached_info.channel_id,
                    video_count=cached_info.video_count,
                    last_updated=cached_info.last_updated,
                    thumbnail_url=cached_info.thumbnail_url,
                    videos=[],  # Empty videos list for lightweight operations
                )
                return lightweight_info

            # If no cache, fetch lightweight version
            return self.youtube_client.get_playlist_info(
                playlist_id, include_videos=False
            )

        except Exception as e:
            logger.error(
                f"Failed to fetch lightweight playlist info for {playlist_id}: {e}"
            )
            return None

    def clear_playlist_cache(self, playlist_id: Optional[str] = None) -> None:
        """Clear playlist cache for specific playlist or all playlists."""
        if playlist_id:
            self._playlist_cache.pop(playlist_id, None)
            self._playlist_cache_timestamps.pop(playlist_id, None)
            logger.debug(f"Cleared cache for playlist {playlist_id}")
        else:
            self._playlist_cache.clear()
            self._playlist_cache_timestamps.clear()
            logger.debug("Cleared all playlist cache")

    def analyze_playlist_changes(
        self, playlist_state: PlaylistState, current_playlist: PlaylistInfo
    ) -> List[SyncItem]:
        """Analyze changes between stored and current playlist."""
        sync_items = []

        # Get current video IDs and stored video IDs
        current_videos = {video.video_id: video for video in current_playlist.videos}
        stored_videos = {
            video.video_id: video for video in playlist_state.playlist_info.videos
        }

        # Get existing local files
        local_files = self.download_manager.get_downloaded_videos(current_playlist)
        local_video_ids = set()

        for file_path in local_files:
            # Try to match files to video IDs (this could be improved with better metadata storage)
            for video_id, video_info in current_videos.items():
                expected_path = self.download_manager.get_video_file_path(
                    video_info, current_playlist
                )
                if (
                    file_path.name == expected_path.name
                    or file_path.stem in video_info.title
                ):
                    local_video_ids.add(video_id)
                    break

        # Find new videos (in current but not in stored or not downloaded)
        for video_id, video_info in current_videos.items():
            if video_id not in stored_videos:
                sync_items.append(
                    SyncItem(
                        action=SyncAction.DOWNLOAD,
                        video_info=video_info,
                        reason="New video in playlist",
                    )
                )
            elif video_id not in local_video_ids:
                sync_items.append(
                    SyncItem(
                        action=SyncAction.DOWNLOAD,
                        video_info=video_info,
                        reason="Video not found locally",
                    )
                )
            else:
                # Check if metadata has changed significantly
                stored_video = stored_videos[video_id]
                if (
                    video_info.title != stored_video.title
                    or video_info.duration != stored_video.duration
                ):
                    sync_items.append(
                        SyncItem(
                            action=SyncAction.UPDATE_METADATA,
                            video_info=video_info,
                            reason="Video metadata changed",
                        )
                    )
                else:
                    sync_items.append(
                        SyncItem(
                            action=SyncAction.SKIP,
                            video_info=video_info,
                            reason="Already up to date",
                        )
                    )

        # Find removed videos (in stored but not in current)
        for video_id, video_info in stored_videos.items():
            if video_id not in current_videos:
                local_file_path = self.download_manager.get_video_file_path(
                    video_info, playlist_state.playlist_info
                )
                sync_items.append(
                    SyncItem(
                        action=SyncAction.REMOVE,
                        video_info=video_info,
                        reason="Video removed from playlist",
                        local_file_path=local_file_path,
                    )
                )

        return sync_items

    def plan_sync(
        self, playlist_id: str, current_playlist: Optional[PlaylistInfo] = None
    ) -> Tuple[List[SyncItem], Optional[str]]:
        """Plan synchronization actions for a playlist."""
        playlist_state = self.playlist_manager.get_playlist(playlist_id)
        if not playlist_state:
            return [], "Playlist not found in tracking list"

        try:
            # Fetch current playlist information if not provided (with caching)
            if current_playlist is None:
                current_playlist = self._get_cached_playlist_info(playlist_id)

            # Analyze changes
            sync_items = self.analyze_playlist_changes(playlist_state, current_playlist)

            logger.debug(
                f"Sync plan for '{current_playlist.title}': {len(sync_items)} items"
            )

            # Log summary of actions
            action_counts = {}
            for item in sync_items:
                action_counts[item.action] = action_counts.get(item.action, 0) + 1

            for action, count in action_counts.items():
                logger.debug(f"  {action.value}: {count} items")

            return sync_items, None

        except Exception as e:
            error_msg = f"Error planning sync for playlist {playlist_id}: {str(e)}"
            logger.error(error_msg)
            return [], error_msg

    async def sync_playlist(
        self,
        playlist_id: str,
        current_playlist: Optional[PlaylistInfo] = None,
        dry_run: bool = False,
        save: bool = True,
    ) -> SyncResult:
        """Synchronize a single playlist, optionally with pre-fetched info."""
        start_time = datetime.now()
        result = SyncResult(playlist_id=playlist_id, success=False)

        try:
            self._current_playlist_id = playlist_id

            # Plan sync actions
            sync_items, error = self.plan_sync(
                playlist_id, current_playlist=current_playlist
            )
            if error:
                result.errors.append(error)
                return result

            if not sync_items:
                logger.debug(f"No sync actions needed for playlist {playlist_id}")
                result.success = True
                return result

            # If current_playlist was not provided, it would have been fetched in plan_sync
            # We need to ensure we have it for the rest of the function.
            if current_playlist is None:
                current_playlist = self._get_cached_playlist_info(playlist_id)

            playlist_state = self.playlist_manager.get_playlist(playlist_id)

            result.items_processed = len(sync_items)

            if dry_run:
                logger.debug(f"DRY RUN: Would process {len(sync_items)} items")
                for item in sync_items:
                    logger.debug(
                        f"  {item.action.value}: {item.video_info.title} - {item.reason}"
                    )
                result.success = True
                return result

            # Process sync actions
            downloads_needed = [
                item for item in sync_items if item.action == SyncAction.DOWNLOAD
            ]
            removals_needed = [
                item for item in sync_items if item.action == SyncAction.REMOVE
            ]

            # Handle downloads
            if downloads_needed:
                logger.debug(f"Downloading {len(downloads_needed)} videos...")
                download_results = await self._process_downloads(
                    downloads_needed, current_playlist
                )

                for download_result in download_results:
                    if download_result.success:
                        result.items_downloaded += 1
                    else:
                        result.items_failed += 1
                        result.errors.append(
                            f"Download failed: {download_result.error_message}"
                        )

            # Handle removals
            if removals_needed:
                logger.debug(f"Removing {len(removals_needed)} files...")
                removed_count = self._process_removals(removals_needed)
                result.items_removed = removed_count

            # Count skipped items
            result.items_skipped = len(
                [item for item in sync_items if item.action == SyncAction.SKIP]
            )

            # Update playlist state
            self.playlist_manager.update_playlist_info(
                playlist_id, current_playlist, save=save
            )
            self.playlist_manager.update_sync_status(
                playlist_id=playlist_id,
                last_sync=datetime.now(timezone.utc).isoformat(),
                download_count=playlist_state.download_count + result.items_downloaded,
                failed_count=playlist_state.failed_count + result.items_failed,
                local_path=str(
                    self.download_manager.get_playlist_download_path(current_playlist)
                ),
                sync_errors=result.errors[-10:],  # Keep last 10 errors
                save=save,
            )

            result.success = result.items_failed == 0

            logger.debug(
                f"Sync completed for '{current_playlist.title}': "
                f"{result.items_downloaded} downloaded, {result.items_removed} removed, "
                f"{result.items_skipped} skipped, {result.items_failed} failed"
            )

        except Exception as e:
            error_msg = f"Sync failed for playlist {playlist_id}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self._current_playlist_id = None

        return result

    async def _process_downloads(
        self, download_items: List[SyncItem], playlist_info: PlaylistInfo
    ) -> List[DownloadResult]:
        """Process download actions."""
        videos_to_download = [item.video_info for item in download_items]

        # Update playlist info with videos to download
        playlist_with_downloads = PlaylistInfo(
            playlist_id=playlist_info.playlist_id,
            title=playlist_info.title,
            description=playlist_info.description,
            channel_title=playlist_info.channel_title,
            channel_id=playlist_info.channel_id,
            video_count=len(videos_to_download),
            last_updated=playlist_info.last_updated,
            thumbnail_url=playlist_info.thumbnail_url,
            videos=videos_to_download,
        )

        return await self.download_manager.download_playlist(playlist_with_downloads)

    def _process_removals(self, removal_items: List[SyncItem]) -> int:
        """Process file removal actions."""
        removed_count = 0

        for item in removal_items:
            if item.local_file_path and item.local_file_path.exists():
                try:
                    if not self.settings.sync.preserve_deleted_locally:
                        item.local_file_path.unlink()
                        logger.debug(f"Removed file: {item.local_file_path.name}")
                        removed_count += 1
                    else:
                        logger.debug(
                            f"Would remove (preserved): {item.local_file_path.name}"
                        )
                except OSError as e:
                    logger.error(f"Failed to remove file {item.local_file_path}: {e}")
            else:
                logger.warning(f"File not found for removal: {item.video_info.title}")

        return removed_count

    async def _sync_playlist_task(self, playlist_id: str, dry_run: bool) -> SyncResult:
        """Helper to wrap sync_playlist for concurrent execution."""
        try:
            # When syncing all, save changes at the end
            return await self.sync_playlist(playlist_id, dry_run=dry_run, save=False)
        except Exception as e:
            logger.error(f"Failed to sync playlist {playlist_id}: {e}")
            return SyncResult(playlist_id=playlist_id, success=False, errors=[str(e)])

    async def sync_all_playlists(self, dry_run: bool = False) -> Dict[str, SyncResult]:
        """Sync all tracked playlists concurrently."""
        all_playlists = self.playlist_manager.get_all_playlists()

        logger.debug(f"Starting concurrent sync of {len(all_playlists)} playlists...")

        # Create a list of tasks to run concurrently
        tasks = [
            self._sync_playlist_task(playlist_id, dry_run)
            for playlist_id in all_playlists
        ]

        # Run tasks and gather results
        sync_results = await asyncio.gather(*tasks)

        # Process results into a dictionary
        results = {res.playlist_id: res for res in sync_results}

        # Save all changes at once
        if not dry_run:
            self.playlist_manager.save()
            logger.debug("All playlist changes saved to disk.")

        # Log summary
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        total_downloaded = sum(r.items_downloaded for r in results.values())
        total_removed = sum(r.items_removed for r in results.values())

        logger.debug(
            f"Sync all completed: {successful} successful, {failed} failed, "
            f"{total_downloaded} downloaded, {total_removed} removed"
        )

        return results

    def get_sync_statistics(self) -> Dict[str, any]:
        """Get synchronization statistics."""
        stats = self.playlist_manager.get_statistics()

        # Add quota information if available
        try:
            quota_info = self.youtube_client.get_quota_usage()
            if quota_info:
                stats.update(
                    {
                        "api_quota_used": quota_info["used"],
                        "api_quota_remaining": quota_info["remaining"],
                    }
                )
        except Exception:
            pass  # Ignore quota errors for no-auth mode

        return stats

    def check_prerequisites(self) -> List[str]:
        """Check if all prerequisites for syncing are met."""
        issues = []

        # Check configuration
        config_issues = self.settings.validate_setup()
        issues.extend(config_issues.values())

        # Check API connectivity
        try:
            # Only validate API key if explicitly using API key mode (not currently supported)
            # In this project, supported modes are: no_auth, auto_oauth, manual_oauth.
            # If an API key mode is added in the future, extend UnifiedYouTubeClient accordingly.
            pass
        except Exception as e:
            issues.append(f"YouTube client connection failed: {e}")

        # Check download directory
        try:
            base_path = Path(self.settings.download.base_path)
            base_path.mkdir(parents=True, exist_ok=True)

            # Test write permissions
            test_file = base_path / ".yt_music_manager_cli_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            issues.append(f"Cannot write to download directory: {e}")

        return issues

    async def sync_playlists_batch(
        self, playlist_ids: List[str], batch_size: int = 3, dry_run: bool = False
    ) -> Dict[str, SyncResult]:
        """Sync multiple playlists in optimized batches with connection reuse."""
        if not playlist_ids:
            return {}

        logger.info(
            f"Starting batch sync of {len(playlist_ids)} playlists in batches of {batch_size}"
        )

        # Pre-fetch all playlist info to utilize API caching
        await self._prefetch_playlist_info(playlist_ids)

        results = {}

        # Process playlists in batches
        for i in range(0, len(playlist_ids), batch_size):
            batch = playlist_ids[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(playlist_ids) + batch_size - 1) // batch_size

            logger.info(
                f"Processing batch {batch_num}/{total_batches}: {len(batch)} playlists"
            )

            # Process current batch concurrently
            batch_tasks = [
                self._sync_playlist_task(playlist_id, dry_run) for playlist_id in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process batch results
            for playlist_id, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Exception syncing playlist {playlist_id}: {result}")
                    results[playlist_id] = SyncResult(
                        playlist_id=playlist_id, success=False, errors=[str(result)]
                    )
                else:
                    results[playlist_id] = result

            # Brief pause between batches to avoid overwhelming the API
            if i + batch_size < len(playlist_ids):
                await asyncio.sleep(0.5)

        # Save all changes once at the end
        if not dry_run:
            self.playlist_manager.save()

        # Log summary
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        total_downloaded = sum(r.items_downloaded for r in results.values())

        logger.info(
            f"Batch sync completed: {successful}/{len(playlist_ids)} successful, {total_downloaded} downloads"
        )

        return results

    async def _prefetch_playlist_info(self, playlist_ids: List[str]) -> None:
        """Pre-fetch playlist information to optimize caching."""
        logger.debug(f"Pre-fetching info for {len(playlist_ids)} playlists")

        # Create lightweight fetch tasks (without full video lists initially)
        lightweight_tasks = [
            self._fetch_playlist_lightweight(playlist_id)
            for playlist_id in playlist_ids
        ]

        # Execute lightweight fetches
        await asyncio.gather(*lightweight_tasks, return_exceptions=True)

        logger.debug("Pre-fetch completed")

    async def _fetch_playlist_lightweight(self, playlist_id: str) -> None:
        """Fetch lightweight playlist info asynchronously."""
        try:
            # This will populate the cache with basic info
            self._get_cached_playlist_info_lightweight(playlist_id)
        except Exception as e:
            logger.warning(f"Failed to pre-fetch playlist {playlist_id}: {e}")

    async def sync_playlist_optimized(
        self, playlist_id: str, dry_run: bool = False
    ) -> SyncResult:
        """Optimized single playlist sync with all performance enhancements."""
        start_time = datetime.now()
        result = SyncResult(playlist_id=playlist_id, success=False)

        try:
            self._current_playlist_id = playlist_id

            # Use cached playlist info
            current_playlist = self._get_cached_playlist_info(playlist_id)
            if not current_playlist:
                result.errors.append("Failed to fetch playlist information")
                return result

            # Plan sync with cached data
            sync_items, error = self.plan_sync(playlist_id, current_playlist)
            if error:
                result.errors.append(error)
                return result

            if not sync_items:
                logger.debug(f"No sync actions needed for playlist {playlist_id}")
                result.success = True
                return result

            result.items_processed = len(sync_items)

            if dry_run:
                logger.debug(f"DRY RUN: Would process {len(sync_items)} items")
                result.success = True
                return result

            # Use optimized batch downloads
            downloads_needed = [
                item for item in sync_items if item.action == SyncAction.DOWNLOAD
            ]
            if downloads_needed:
                logger.debug(
                    f"Using optimized batch download for {len(downloads_needed)} videos"
                )
                videos_to_download = [item.video_info for item in downloads_needed]

                # Create optimized playlist object
                download_playlist = PlaylistInfo(
                    playlist_id=current_playlist.playlist_id,
                    title=current_playlist.title,
                    description=current_playlist.description,
                    channel_title=current_playlist.channel_title,
                    channel_id=current_playlist.channel_id,
                    video_count=len(videos_to_download),
                    last_updated=current_playlist.last_updated,
                    thumbnail_url=current_playlist.thumbnail_url,
                    videos=videos_to_download,
                )

                # Use optimized download method
                download_results = (
                    await self.download_manager.download_playlist_optimized(
                        download_playlist, batch_size=5, max_concurrent_batches=2
                    )
                )

                for download_result in download_results:
                    if download_result.success:
                        result.items_downloaded += 1
                    else:
                        result.items_failed += 1
                        result.errors.append(
                            f"Download failed: {download_result.error_message}"
                        )

            # Handle other actions
            removals_needed = [
                item for item in sync_items if item.action == SyncAction.REMOVE
            ]
            if removals_needed:
                result.items_removed = self._process_removals(removals_needed)

            result.items_skipped = len(
                [item for item in sync_items if item.action == SyncAction.SKIP]
            )

            # Update state efficiently
            playlist_state = self.playlist_manager.get_playlist(playlist_id)
            if playlist_state:
                self.playlist_manager.update_sync_status(
                    playlist_id=playlist_id,
                    last_sync=datetime.now(timezone.utc).isoformat(),
                    download_count=playlist_state.download_count
                    + result.items_downloaded,
                    failed_count=playlist_state.failed_count + result.items_failed,
                    local_path=str(
                        self.download_manager.get_playlist_download_path(
                            current_playlist
                        )
                    ),
                    sync_errors=result.errors[-5:],  # Keep last 5 errors
                    save=True,
                )

            result.success = result.items_failed == 0

        except Exception as e:
            error_msg = f"Optimized sync failed for playlist {playlist_id}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self._current_playlist_id = None

        return result
