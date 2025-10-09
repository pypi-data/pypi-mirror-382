"""
Download manager for YouTube videos using yt-dlp.
Handles audio extraction, file organization, and concurrent downloads.
"""

import logging
import os
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import json
import re
import shutil

import yt_dlp
from yt_dlp.utils import DownloadError

from .config import get_settings
from .youtube_api import VideoInfo, PlaylistInfo
from .logging_utils import show_warning


logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result of a download operation."""

    video_id: str
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None


@dataclass
class DownloadProgress:
    """Progress information for a download."""

    video_id: str
    title: str
    status: str  # 'downloading', 'converting', 'completed', 'error'
    percent: float = 0.0
    speed: Optional[str] = None
    eta: Optional[str] = None
    total_bytes_str: Optional[str] = None
    file_path: Optional[str] = None


class DownloadManager:
    """Manages YouTube video downloads with yt-dlp."""

    def __init__(
        self,
        ffmpeg_available: bool,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ):
        """Initialize download manager."""
        self.settings = get_settings()
        self.progress_callback = progress_callback
        self.active_downloads: Dict[str, DownloadProgress] = {}
        self._ffmpeg_available = ffmpeg_available
        self._setup_download_options()

    def _setup_download_options(self) -> None:
        """Set up yt-dlp options based on configuration."""
        base_path = Path(self.settings.download.base_path)
        base_path.mkdir(parents=True, exist_ok=True)

        self.ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(base_path / "%(playlist)s" / "%(title)s.%(ext)s"),
            "extractaudio": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "ignoreerrors": True,
            "no_warnings": False,
            "quiet": True,
            "verbose": False,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "retries": self.settings.advanced.retry_attempts,
            "socket_timeout": self.settings.advanced.connection_timeout,
            "user_agent": self.settings.advanced.user_agent,
        }

        # Conditionally add postprocessors if ffmpeg is available
        if self._ffmpeg_available:
            self.ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.settings.download.audio_format,
                    "preferredquality": self.settings.download.audio_quality,
                },
                {
                    "key": "FFmpegMetadata",
                },
            ]
            # Set audio format and quality only if converting
            self.ydl_opts["audioformat"] = self.settings.download.audio_format
            self.ydl_opts["audioquality"] = self.settings.download.audio_quality
        else:
            # If ffmpeg is not available, download the best audio directly
            # and do not attempt to convert or embed metadata.
            self.ydl_opts["audioformat"] = None  # Let yt-dlp decide the format

    def _progress_hook(self, progress_info: Dict[str, Any]) -> None:
        """Handle download progress updates."""
        if progress_info["status"] == "downloading":
            # Extract video ID from filename or URL
            video_id = self._extract_video_id_from_progress(progress_info)
            if not video_id:
                return

            # Get current progress or create new one
            current_progress = self.active_downloads.get(
                video_id,
                DownloadProgress(
                    video_id=video_id,
                    title=progress_info.get("info_dict", {}).get("title", "Unknown"),
                    status="downloading",
                ),
            )

            # Update progress information
            current_progress.status = "downloading"
            current_progress.percent = progress_info.get("_percent_str", "0%").replace(
                "%", ""
            )
            try:
                current_progress.percent = float(current_progress.percent)
            except (ValueError, TypeError):
                current_progress.percent = 0.0

            current_progress.speed = progress_info.get("_speed_str", None)
            current_progress.eta = progress_info.get("_eta_str", None)
            current_progress.total_bytes_str = progress_info.get(
                "_total_bytes_str", None
            )

            self.active_downloads[video_id] = current_progress

            if self.progress_callback:
                self.progress_callback(current_progress)

        elif progress_info["status"] == "finished":
            video_id = self._extract_video_id_from_progress(progress_info)
            if video_id and video_id in self.active_downloads:
                self.active_downloads[video_id].status = "converting"
                self.active_downloads[video_id].percent = 100.0
                self.active_downloads[video_id].file_path = progress_info.get(
                    "filename"
                )

                if self.progress_callback:
                    self.progress_callback(self.active_downloads[video_id])

    def _postprocessor_hook(self, progress_info: Dict[str, Any]) -> None:
        """Handle post-processing progress updates."""
        if progress_info.get("status") == "finished":
            # Try to find the corresponding video ID
            info_dict = progress_info.get("info_dict", {})
            video_id = info_dict.get("id")

            if video_id and video_id in self.active_downloads:
                self.active_downloads[video_id].status = "completed"
                self.active_downloads[video_id].file_path = progress_info.get(
                    "filepath"
                )

                if self.progress_callback:
                    self.progress_callback(self.active_downloads[video_id])

    def _extract_video_id_from_progress(
        self, progress_info: Dict[str, Any]
    ) -> Optional[str]:
        """Extract video ID from progress information."""
        # Try to get from info_dict first
        info_dict = progress_info.get("info_dict", {})
        video_id = info_dict.get("id")
        if video_id:
            return video_id

        # Try to extract from filename
        filename = progress_info.get("filename", "")
        if filename:
            # Look for video ID pattern in filename
            match = re.search(r"([a-zA-Z0-9_-]{11})", filename)
            if match:
                return match.group(1)

        return None

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for file system compatibility."""
        # Remove or replace invalid characters
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Remove multiple consecutive underscores
        filename = re.sub(r"_+", "_", filename)

        # Trim whitespace and dots from ends
        filename = filename.strip(". ")

        # Ensure filename is not too long (255 bytes limit on most systems)
        if len(filename.encode("utf-8")) > 255:
            filename = filename[:200] + "..."

        return filename

    def get_playlist_download_path(self, playlist_info: PlaylistInfo) -> Path:
        """Get the download path for a playlist."""
        base_path = Path(self.settings.download.base_path)
        playlist_name = self.sanitize_filename(playlist_info.title)
        return base_path / playlist_name

    def get_video_file_path(
        self, video_info: VideoInfo, playlist_info: PlaylistInfo
    ) -> Path:
        """Get the expected file path for a downloaded video."""
        playlist_path = self.get_playlist_download_path(playlist_info)
        filename = self.sanitize_filename(video_info.title)
        return playlist_path / f"{filename}.{self.settings.download.audio_format}"

    def download_video(
        self, video_info: VideoInfo, playlist_info: PlaylistInfo
    ) -> DownloadResult:
        """Download a single video."""
        video_url = f"https://www.youtube.com/watch?v={video_info.video_id}"
        playlist_path = self.get_playlist_download_path(playlist_info)

        # Create playlist directory
        playlist_path.mkdir(parents=True, exist_ok=True)

        # Set up custom output template for this download
        ydl_opts = self.ydl_opts.copy()
        ydl_opts["outtmpl"] = str(
            playlist_path / f"{self.sanitize_filename(video_info.title)}.%(ext)s"
        )

        # Initialize progress tracking
        progress = DownloadProgress(
            video_id=video_info.video_id, title=video_info.title, status="downloading"
        )
        self.active_downloads[video_info.video_id] = progress

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug(
                    f"Starting download: {video_info.title} ({video_info.video_id})"
                )
                ydl.download([video_url])

            # Find the downloaded file, which may have a different extension if ffmpeg is missing
            expected_path = self.get_video_file_path(video_info, playlist_info)

            # Search for any potential audio file, preferring the configured format
            similar_files = list(
                playlist_path.glob(f"{self.sanitize_filename(video_info.title)}.*")
            )

            # List of potential audio extensions, including common fallbacks
            # Use a set for efficient lookup
            allowed_extensions = {
                f".{self.settings.download.audio_format}",
                ".m4a",
                ".webm",
                ".mp3",
                ".aac",
                ".ogg",
                ".wav",
                ".flac",
            }

            found_file = None

            # Prioritize the expected file
            if expected_path.exists():
                found_file = expected_path
            else:
                # Search for other allowed extensions
                for f in similar_files:
                    if f.suffix.lower() in allowed_extensions:
                        found_file = f
                        break

            # If no match, take the first similar file as a fallback, if any
            if not found_file and similar_files:
                # Filter out non-audio/video files just in case
                likely_audio = [
                    f
                    for f in similar_files
                    if f.suffix.lower() not in [".json", ".txt", ".jpg", ".part"]
                ]
                if likely_audio:
                    found_file = likely_audio[0]

            if found_file and found_file.exists():
                file_path = str(found_file)
                file_size = found_file.stat().st_size
            else:
                # This error is now more informative
                raise FileNotFoundError(
                    "Downloaded file not found. This can happen if the video is unavailable, "
                    "or if there was a network error during download. "
                    "Check the logs for details from yt-dlp."
                )

            # Update final progress
            progress.status = "completed"
            progress.percent = 100.0
            progress.file_path = file_path
            self.active_downloads[video_info.video_id] = progress

            if self.progress_callback:
                self.progress_callback(progress)

            logger.debug(f"Successfully downloaded: {video_info.title}")
            return DownloadResult(
                video_id=video_info.video_id,
                success=True,
                file_path=file_path,
                file_size=file_size,
            )

        except DownloadError as e:
            error_msg = f"yt-dlp error: {str(e)}"
            logger.error(f"Download failed for {video_info.title}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Download failed for {video_info.title}: {error_msg}")
        finally:
            # Clean up progress tracking
            if video_info.video_id in self.active_downloads:
                if self.active_downloads[video_info.video_id].status != "completed":
                    self.active_downloads[video_info.video_id].status = "error"
                    if self.progress_callback:
                        self.progress_callback(
                            self.active_downloads[video_info.video_id]
                        )

        return DownloadResult(
            video_id=video_info.video_id, success=False, error_message=error_msg
        )

    async def download_playlist(
        self, playlist_info: PlaylistInfo, max_concurrent: Optional[int] = None
    ) -> List[DownloadResult]:
        """Download all videos in a playlist with concurrent downloads."""
        if max_concurrent is None:
            max_concurrent = self.settings.sync.max_concurrent_downloads

        logger.debug(
            f"Starting download of playlist: {playlist_info.title} ({len(playlist_info.videos)} videos)"
        )

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(video_info: VideoInfo) -> DownloadResult:
            async with semaphore:
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    return await loop.run_in_executor(
                        executor, self.download_video, video_info, playlist_info
                    )

        # Create download tasks
        tasks = [download_with_semaphore(video) for video in playlist_info.videos]

        # Execute downloads and collect results
        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            results.append(result)

        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.debug(
            f"Playlist download completed: {successful} successful, {failed} failed"
        )

        return results

    def verify_download(
        self, video_info: VideoInfo, playlist_info: PlaylistInfo
    ) -> bool:
        """Verify that a video has been downloaded successfully."""
        file_path = self.get_video_file_path(video_info, playlist_info)

        if not file_path.exists():
            return False

        # Check if file is not empty
        if file_path.stat().st_size == 0:
            logger.warning(f"Downloaded file is empty: {file_path}")
            return False

        # Additional verification could include checking file format, duration, etc.
        return True

    def get_downloaded_videos(self, playlist_info: PlaylistInfo) -> List[Path]:
        """Get list of all downloaded video files for a playlist."""
        playlist_path = self.get_playlist_download_path(playlist_info)

        if not playlist_path.exists():
            return []

        audio_extensions = [".mp3", ".aac", ".ogg", ".wav", ".flac", ".m4a", ".webm"]
        downloaded_files = []

        for file_path in playlist_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                downloaded_files.append(file_path)

        return downloaded_files

    def cleanup_failed_downloads(self, playlist_info: PlaylistInfo) -> None:
        """Clean up partial or corrupted download files."""
        playlist_path = self.get_playlist_download_path(playlist_info)

        if not playlist_path.exists():
            return

        # Remove temporary files and empty files
        for file_path in playlist_path.iterdir():
            if file_path.is_file():
                if (
                    file_path.suffix in [".part", ".ytdl", ".temp"]
                    or file_path.stat().st_size == 0
                ):
                    try:
                        file_path.unlink()
                        logger.info(f"Cleaned up failed download: {file_path.name}")
                    except OSError as e:
                        logger.error(f"Failed to clean up file {file_path}: {e}")

    def get_active_downloads(self) -> Dict[str, DownloadProgress]:
        """Get currently active downloads."""
        return self.active_downloads.copy()

    def cancel_download(self, video_id: str) -> bool:
        """Cancel an active download (limited support)."""
        if video_id in self.active_downloads:
            self.active_downloads[video_id].status = "cancelled"
            # Note: yt-dlp doesn't have easy cancellation support
            # This mainly updates the status for UI purposes
            return True
        return False

    def batch_download_videos(
        self, video_batch: List[VideoInfo], playlist_info: PlaylistInfo
    ) -> List[DownloadResult]:
        """Download multiple videos using yt-dlp's batch capabilities for better performance."""
        if not video_batch:
            return []

        # Group videos by similar parameters to optimize yt-dlp sessions
        playlist_path = self.get_playlist_download_path(playlist_info)
        playlist_path.mkdir(parents=True, exist_ok=True)

        # Create URL list for batch processing
        video_urls = [
            f"https://www.youtube.com/watch?v={video.video_id}" for video in video_batch
        ]

        # Setup batch yt-dlp options
        batch_opts = self.ydl_opts.copy()
        batch_opts["outtmpl"] = str(playlist_path / "%(title)s.%(ext)s")

        # Initialize progress tracking for all videos
        results = []
        for video in video_batch:
            progress = DownloadProgress(
                video_id=video.video_id, title=video.title, status="queued"
            )
            self.active_downloads[video.video_id] = progress

        try:
            with yt_dlp.YoutubeDL(batch_opts) as ydl:
                logger.info(f"Starting batch download of {len(video_batch)} videos")
                ydl.download(video_urls)

            # Verify downloaded files and create results
            for video in video_batch:
                if self.verify_download(video, playlist_info):
                    file_path = self.get_video_file_path(video, playlist_info)
                    results.append(
                        DownloadResult(
                            video_id=video.video_id,
                            success=True,
                            file_path=str(file_path),
                            file_size=(
                                file_path.stat().st_size if file_path.exists() else 0
                            ),
                        )
                    )
                    # Update progress
                    if video.video_id in self.active_downloads:
                        self.active_downloads[video.video_id].status = "completed"
                        if self.progress_callback:
                            self.progress_callback(
                                self.active_downloads[video.video_id]
                            )
                else:
                    results.append(
                        DownloadResult(
                            video_id=video.video_id,
                            success=False,
                            error_message="Download verification failed",
                        )
                    )
                    # Update progress
                    if video.video_id in self.active_downloads:
                        self.active_downloads[video.video_id].status = "error"
                        if self.progress_callback:
                            self.progress_callback(
                                self.active_downloads[video.video_id]
                            )

        except Exception as e:
            logger.error(f"Batch download failed: {e}")
            # Mark all as failed
            for video in video_batch:
                results.append(
                    DownloadResult(
                        video_id=video.video_id, success=False, error_message=str(e)
                    )
                )
                # Update progress
                if video.video_id in self.active_downloads:
                    self.active_downloads[video.video_id].status = "error"
                    if self.progress_callback:
                        self.progress_callback(self.active_downloads[video.video_id])

        return results

    async def download_playlist_optimized(
        self,
        playlist_info: PlaylistInfo,
        batch_size: int = 5,
        max_concurrent_batches: int = 2,
    ) -> List[DownloadResult]:
        """Download playlist using optimized batch processing."""
        logger.info(f"Starting optimized download of playlist: {playlist_info.title}")

        # Filter out already downloaded videos
        remaining_videos = []
        for video in playlist_info.videos:
            if not self.verify_download(video, playlist_info):
                remaining_videos.append(video)

        if not remaining_videos:
            logger.info("All videos already downloaded")
            return []

        logger.info(
            f"Downloading {len(remaining_videos)} remaining videos in batches of {batch_size}"
        )

        # Split videos into batches
        video_batches = [
            remaining_videos[i : i + batch_size]
            for i in range(0, len(remaining_videos), batch_size)
        ]

        results = []
        semaphore = asyncio.Semaphore(max_concurrent_batches)

        async def process_batch(batch: List[VideoInfo]) -> List[DownloadResult]:
            async with semaphore:
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    return await loop.run_in_executor(
                        executor, self.batch_download_videos, batch, playlist_info
                    )

        # Process batches concurrently
        batch_tasks = [process_batch(batch) for batch in video_batches]

        for completed_task in asyncio.as_completed(batch_tasks):
            batch_results = await completed_task
            results.extend(batch_results)

        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.info(
            f"Optimized playlist download completed: {successful} successful, {failed} failed"
        )

        return results

    def get_download_statistics(self, playlist_info: PlaylistInfo) -> Dict[str, int]:
        """Get download statistics for a playlist."""
        downloaded_files = self.get_downloaded_videos(playlist_info)
        total_videos = len(playlist_info.videos)
        downloaded_count = len(downloaded_files)

        # Calculate total file size
        total_size = sum(file.stat().st_size for file in downloaded_files)

        return {
            "total_videos": total_videos,
            "downloaded_count": downloaded_count,
            "pending_count": total_videos - downloaded_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "completion_percentage": (
                round((downloaded_count / total_videos) * 100, 1)
                if total_videos > 0
                else 0
            ),
        }
