"""
Unified YouTube client that supports multiple authentication methods.
Automatically chooses the appropriate method based on configuration.
"""

import logging
from typing import List, Optional, Set, Tuple, Dict, Any

from .config import get_settings
from .youtube_api import YouTubeAPI, PlaylistInfo, VideoInfo, YouTubeAPIError
from .youtube_extractor import YouTubeExtractor
from .oauth_handler import YouTubeOAuth


logger = logging.getLogger(__name__)


class UnifiedYouTubeClient:
    """Unified client that supports no-auth, API key, and OAuth authentication."""

    def __init__(self):
        """Initialize the unified YouTube client."""
        self.settings = get_settings()
        self.auth_method = self.settings.youtube.auth_method
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the appropriate client based on auth method."""
        try:
            if self.auth_method == "no_auth":
                logger.debug("Using no-auth mode (public playlists only)")
                self.client = YouTubeExtractor()

            elif self.auth_method == "auto_oauth":
                logger.debug("Using automatic OAuth authentication")
                oauth_handler = YouTubeOAuth()
                if oauth_handler.setup_oauth():
                    self.client = oauth_handler.get_authenticated_youtube_api()
                    self.oauth_handler = oauth_handler
                else:
                    # Don't log error - let caller handle it
                    raise YouTubeAPIError("Automatic OAuth authentication failed")

            elif self.auth_method == "manual_oauth":
                logger.debug("Using manual OAuth authentication")
                oauth_handler = YouTubeOAuth()
                if oauth_handler.setup_oauth():
                    self.client = oauth_handler.get_authenticated_youtube_api()
                    self.oauth_handler = oauth_handler
                else:
                    # Don't log error - let caller handle it
                    raise YouTubeAPIError("Manual OAuth authentication failed")

            else:
                raise YouTubeAPIError(
                    f"Unknown authentication method: {self.auth_method}"
                )

        except YouTubeAPIError:
            # Re-raise without logging - caller will handle
            raise
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {e}")
            raise

    def extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from YouTube URL."""
        if hasattr(self.client, "extract_playlist_id"):
            return self.client.extract_playlist_id(url)
        else:
            # Fallback implementation
            import re

            patterns = [
                r"[?&]list=([^&]+)",
                r"youtube\.com/playlist\?list=([^&]+)",
                r"youtube\.com/watch\?.*list=([^&]+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

            if len(url) == 34 and url.startswith("PL"):
                return url

            raise YouTubeAPIError(f"Could not extract playlist ID from URL: {url}")

    def get_playlist_info(
        self, playlist_id: str, include_videos: bool = True
    ) -> PlaylistInfo:
        """Get playlist information."""
        try:
            return self.client.get_playlist_info(playlist_id, include_videos)
        except YouTubeAPIError as e:
            if "private" in str(e).lower() and self.auth_method == "no_auth":
                raise YouTubeAPIError(
                    f"This playlist appears to be private. "
                    f"Switch to 'oauth' authentication to access private playlists.\n\n"
                    f"To fix this:\n"
                    f"1. Change auth_method to 'oauth' in config/settings.toml\n"
                    f"2. Set up OAuth credentials\n"
                    f"3. Run: ytmm auth mode auto_oauth\n\n"
                    f"Or use public playlists only with 'no_auth' mode."
                )
            raise

    def get_playlist_videos(self, playlist_id: str) -> List[VideoInfo]:
        """Get all videos in a playlist."""
        return self.client.get_playlist_videos(playlist_id)

    def check_playlist_updates(
        self, playlist_id: str, last_check: Optional[str] = None
    ) -> Tuple[List[VideoInfo], Set[str]]:
        """Check for updates in a playlist."""
        return self.client.check_playlist_updates(playlist_id, last_check)

    def validate_api_access(self) -> bool:
        """Validate that the client can access YouTube."""
        try:
            if hasattr(self.client, "validate_api_key"):
                return self.client.validate_api_key()
            elif hasattr(self.client, "validate_playlist_access"):
                # For no-auth mode, try accessing a known public playlist
                test_playlist = (
                    "PLrAXtmRdnEQy5lCuBHjKr6PuYg7Q9YQ4n"  # YouTube's own playlist
                )
                return self.client.validate_playlist_access(test_playlist)
            else:
                return True  # Assume OAuth is working if we got this far
        except Exception as e:
            logger.error(f"API access validation failed: {e}")
            return False

    def get_quota_usage(self) -> Dict[str, int]:
        """Get quota usage information."""
        if hasattr(self.client, "get_quota_usage"):
            return self.client.get_quota_usage()
        else:
            # No quota tracking for no-auth mode
            return {"used": 0, "limit": "unlimited", "remaining": "unlimited"}

    def get_user_playlists(self) -> List[PlaylistInfo]:
        """Get user's own playlists (OAuth only)."""
        if self.auth_method != "oauth":
            raise YouTubeAPIError(
                "User playlists are only available with OAuth authentication"
            )

        if not hasattr(self, "oauth_handler"):
            raise YouTubeAPIError("OAuth handler not available")

        try:
            playlist_items = self.oauth_handler.get_user_playlists()
            playlists = []

            for item in playlist_items:
                snippet = item["snippet"]
                content_details = item.get("contentDetails", {})

                playlist_info = PlaylistInfo(
                    playlist_id=item["id"],
                    title=snippet["title"],
                    description=snippet.get("description", ""),
                    channel_title=snippet["channelTitle"],
                    channel_id=snippet["channelId"],
                    video_count=content_details.get("itemCount", 0),
                    last_updated=snippet.get("publishedAt", ""),
                    thumbnail_url=snippet.get("thumbnails", {})
                    .get("default", {})
                    .get("url", ""),
                    videos=[],
                )
                playlists.append(playlist_info)

            return playlists

        except Exception as e:
            raise YouTubeAPIError(f"Failed to get user playlists: {e}")

    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information."""
        info = {
            "method": self.auth_method,
            "authenticated": True,
            "can_access_private": self.auth_method in ["auto_oauth", "manual_oauth"],
            "can_access_user_playlists": self.auth_method
            in ["auto_oauth", "manual_oauth"],
        }

        if self.auth_method in ["auto_oauth", "manual_oauth"] and hasattr(
            self, "oauth_handler"
        ):
            auth_status = self.oauth_handler.get_auth_status()
            info.update(auth_status)

        return info

    # Backwards/compat-style alias some consumers may expect
    def get_auth_status(self) -> Dict[str, Any]:
        return self.get_auth_info()

    def is_playlist_accessible(self, playlist_id: str) -> bool:
        """Check if a playlist is accessible with current authentication."""
        try:
            # Try to get basic playlist info
            self.get_playlist_info(playlist_id, include_videos=False)
            return True
        except YouTubeAPIError as e:
            if "private" in str(e).lower():
                return False
            raise  # Re-raise other errors

    def get_supported_features(self) -> Dict[str, bool]:
        """Get information about what features are supported."""
        return {
            "public_playlists": True,
            "private_playlists": self.auth_method in ["auto_oauth", "manual_oauth"],
            "user_playlists": self.auth_method in ["auto_oauth", "manual_oauth"],
            "quota_tracking": self.auth_method in ["auto_oauth", "manual_oauth"],
            "rate_limiting": True,
            "batch_requests": self.auth_method in ["auto_oauth", "manual_oauth"],
        }


# Convenience function to get a configured client
def get_youtube_client() -> UnifiedYouTubeClient:
    """Get a configured YouTube client."""
    return UnifiedYouTubeClient()
