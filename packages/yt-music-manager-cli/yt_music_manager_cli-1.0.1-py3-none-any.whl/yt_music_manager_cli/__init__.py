"""
YT Music Manager CLI (YTMM CLI) - YouTube Playlist Synchronizer
A CLI tool for downloading and syncing YouTube & Youtube Music playlists. (YT Music Manager CLI)
"""

__version__ = "1.0.1"
__author__ = "Sukarth Acharya"
__email__ = "sukarthacharya@gmail.com"

from .config import Settings
from .download_manager import DownloadManager
from .playlist_manager import PlaylistManager
from .sync_engine import SyncEngine

__all__ = [
    "Settings",
    "DownloadManager",
    "PlaylistManager",
    "SyncEngine",
]
