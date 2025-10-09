"""
Logging configuration and utilities for YT Music Manager CLI (YTMM CLI).
Provides structured logging with file rotation and rich console output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from .config import get_settings


# Custom theme for rich console
YT_MUSIC_MANAGER_CLI_THEME = Theme(
    {
        "info": "blue",
        "warning": "yellow",
        "error": "red",
        "critical": "bold red",
        "success": "green",
        "progress": "cyan",
        "highlight": "magenta",
    }
)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "exc_info",
                "exc_text",
                "stack_info",
                "getMessage",
            ]
        }

        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry, ensure_ascii=False)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to the log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class YTMusicManagerCLILogger:
    """Central logging manager for YT Music Manager CLI."""

    def __init__(self):
        self.settings = get_settings()
        # Use same robust console settings as CLI for cross-platform compatibility
        # Console creation with defensive fallback (tests may monkeypatch Console with limited signature)
        try:
            self.console = Console(
                theme=YT_MUSIC_MANAGER_CLI_THEME,
                force_terminal=True,
                legacy_windows=True,
                color_system="standard",
            )
        except TypeError:
            # Fallback minimal console
            self.console = Console()
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Create logs directory
        log_file_path = Path(self.settings.logging.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.settings.logging.level))

        # Clear existing handlers
        root_logger.handlers.clear()

        # File handler with rotation
        file_handler = self._create_file_handler(log_file_path)
        root_logger.addHandler(file_handler)

        # Console handler with Rich
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)

        # Set up specific logger levels
        self._configure_third_party_loggers()

        # Log startup message
        logger = self.get_logger("yt_music_manager_cli.logging")
        logger.debug("Logging system initialized")
        logger.debug(f"Log level: {self.settings.logging.level}")
        logger.debug(f"Log file: {log_file_path}")

    def _create_file_handler(self, log_file_path: Path) -> logging.Handler:
        """Create rotating file handler."""
        max_bytes = self._parse_size(self.settings.logging.max_log_size)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=self.settings.logging.backup_count,
            encoding="utf-8",
        )

        # Use JSON formatter for file logs
        file_handler.setFormatter(JsonFormatter())
        return file_handler

    def _create_console_handler(self) -> logging.Handler:
        """Create rich console handler with optimal cross-platform settings."""
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,  # Enable Rich markup for consistent styling
            highlighter=None,  # Disable highlighting to avoid conflicts
        )

        # Don't set custom formatter - let RichHandler handle the styling
        return console_handler

    def _configure_third_party_loggers(self) -> None:
        """Configure log levels for third-party libraries."""
        third_party_configs = {
            "yt_dlp": logging.WARNING,
            "googleapiclient": logging.WARNING,
            "google.auth": logging.WARNING,
            "urllib3": logging.WARNING,
            "requests": logging.WARNING,
        }

        for logger_name, level in third_party_configs.items():
            logging.getLogger(logger_name).setLevel(level)

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper().strip()

        multipliers = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 * 1024,
            "GB": 1024 * 1024 * 1024,
        }

        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number_part = size_str[: -len(suffix)]
                try:
                    return int(float(number_part) * multiplier)
                except ValueError:
                    break

        # Default to 10MB if parsing fails
        return 10 * 1024 * 1024

    def get_logger(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> logging.Logger:
        """Get a logger with optional context."""
        if name not in self._loggers:
            logger = logging.getLogger(name)

            if context:
                logger.addFilter(ContextFilter(context))

            self._loggers[name] = logger

        return self._loggers[name]

    def add_context(self, logger_name: str, context: Dict[str, Any]) -> None:
        """Add context to an existing logger."""
        if logger_name in self._loggers:
            self._loggers[logger_name].addFilter(ContextFilter(context))

    def log_exception(
        self,
        logger_name: str,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an exception with full context."""
        logger = self.get_logger(logger_name)

        extra_info = context or {}
        extra_info.update(
            {
                "exception_type": type(exception).__name__,
                "exception_module": type(exception).__module__,
            }
        )

        logger.error(
            f"Exception occurred: {str(exception)}", exc_info=True, extra=extra_info
        )

    def log_api_call(
        self,
        logger_name: str,
        api_name: str,
        endpoint: str,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        quota_cost: Optional[int] = None,
    ) -> None:
        """Log API call information."""
        logger = self.get_logger(logger_name)

        extra_info = {
            "api_name": api_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": int(response_time * 1000) if response_time else None,
            "quota_cost": quota_cost,
        }

        message = f"{api_name} API call to {endpoint}"
        if status_code:
            message += f" (status: {status_code})"
        if response_time:
            message += f" (time: {response_time:.2f}s)"

        if status_code and status_code >= 400:
            logger.warning(message, extra=extra_info)
        else:
            logger.debug(message, extra=extra_info)

    def log_download_progress(
        self,
        logger_name: str,
        video_title: str,
        percent: float,
        speed: Optional[str] = None,
        eta: Optional[str] = None,
    ) -> None:
        """Log download progress."""
        logger = self.get_logger(logger_name)

        extra_info = {
            "video_title": video_title,
            "progress_percent": percent,
            "download_speed": speed,
            "eta": eta,
        }

        message = f"Download progress: {video_title} ({percent:.1f}%)"
        if speed:
            message += f" at {speed}"
        if eta:
            message += f" ETA: {eta}"

        logger.debug(message, extra=extra_info)

    def log_sync_summary(
        self,
        logger_name: str,
        playlist_name: str,
        downloaded: int,
        removed: int,
        skipped: int,
        failed: int,
        duration: float,
    ) -> None:
        """Log sync operation summary."""
        logger = self.get_logger(logger_name)

        extra_info = {
            "playlist_name": playlist_name,
            "downloaded_count": downloaded,
            "removed_count": removed,
            "skipped_count": skipped,
            "failed_count": failed,
            "duration_seconds": duration,
        }

        message = (
            f"Sync completed for '{playlist_name}': "
            f"{downloaded} downloaded, {removed} removed, "
            f"{skipped} skipped, {failed} failed "
            f"(took {duration:.1f}s)"
        )

        if failed > 0:
            logger.warning(message, extra=extra_info)
        else:
            logger.info(message, extra=extra_info)

    def print_banner(self, title: str, version: str) -> None:
        """Print application banner."""
        self.console.print(f"\n[bold blue]{title}[/bold blue] [dim]v{version}[/dim]")
        self.console.print("[dim]YouTube Music Playlist Manager (YTMM CLI)[/dim]\n")

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[success]✓[/success] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[warning]⚠[/warning] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[error]✗[/error] {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[info]ℹ[/info] {message}")


# Global logger instance
_logger_manager: Optional[YTMusicManagerCLILogger] = None


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """Get a logger instance."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = YTMusicManagerCLILogger()
    return _logger_manager.get_logger(name, context)


def get_console() -> Console:
    """Get the rich console instance with cross-platform optimized settings."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = YTMusicManagerCLILogger()
    return _logger_manager.console


def create_console(theme: Optional[Theme] = None) -> Console:
    """Create a new Console instance with optimized cross-platform settings.

    This ensures consistent color output across all terminals:
    - PowerShell 5.1, Windows Terminal, Windows CMD
    - Linux terminals, macOS terminals
    - CI/CD environments
    """
    import os

    # Enable Windows console features if needed
    if os.name == "nt":
        try:
            import colorama

            colorama.just_fix_windows_console()
        except ImportError:
            pass

    return Console(
        theme=theme or YT_MUSIC_MANAGER_CLI_THEME,
        force_terminal=True,  # Always emit ANSI
        legacy_windows=True if os.name == "nt" else False,  # Colorama fallback
        color_system="standard",  # 8 colors minimum, universally supported
    )


def setup_logging() -> None:
    """Initialize logging system."""
    global _logger_manager
    _logger_manager = YTMusicManagerCLILogger()


def log_exception(
    exception: Exception,
    logger_name: str = "yt_music_manager_cli.error",
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Convenience function to log exceptions."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = YTMusicManagerCLILogger()
    _logger_manager.log_exception(logger_name, exception, context)


# Warning handling utilities
import warnings
from types import FrameType
from typing import Set, Optional, TextIO, Type

# Use a set to track displayed warnings and avoid duplicates
_displayed_warnings: Set[str] = set()


def format_warning(
    message: str,
    category: Type[Warning],
    filename: str,
    lineno: int,
    file: Optional[TextIO] = None,
    line: Optional[str] = None,
) -> str:
    """Custom warning format function."""
    return f"WARNING: {message}\n"


def show_warning(message: str) -> None:
    """
    Shows a warning to the user, ensuring duplicates are not shown.
    """
    # Only show a given warning once to avoid spamming the console
    if message not in _displayed_warnings:
        warnings.showwarning(message, UserWarning, "", 0)
        _displayed_warnings.add(message)


# Set the custom format
warnings.formatwarning = format_warning
