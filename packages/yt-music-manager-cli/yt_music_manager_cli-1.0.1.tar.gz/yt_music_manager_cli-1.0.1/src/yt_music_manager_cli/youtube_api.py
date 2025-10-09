"""
YouTube API integration for fetching playlist information and video metadata.
Handles authentication, rate limiting, and data extraction.
"""

import logging
import time
import hashlib
import pickle
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions

from .config import get_settings
from .exceptions import YouTubeAPIError


logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Information about a YouTube video."""

    video_id: str
    title: str
    duration: str
    upload_date: str
    uploader: str
    uploader_id: str
    view_count: int
    like_count: Optional[int] = None
    description: str = ""
    thumbnail_url: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "VideoInfo":
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class PlaylistInfo:
    """Information about a YouTube playlist."""

    playlist_id: str
    title: str
    description: str
    channel_title: str
    channel_id: str
    video_count: int
    last_updated: str
    thumbnail_url: str = ""
    videos: List[VideoInfo] | None = None

    def __post_init__(self):
        if self.videos is None:
            self.videos = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["videos"] = [video.to_dict() for video in self.videos]
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "PlaylistInfo":
        """Create instance from dictionary."""
        videos = [VideoInfo.from_dict(v) for v in data.get("videos", [])]
        data_copy = data.copy()
        data_copy["videos"] = videos
        return cls(**data_copy)


"""Note: YouTubeAPIError is imported from yt_music_manager_cli.exceptions to ensure a single
consistent exception type across the codebase."""


class YouTubeAPI:
    """YouTube Data API v3 client with rate limiting, error handling, and caching."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """Initialize YouTube API client."""
        self.settings = get_settings()
        # Some environments may omit api_key; keep attribute even if empty for clarity
        self.api_key = api_key or getattr(self.settings.youtube, "api_key", "")

        if not self.api_key:
            raise YouTubeAPIError("YouTube API key is required")

        try:
            self.service = build("youtube", "v3", developerKey=self.api_key)
        except google.auth.exceptions.GoogleAuthError as e:
            raise YouTubeAPIError(f"Failed to authenticate with YouTube API: {e}")

        # Rate limiting (YouTube API allows 10,000 units per day)
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        self.quota_used = 0
        self.daily_quota_limit = 10000

        # Caching setup
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=1)  # Cache for 1 hour by default
        self.playlist_cache_ttl = timedelta(hours=6)  # Playlists change less frequently

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        self.last_request_time = time.time()

    def _make_request(self, request, quota_cost: int = 1) -> Dict:
        """Make a request with error handling and rate limiting."""
        if self.quota_used + quota_cost > self.daily_quota_limit:
            raise YouTubeAPIError("Daily quota limit reached")

        self._wait_for_rate_limit()

        try:
            response = request.execute()
            self.quota_used += quota_cost
            logger.debug(
                f"API request successful, quota used: {self.quota_used}/{self.daily_quota_limit}"
            )
            return response
        except HttpError as e:
            error_details = json.loads(e.content.decode("utf-8"))
            error_message = error_details.get("error", {}).get(
                "message", "Unknown error"
            )

            if e.resp.status == 403:
                if "quota" in error_message.lower():
                    raise YouTubeAPIError("YouTube API quota exceeded")
                elif "key" in error_message.lower():
                    raise YouTubeAPIError("Invalid YouTube API key")
                else:
                    raise YouTubeAPIError(f"Access denied: {error_message}")
            elif e.resp.status == 404:
                raise YouTubeAPIError(f"Resource not found: {error_message}")
            else:
                raise YouTubeAPIError(f"API error ({e.resp.status}): {error_message}")
        except Exception as e:
            raise YouTubeAPIError(f"Unexpected error: {e}")

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate a cache key for the given endpoint and parameters."""
        # Create a unique key based on endpoint and sorted parameters
        param_str = json.dumps(params, sort_keys=True)
        key_data = f"{endpoint}:{param_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> Path:
        """Get the cache file path for a given cache key."""
        return self.cache_dir / f"{cache_key}.cache"

    def _is_cache_valid(self, cache_file: Path, ttl: timedelta) -> bool:
        """Check if a cache file is still valid."""
        if not cache_file.exists():
            return False

        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
        return datetime.now(timezone.utc) - file_time < ttl

    def _load_from_cache(self, cache_key: str, ttl: timedelta) -> Optional[Dict]:
        """Load data from cache if valid."""
        cache_file = self._get_cache_file(cache_key)

        if not self._is_cache_valid(cache_file, ttl):
            return None

        try:
            with open(cache_file, "rb") as f:
                data = pickle.load(f)
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            # Remove corrupted cache file
            try:
                cache_file.unlink()
            except Exception:
                pass
            return None

    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache."""
        cache_file = self._get_cache_file(cache_key)

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            logger.debug(f"Cached data for key: {cache_key[:8]}...")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _make_cached_request(
        self,
        endpoint: str,
        params: Dict,
        quota_cost: int = 1,
        ttl: Optional[timedelta] = None,
    ) -> Dict:
        """Make a cached API request."""
        if ttl is None:
            ttl = self.cache_ttl

        cache_key = self._get_cache_key(endpoint, params)

        # Try cache first
        cached_data = self._load_from_cache(cache_key, ttl)
        if cached_data is not None:
            return cached_data

        # Cache miss - make actual request
        if endpoint == "playlistItems":
            request = self.service.playlistItems().list(**params)
        elif endpoint == "playlists":
            request = self.service.playlists().list(**params)
        elif endpoint == "videos":
            request = self.service.videos().list(**params)
        else:
            raise YouTubeAPIError(f"Unknown endpoint: {endpoint}")

        response = self._make_request(request, quota_cost)

        # Save to cache
        self._save_to_cache(cache_key, response)

        return response

    def clear_cache(self, older_than: Optional[timedelta] = None) -> int:
        """Clear cache files, optionally only those older than specified time."""
        cleared_count = 0

        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                should_clear = False

                if older_than is None:
                    should_clear = True
                else:
                    file_time = datetime.fromtimestamp(
                        cache_file.stat().st_mtime, tz=timezone.utc
                    )
                    if datetime.now(timezone.utc) - file_time > older_than:
                        should_clear = True

                if should_clear:
                    try:
                        cache_file.unlink()
                        cleared_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to clear cache file {cache_file}: {e}")

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")

        logger.info(f"Cleared {cleared_count} cache files")
        return cleared_count

    def extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from YouTube URL."""
        import re

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
        """Get playlist information and optionally include videos."""
        logger.info(f"Fetching playlist info for ID: {playlist_id}")

        # Get playlist details with caching
        params = {
            "part": "snippet,status,contentDetails",
            "id": playlist_id,
            "maxResults": 1,
        }

        response = self._make_cached_request(
            "playlists", params, quota_cost=1, ttl=self.playlist_cache_ttl
        )

        if not response.get("items"):
            raise YouTubeAPIError(f"Playlist not found: {playlist_id}")

        playlist_data = response["items"][0]
        snippet = playlist_data["snippet"]
        content_details = playlist_data.get("contentDetails", {})

        playlist_info = PlaylistInfo(
            playlist_id=playlist_id,
            title=snippet["title"],
            description=snippet.get("description", ""),
            channel_title=snippet["channelTitle"],
            channel_id=snippet["channelId"],
            video_count=content_details.get("itemCount", 0),
            last_updated=datetime.now(timezone.utc).isoformat(),
            thumbnail_url=snippet.get("thumbnails", {})
            .get("default", {})
            .get("url", ""),
            videos=[],
        )

        if include_videos:
            playlist_info.videos = self.get_playlist_videos(playlist_id)

        logger.info(
            f"Playlist '{playlist_info.title}' has {playlist_info.video_count} videos"
        )
        return playlist_info

    def get_playlist_videos(self, playlist_id: str) -> List[VideoInfo]:
        """Get all videos in a playlist."""
        videos: List[VideoInfo] = []
        next_page_token = None

        while True:
            params = {
                "part": "snippet,contentDetails",
                "playlistId": playlist_id,
                "maxResults": 50,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            response = self._make_cached_request(
                "playlistItems", params, quota_cost=1, ttl=self.playlist_cache_ttl
            )

            video_ids = []
            video_snippets = {}

            for item in response.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                video_ids.append(video_id)
                video_snippets[video_id] = snippet

            # Get detailed video information
            if video_ids:
                video_details = self.get_video_details(video_ids)
                for video_detail in video_details:
                    video_id = video_detail.video_id
                    if video_id in video_snippets:
                        # Update with playlist-specific information
                        video_detail.title = video_snippets[video_id]["title"]
                        videos.append(video_detail)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        logger.info(f"Retrieved {len(videos)} videos from playlist {playlist_id}")
        return videos

    def get_video_details(self, video_ids: List[str]) -> List[VideoInfo]:
        """Get detailed information for multiple videos."""
        if not video_ids:
            return []

        # YouTube API allows up to 50 video IDs per request
        videos: List[VideoInfo] = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i : i + 50]

            params = {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(batch_ids),
            }

            response = self._make_cached_request(
                "videos", params, quota_cost=1, ttl=self.cache_ttl
            )

            for item in response.get("items", []):
                try:
                    snippet = item["snippet"]
                    content_details = item["contentDetails"]
                    statistics = item.get("statistics", {})

                    video_info = VideoInfo(
                        video_id=item["id"],
                        title=snippet["title"],
                        duration=content_details.get("duration", ""),
                        upload_date=snippet.get("publishedAt", ""),
                        uploader=snippet["channelTitle"],
                        uploader_id=snippet["channelId"],
                        view_count=int(statistics.get("viewCount", 0)),
                        like_count=(
                            int(statistics.get("likeCount", 0))
                            if statistics.get("likeCount")
                            else None
                        ),
                        description=snippet.get("description", ""),
                        thumbnail_url=snippet.get("thumbnails", {})
                        .get("default", {})
                        .get("url", ""),
                    )
                    videos.append(video_info)
                except (KeyError, ValueError) as e:
                    logger.warning(
                        f"Error parsing video data for ID {item.get('id')}: {e}"
                    )
                    continue

        return videos

    def check_playlist_updates(
        self, playlist_id: str, last_check: Optional[str] = None
    ) -> Tuple[List[VideoInfo], Set[str]]:
        """Check for updates in a playlist since last check."""
        logger.info(f"Checking for updates in playlist {playlist_id}")

        current_videos = self.get_playlist_videos(playlist_id)
        current_video_ids = {video.video_id for video in current_videos}

        if last_check is None:
            # First time checking, all videos are new
            return current_videos, set()

        # Load previous video IDs from cache or database
        # For now, we'll return all current videos as new
        # This would be enhanced with proper state management
        return current_videos, set()

    def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        try:
            request = self.service.search().list(
                part="snippet", q="test", maxResults=1, type="video"
            )
            self._make_request(request, quota_cost=100)
            return True
        except YouTubeAPIError:
            return False

    def get_quota_usage(self) -> Dict[str, int]:
        """Get current quota usage information."""
        return {
            "used": self.quota_used,
            "limit": self.daily_quota_limit,
            "remaining": self.daily_quota_limit - self.quota_used,
        }
