"""
YouTube playlist extraction without API key using yt-dlp.
Handles public playlists and video metadata extraction.
"""

import logging
import re
import sys
import io
from contextlib import redirect_stderr
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from .config import get_settings
from .youtube_api import VideoInfo, PlaylistInfo
from .exceptions import YouTubeAPIError
from .logging_utils import show_warning


logger = logging.getLogger(__name__)


class YouTubeExtractor:
    """Extract YouTube playlist information without API key using yt-dlp."""

    def __init__(self):
        """Initialize YouTube extractor."""
        self.settings = get_settings()
        self._setup_ydl_options()

    def _setup_ydl_options(self) -> None:
        """Set up yt-dlp options for metadata extraction only."""
        self.ydl_opts = {
            "quiet": True,
            "no_warnings": False,
            "extract_flat": False,  # We need full info
            "skip_download": True,  # Only extract metadata
            "ignoreerrors": True,  # Continue on individual video errors
            "user_agent": self.settings.advanced.user_agent,
            "socket_timeout": self.settings.advanced.connection_timeout,
        }

    def extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from YouTube URL."""
        # Handle different YouTube playlist URL formats
        patterns = [
            r"[?&]list=([^&]+)",
            r"youtube\.com/playlist\?list=([^&]+)",
            r"youtube\.com/watch\?.*list=([^&]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If no pattern matches, assume the URL is just the playlist ID
        if len(url) == 34 and url.startswith("PL"):
            return url

        raise YouTubeAPIError(f"Could not extract playlist ID from URL: {url}")

    def get_playlist_info(
        self, playlist_id: str, include_videos: bool = True
    ) -> PlaylistInfo:
        """Get playlist information using yt-dlp."""
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        logger.debug(f"Extracting playlist info for: {playlist_url}")

        try:
            # Capture stderr to prevent yt-dlp from printing directly to the console
            stderr_capture = io.StringIO()
            with redirect_stderr(stderr_capture):
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    # Extract playlist metadata
                    playlist_data = ydl.extract_info(playlist_url, download=False)

            # Process and display any captured warnings
            self._process_stderr(stderr_capture.getvalue())

            if not playlist_data:
                raise YouTubeAPIError(
                    f"Playlist not found or could not be extracted: {playlist_id}"
                )

            # Extract basic playlist info
            playlist_info = PlaylistInfo(
                playlist_id=playlist_id,
                title=playlist_data.get("title", "Unknown Playlist"),
                description=playlist_data.get("description", ""),
                channel_title=playlist_data.get("uploader", "Unknown Channel"),
                channel_id=playlist_data.get("uploader_id", ""),
                video_count=len(playlist_data.get("entries", [])),
                last_updated=datetime.now(timezone.utc).isoformat(),
                thumbnail_url=self._get_best_thumbnail(
                    playlist_data.get("thumbnails", [])
                ),
                videos=[],
            )

            if include_videos:
                playlist_info.videos = self._extract_video_info(
                    playlist_data.get("entries", [])
                )

            logger.debug(
                f"Extracted playlist '{playlist_info.title}' with {len(playlist_info.videos)} videos"
            )
            return playlist_info

        except ExtractorError as e:
            if "Private playlist" in str(e) or "private" in str(e).lower():
                raise YouTubeAPIError(
                    f"Playlist is private and cannot be accessed without authentication. "
                    f"Use 'oauth' authentication method to access private playlists."
                )
            elif "not found" in str(e).lower() or "doesn't exist" in str(e).lower():
                raise YouTubeAPIError(f"Playlist not found: {playlist_id}")
            else:
                raise YouTubeAPIError(f"Error extracting playlist: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"Unexpected error extracting playlist: {e}")

    def _extract_video_info(self, entries: List[Dict]) -> List[VideoInfo]:
        """Extract video information from playlist entries."""
        videos = []

        for entry in entries:
            if not entry:  # Skip unavailable videos
                continue

            try:
                # Handle both full extraction and flat extraction
                if entry.get("_type") == "url":
                    # This is a flat extraction, we need more info
                    video_id = entry.get("id", "")
                    if not video_id:
                        continue

                    # Extract individual video info
                    video_info = self._get_video_details(video_id)
                    if video_info:
                        videos.append(video_info)
                else:
                    # Full extraction available
                    video_info = self._parse_video_entry(entry)
                    if video_info:
                        videos.append(video_info)

            except Exception as e:
                logger.warning(f"Error processing video entry: {e}")
                continue

        return videos

    def _get_video_details(self, video_id: str) -> Optional[VideoInfo]:
        """Get detailed information for a single video."""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                video_data = ydl.extract_info(video_url, download=False)
                return self._parse_video_entry(video_data)
        except ExtractorError as e:
            # Handle cases where video is unavailable
            if "video unavailable" in str(e).lower():
                logger.warning(f"Video {video_id} is unavailable and will be skipped.")
            else:
                logger.warning(f"Error extracting video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting video {video_id}: {e}")
            return None

    def _parse_video_entry(self, entry: Dict) -> Optional[VideoInfo]:
        """Parse a video entry into VideoInfo object."""
        try:
            video_id = entry.get("id", "")
            if not video_id:
                return None

            # Handle view count (can be None for some videos)
            view_count = entry.get("view_count", 0)
            if view_count is None:
                view_count = 0

            # Handle like count (might not be available)
            like_count = entry.get("like_count")

            # Handle duration
            duration = entry.get("duration")
            if duration is not None:
                # Convert seconds to ISO 8601 duration format
                minutes, seconds = divmod(int(duration), 60)
                hours, minutes = divmod(minutes, 60)
                if hours > 0:
                    duration_str = f"PT{hours}H{minutes}M{seconds}S"
                else:
                    duration_str = f"PT{minutes}M{seconds}S"
            else:
                duration_str = "PT0S"

            video_info = VideoInfo(
                video_id=video_id,
                title=entry.get("title", "Unknown Title"),
                duration=duration_str,
                upload_date=entry.get("upload_date", ""),
                uploader=entry.get("uploader", "Unknown Channel"),
                uploader_id=entry.get("uploader_id", ""),
                view_count=int(view_count),
                like_count=int(like_count) if like_count is not None else None,
                description=entry.get("description", "")[
                    :500
                ],  # Limit description length
                thumbnail_url=self._get_best_thumbnail(entry.get("thumbnails", [])),
            )

            return video_info

        except Exception as e:
            logger.warning(f"Error parsing video entry: {e}")
            return None

    def _process_stderr(self, stderr: str):
        """Process and display warnings from yt-dlp."""
        lines = stderr.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Consolidate "unavailable videos" warnings
            if "unavailable videos are hidden" in line:
                # Extract the number of unavailable videos
                match = re.search(r"(\d+) unavailable videos are hidden", line)
                count = match.group(1) if match else "Some"
                show_warning(
                    f"YouTube said: {count} unavailable videos are hidden in this playlist."
                )
                continue

            # Show other important warnings
            if line.startswith("WARNING:") or line.startswith("ERROR:"):
                # Clean up the message for better readability
                message = line.replace("WARNING:", "").replace("ERROR:", "").strip()
                show_warning(message)

    def _get_best_thumbnail(self, thumbnails: List[Dict]) -> str:
        """Get the best quality thumbnail URL."""
        if not thumbnails:
            return ""

        # Prefer higher resolution thumbnails
        sorted_thumbnails = sorted(
            thumbnails,
            key=lambda x: (x.get("width", 0) * x.get("height", 0)),
            reverse=True,
        )

        return sorted_thumbnails[0].get("url", "") if sorted_thumbnails else ""

    def get_playlist_videos(self, playlist_id: str) -> List[VideoInfo]:
        """Get all videos in a playlist."""
        playlist_info = self.get_playlist_info(playlist_id, include_videos=True)
        return playlist_info.videos

    def check_playlist_updates(
        self, playlist_id: str, last_check: Optional[str] = None
    ) -> Tuple[List[VideoInfo], Set[str]]:
        """Check for updates in a playlist since last check."""
        logger.debug(f"Checking for updates in playlist {playlist_id}")

        current_videos = self.get_playlist_videos(playlist_id)
        current_video_ids = {video.video_id for video in current_videos}

        if last_check is None:
            # First time checking, all videos are new
            return current_videos, set()

        # For now, return all current videos as potentially new
        # This could be enhanced with proper state management
        return current_videos, set()

    def validate_playlist_access(self, playlist_id: str) -> bool:
        """Validate that a playlist can be accessed."""
        try:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                return info is not None
        except ExtractorError as e:
            if "Private playlist" in str(e) or "private" in str(e).lower():
                return False
            raise
        except Exception:
            return False

    def is_playlist_private(self, playlist_id: str) -> bool:
        """Check if a playlist is private."""
        try:
            self.validate_playlist_access(playlist_id)
            return False
        except YouTubeAPIError as e:
            if "private" in str(e).lower():
                return True
            return False
        except Exception:
            return False
