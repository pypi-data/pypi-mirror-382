"""
Playlist management and persistence.
Handles storing and retrieving playlist information and sync state.
"""

import logging
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

from .config import get_settings
from .youtube_api import PlaylistInfo, VideoInfo
from .exceptions import DataIntegrityError


logger = logging.getLogger(__name__)


@dataclass
class PlaylistState:
    """State information for a tracked playlist."""

    playlist_info: PlaylistInfo
    last_sync: Optional[str] = None
    download_count: int = 0
    failed_count: int = 0
    local_path: Optional[str] = None
    sync_errors: List[str] = None

    def __post_init__(self):
        if self.sync_errors is None:
            self.sync_errors = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["playlist_info"] = self.playlist_info.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "PlaylistState":
        """Create instance from dictionary."""
        playlist_info = PlaylistInfo.from_dict(data["playlist_info"])
        data_copy = data.copy()
        data_copy["playlist_info"] = playlist_info
        return cls(**data_copy)


class PlaylistManager:
    """Manages playlist information and sync state persistence."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize playlist manager."""
        self.settings = get_settings()

        if data_dir is None:
            # Create data directory in the same location as config
            data_dir = Path("data")

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.playlists_file = self.data_dir / "playlists.json"
        self.state_file = self.data_dir / "sync_state.json"

        self._playlists: Dict[str, PlaylistState] = {}
        self._load_playlists()

    def _load_playlists(self) -> None:
        """Load playlist data from disk with corruption recovery."""
        if not self.playlists_file.exists():
            logger.debug("No existing playlists file found")
            return

        # Try loading main file first
        try:
            success, data = self._load_json_with_validation(self.playlists_file)
            if success:
                self._parse_playlist_data(data)
                logger.debug(f"Loaded {len(self._playlists)} playlists from disk")
                return
        except Exception as e:
            logger.error(f"Error loading main playlists file: {e}")

        # Try backup file if main file failed
        backup_file = self.playlists_file.with_suffix(".json.backup")
        if backup_file.exists():
            logger.warning(
                "Main playlists file corrupted, attempting recovery from backup"
            )
            try:
                success, data = self._load_json_with_validation(backup_file)
                if success:
                    self._parse_playlist_data(data)
                    # Restore from backup
                    shutil.copy2(backup_file, self.playlists_file)
                    logger.info(
                        f"Successfully recovered {len(self._playlists)} playlists from backup"
                    )
                    return
            except Exception as e:
                logger.error(f"Error loading backup playlists file: {e}")

        # If all recovery attempts fail, start fresh but log the issue
        logger.warning(
            "Unable to recover playlist data, starting with empty playlist database"
        )
        self._playlists = {}
        # Create a corruption report
        self._create_corruption_report()

    def _load_json_with_validation(
        self, file_path: Path
    ) -> Tuple[bool, Optional[Dict]]:
        """Load and validate JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic integrity check
            if not content.strip():
                logger.error(f"File {file_path} is empty")
                return False, None

            # Parse JSON
            data = json.loads(content)

            # Validate structure
            if not isinstance(data, dict):
                logger.error(f"File {file_path} does not contain a valid JSON object")
                return False, None

            # Calculate and log checksum for integrity tracking
            checksum = hashlib.md5(content.encode()).hexdigest()
            logger.debug(f"Loaded {file_path} (checksum: {checksum[:8]})")

            return True, data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {file_path}: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            return False, None

    def _parse_playlist_data(self, data: Dict) -> None:
        """Parse and validate playlist data from JSON."""
        self._playlists = {}
        invalid_playlists = []

        for playlist_id, playlist_data in data.items():
            try:
                # Validate playlist_id format
                if not isinstance(playlist_id, str) or not playlist_id.strip():
                    logger.warning(f"Invalid playlist ID: {playlist_id}")
                    continue

                # Validate playlist data structure
                if not isinstance(playlist_data, dict):
                    logger.warning(f"Invalid data structure for playlist {playlist_id}")
                    continue

                playlist_state = PlaylistState.from_dict(playlist_data)

                # Additional validation
                if not playlist_state.playlist_info.playlist_id:
                    logger.warning(
                        f"Playlist {playlist_id} missing playlist_info.playlist_id"
                    )
                    continue

                self._playlists[playlist_id] = playlist_state

            except Exception as e:
                logger.error(f"Error loading playlist {playlist_id}: {e}")
                invalid_playlists.append(playlist_id)
                continue

        if invalid_playlists:
            logger.warning(
                f"Failed to load {len(invalid_playlists)} playlists: {invalid_playlists}"
            )

    def _create_corruption_report(self) -> None:
        """Create a report of corruption incidents."""
        report_file = self.data_dir / "corruption_report.json"

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "main_file_exists": self.playlists_file.exists(),
            "backup_file_exists": self.playlists_file.with_suffix(
                ".json.backup"
            ).exists(),
            "main_file_size": (
                self.playlists_file.stat().st_size
                if self.playlists_file.exists()
                else 0
            ),
            "backup_file_size": 0,
        }

        backup_file = self.playlists_file.with_suffix(".json.backup")
        if backup_file.exists():
            report["backup_file_size"] = backup_file.stat().st_size

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Created corruption report: {report_file}")
        except Exception as e:
            logger.error(f"Failed to create corruption report: {e}")

    def _save_playlists(self) -> None:
        """Save playlist data to disk with integrity checks."""
        try:
            data = {}
            for playlist_id, playlist_state in self._playlists.items():
                try:
                    playlist_dict = playlist_state.to_dict()
                    # Validate the serialized data
                    if not isinstance(playlist_dict, dict):
                        logger.error(
                            f"Invalid serialization for playlist {playlist_id}"
                        )
                        continue
                    data[playlist_id] = playlist_dict
                except Exception as e:
                    logger.error(f"Error serializing playlist {playlist_id}: {e}")
                    continue

            # Create backup of existing file before writing
            if self.playlists_file.exists():
                try:
                    backup_file = self.playlists_file.with_suffix(".json.backup")
                    shutil.copy2(self.playlists_file, backup_file)
                    logger.debug("Created backup of existing playlists file")
                except Exception as e:
                    logger.warning(f"Failed to create backup: {e}")

            # Write to temporary file first
            temp_file = self.playlists_file.with_suffix(".json.tmp")

            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Verify the written file
                success, verified_data = self._load_json_with_validation(temp_file)
                if not success:
                    raise DataIntegrityError("Failed to verify written playlist data")

                # Verify data integrity
                if len(verified_data) != len(data):
                    raise DataIntegrityError(
                        f"Data count mismatch: expected {len(data)}, got {len(verified_data)}"
                    )

                # Atomic move to final location
                temp_file.replace(self.playlists_file)

                logger.debug(f"Saved {len(self._playlists)} playlists to disk")

            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
                raise

        except Exception as e:
            logger.error(f"Error saving playlists file: {e}")
            raise

    def save(self) -> None:
        """Save all pending changes to disk."""
        self._save_playlists()

    def add_playlist(self, playlist_info: PlaylistInfo) -> None:
        """Add a new playlist to track."""
        playlist_state = PlaylistState(
            playlist_info=playlist_info,
            last_sync=None,
            download_count=0,
            failed_count=0,
            local_path=None,
            sync_errors=[],
        )

        self._playlists[playlist_info.playlist_id] = playlist_state
        self._save_playlists()

        logger.debug(
            f"Added playlist: {playlist_info.title} ({playlist_info.playlist_id})"
        )

    def remove_playlist(self, playlist_id: str) -> bool:
        """Remove a playlist from tracking."""
        if playlist_id in self._playlists:
            removed = self._playlists.pop(playlist_id)
            self._save_playlists()
            logger.debug(f"Removed playlist: {removed.playlist_info.title}")
            return True
        return False

    def get_playlist(self, playlist_id: str) -> Optional[PlaylistState]:
        """Get a specific playlist state."""
        return self._playlists.get(playlist_id)

    def get_all_playlists(self) -> Dict[str, PlaylistState]:
        """Get all tracked playlists."""
        return self._playlists.copy()

    def update_playlist_info(
        self, playlist_id: str, playlist_info: PlaylistInfo, save: bool = True
    ) -> None:
        """Update playlist information."""
        if playlist_id in self._playlists:
            self._playlists[playlist_id].playlist_info = playlist_info
            if save:
                self._save_playlists()
            logger.debug(f"Updated playlist info: {playlist_info.title}")
        else:
            logger.warning(f"Attempted to update non-existent playlist: {playlist_id}")

    def update_sync_status(
        self,
        playlist_id: str,
        last_sync: Optional[str] = None,
        download_count: Optional[int] = None,
        failed_count: Optional[int] = None,
        local_path: Optional[str] = None,
        sync_errors: Optional[List[str]] = None,
        save: bool = True,
    ) -> None:
        """Update sync status for a playlist."""
        if playlist_id not in self._playlists:
            logger.warning(
                f"Attempted to update sync status for non-existent playlist: {playlist_id}"
            )
            return

        playlist_state = self._playlists[playlist_id]

        if last_sync is not None:
            playlist_state.last_sync = last_sync
        if download_count is not None:
            playlist_state.download_count = download_count
        if failed_count is not None:
            playlist_state.failed_count = failed_count
        if local_path is not None:
            playlist_state.local_path = local_path
        if sync_errors is not None:
            playlist_state.sync_errors = sync_errors

        if save:
            self._save_playlists()
        logger.debug(
            f"Updated sync status for playlist: {playlist_state.playlist_info.title}"
        )

    def get_stale_playlists(self, max_age_hours: int = 24) -> List[PlaylistState]:
        """Get playlists that haven't been synced recently."""
        stale_playlists = []
        current_time = datetime.now(timezone.utc)

        for playlist_state in self._playlists.values():
            if playlist_state.last_sync is None:
                # Never synced
                stale_playlists.append(playlist_state)
            else:
                try:
                    last_sync_time = datetime.fromisoformat(playlist_state.last_sync)
                    age_hours = (current_time - last_sync_time).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        stale_playlists.append(playlist_state)
                except Exception as e:
                    logger.warning(f"Error parsing last sync time: {e}")
                    stale_playlists.append(playlist_state)

        return stale_playlists

    def get_playlist_by_url(self, url: str) -> Optional[PlaylistState]:
        """Get playlist by URL (searches through stored playlists)."""
        from .unified_youtube_client import get_youtube_client

        try:
            client = get_youtube_client()
            playlist_id = client.extract_playlist_id(url)
            return self.get_playlist(playlist_id)
        except Exception as e:
            logger.error(f"Error extracting playlist ID from URL: {e}")
            return None

    def export_playlists(self, export_path: Path) -> None:
        """Export playlist data to a file."""
        data = {"export_date": datetime.now(timezone.utc).isoformat(), "playlists": {}}

        for playlist_id, playlist_state in self._playlists.items():
            data["playlists"][playlist_id] = playlist_state.to_dict()

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self._playlists)} playlists to {export_path}")

    def import_playlists(self, import_path: Path, merge: bool = True) -> int:
        """Import playlist data from a file."""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            imported_count = 0
            playlists_data = data.get("playlists", {})

            for playlist_id, playlist_data in playlists_data.items():
                try:
                    if not merge and playlist_id in self._playlists:
                        logger.info(f"Skipping existing playlist: {playlist_id}")
                        continue

                    playlist_state = PlaylistState.from_dict(playlist_data)
                    self._playlists[playlist_id] = playlist_state
                    imported_count += 1

                except Exception as e:
                    logger.error(f"Error importing playlist {playlist_id}: {e}")
                    continue

            if imported_count > 0:
                self._save_playlists()
                logger.info(f"Imported {imported_count} playlists from {import_path}")

            return imported_count

        except Exception as e:
            logger.error(f"Error importing playlists from {import_path}: {e}")
            raise

    def get_statistics(self) -> Dict[str, int]:
        """Get overall statistics."""
        stats = {
            "total_playlists": len(self._playlists),
            "total_videos": 0,
            "total_downloaded": 0,
            "total_failed": 0,
            "never_synced": 0,
            "recently_synced": 0,
        }

        current_time = datetime.now(timezone.utc)

        for playlist_state in self._playlists.values():
            stats["total_videos"] += len(playlist_state.playlist_info.videos)
            stats["total_downloaded"] += playlist_state.download_count
            stats["total_failed"] += playlist_state.failed_count

            if playlist_state.last_sync is None:
                stats["never_synced"] += 1
            else:
                try:
                    last_sync_time = datetime.fromisoformat(playlist_state.last_sync)
                    age_hours = (current_time - last_sync_time).total_seconds() / 3600
                    if age_hours < 24:
                        stats["recently_synced"] += 1
                except Exception:
                    pass

        return stats

    def cleanup_orphaned_data(self) -> int:
        """Clean up data for playlists that no longer exist."""
        cleaned_count = 0

        # Get all known playlist directories
        known_paths = set()
        for playlist_state in self._playlists.values():
            if playlist_state.local_path:
                known_paths.add(Path(playlist_state.local_path))

        # Check download directory for orphaned folders
        try:
            download_dir = Path(self.settings.download.output_dir)
            if download_dir.exists():
                for item in download_dir.iterdir():
                    if item.is_dir() and item not in known_paths:
                        # Check if this directory might be from a deleted playlist
                        if self._is_likely_playlist_directory(item):
                            logger.info(f"Found orphaned directory: {item}")
                            # Don't auto-delete, just log for now
                            # Could implement a --cleanup flag to actually remove
                            cleaned_count += 1
        except Exception as e:
            logger.error(f"Error during orphaned data cleanup: {e}")

        return cleaned_count

    def _is_likely_playlist_directory(self, path: Path) -> bool:
        """Check if a directory looks like it was created by this app."""
        # Look for common patterns that indicate this was a playlist directory
        indicators = [
            any(
                f.suffix.lower() in [".mp3", ".m4a", ".webm", ".opus"]
                for f in path.glob("*")
            ),
            any(
                f.name.endswith(".part") for f in path.glob("*")
            ),  # Incomplete downloads
            (path / ".playlist_info").exists(),  # Metadata file
        ]
        return any(indicators)

    def detect_incomplete_downloads(self) -> List[Dict[str, str]]:
        """Detect incomplete or corrupted downloads."""
        incomplete_files = []

        for playlist_id, playlist_state in self._playlists.items():
            if not playlist_state.local_path:
                continue

            local_path = Path(playlist_state.local_path)
            if not local_path.exists():
                continue

            try:
                # Check for .part files (incomplete downloads)
                part_files = list(local_path.glob("*.part"))
                for part_file in part_files:
                    incomplete_files.append(
                        {
                            "type": "incomplete",
                            "playlist_id": playlist_id,
                            "file_path": str(part_file),
                            "reason": "Partial download file found",
                        }
                    )

                # Check for very small files (likely corrupted)
                for audio_file in local_path.glob("*"):
                    if audio_file.suffix.lower() in [".mp3", ".m4a", ".webm", ".opus"]:
                        if audio_file.stat().st_size < 1024:  # Less than 1KB
                            incomplete_files.append(
                                {
                                    "type": "corrupted",
                                    "playlist_id": playlist_id,
                                    "file_path": str(audio_file),
                                    "reason": f"File too small: {audio_file.stat().st_size} bytes",
                                }
                            )

                # Check for files with invalid extensions from failed downloads
                suspicious_files = list(local_path.glob("*.unknown")) + list(
                    local_path.glob("*.tmp")
                )
                for sus_file in suspicious_files:
                    incomplete_files.append(
                        {
                            "type": "suspicious",
                            "playlist_id": playlist_id,
                            "file_path": str(sus_file),
                            "reason": f"Suspicious file extension: {sus_file.suffix}",
                        }
                    )

            except Exception as e:
                logger.error(
                    f"Error checking downloads for playlist {playlist_id}: {e}"
                )
                continue

        return incomplete_files

    def cleanup_incomplete_downloads(self, dry_run: bool = True) -> int:
        """Clean up incomplete and corrupted downloads."""
        incomplete_files = self.detect_incomplete_downloads()
        cleaned_count = 0

        for file_info in incomplete_files:
            file_path = Path(file_info["file_path"])

            if dry_run:
                logger.info(
                    f"Would clean up {file_info['type']} file: {file_path} ({file_info['reason']})"
                )
                cleaned_count += 1
            else:
                try:
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"Cleaned up {file_info['type']} file: {file_path}")
                        cleaned_count += 1
                except Exception as e:
                    logger.error(f"Failed to clean up {file_path}: {e}")

        return cleaned_count

    def verify_data_integrity(self) -> Dict[str, Any]:
        """Perform comprehensive data integrity check."""
        integrity_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "playlist_file_status": "ok",
            "backup_file_status": "ok",
            "playlists_loaded": len(self._playlists),
            "incomplete_downloads": 0,
            "orphaned_directories": 0,
            "errors": [],
        }

        try:
            # Check main playlist file
            if self.playlists_file.exists():
                success, _ = self._load_json_with_validation(self.playlists_file)
                if not success:
                    integrity_report["playlist_file_status"] = "corrupted"
                    integrity_report["errors"].append("Main playlist file is corrupted")
            else:
                integrity_report["playlist_file_status"] = "missing"
                integrity_report["errors"].append("Main playlist file is missing")

            # Check backup file
            backup_file = self.playlists_file.with_suffix(".json.backup")
            if backup_file.exists():
                success, _ = self._load_json_with_validation(backup_file)
                if not success:
                    integrity_report["backup_file_status"] = "corrupted"
                    integrity_report["errors"].append(
                        "Backup playlist file is corrupted"
                    )
            else:
                integrity_report["backup_file_status"] = "missing"

            # Check for incomplete downloads
            incomplete_files = self.detect_incomplete_downloads()
            integrity_report["incomplete_downloads"] = len(incomplete_files)

            # Check for orphaned data
            integrity_report["orphaned_directories"] = self.cleanup_orphaned_data()

        except Exception as e:
            integrity_report["errors"].append(f"Error during integrity check: {str(e)}")

        return integrity_report
