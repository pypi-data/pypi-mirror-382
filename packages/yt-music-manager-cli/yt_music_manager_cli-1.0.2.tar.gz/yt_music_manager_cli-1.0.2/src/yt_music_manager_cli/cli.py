"""
Command-line interface for YT Music Manager CLI (YTMM CLI).
Provides user-friendly commands for playlist management and synchronization.
"""

import asyncio
import sys
import shutil
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING
import click
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.console import Console

# Snapshot filesystem state BEFORE importing internal modules that may auto-create
_INIT_CONFIG_PATH = Path("config/settings.toml")
_INIT_LOGS_DIR = Path("logs")
_INIT_DATA_DIR = Path("data")
_preexist_config = _INIT_CONFIG_PATH.exists()
_preexist_logs = _INIT_LOGS_DIR.exists()
_preexist_data = _INIT_DATA_DIR.exists()

from . import __version__
from .config import get_settings, reload_settings, Settings
from .unified_youtube_client import get_youtube_client, UnifiedYouTubeClient
from .oauth_handler import YouTubeOAuth, setup_oauth_instructions
from .oauth_client_config import OAuthClientConfig, create_oauth_client_template
from .playlist_manager import PlaylistManager
from .sync_engine import SyncEngine, SyncResult
from .download_manager import DownloadProgress
from .logging_utils import setup_logging, get_logger, get_console, show_warning

if TYPE_CHECKING:
    from .youtube_api import PlaylistInfo

# Provide a module-level static_ffmpeg object for tests to monkeypatch.
# If the real library isn't available, expose a no-op shim with add_paths().
try:  # pragma: no cover - exercised via tests with monkeypatch
    import static_ffmpeg as static_ffmpeg  # type: ignore
except Exception:  # pragma: no cover

    class _StaticFFmpegShim:
        def add_paths(self) -> None:
            pass

    static_ffmpeg = _StaticFFmpegShim()  # type: ignore
from .exceptions import (
    YTMusicManagerCLIError,
    ConfigurationError,
    ValidationError,
    validate_url,
    validate_file_path,
    ProgressTracker,
)


# Global console instance
import os

# Attempt to proactively enable ANSI color support on Windows (especially PowerShell 5.1)
if os.name == "nt":
    try:  # colorama helps older Windows consoles interpret ANSI sequences
        import colorama  # type: ignore

        colorama.just_fix_windows_console()
    except Exception:
        pass
    # Explicitly enable Virtual Terminal Processing for ANSI if possible
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            if not (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                kernel32.SetConsoleMode(
                    handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                )
    except Exception:
        pass

# Encourage color in downstream libs
os.environ.setdefault("CLICOLOR", "1")
os.environ.setdefault("FORCE_COLOR", "1")
os.environ.setdefault("RICH_FORCE_COLOR", "1")

# Force colors for better terminal support. Use legacy_windows=True to ensure colorama fallback.
# Reuse shared console to avoid runtime signature mismatches in Rich across environments
console = get_console()
logger = get_logger(__name__)


class ProgressDisplay:
    """Handles progress display for long-running operations."""

    def __init__(self):
        self.progress = None
        self.download_tasks = {}
        self.completed_videos = set()

    def start_progress(self):
        """Start a progress display for downloads."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeRemainingColumn(),
            TextColumn("{task.fields[status]}"),
            console=console,
        )
        self.progress.start()

    def update_progress(
        self, task_id, advance: int = 1, description: str = None, status: str = ""
    ):
        """Update progress."""
        if self.progress:
            self.progress.update(
                task_id, advance=advance, description=description, status=status
            )

    def finish_progress(self):
        """Finish progress display."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.download_tasks = {}

    def download_progress_callback(self, playlist_id: str, progress: DownloadProgress):
        """Handle download progress updates."""
        if not self.progress:
            self.start_progress()

        task_id = self.download_tasks.get(progress.video_id)

        if progress.status == "downloading":
            if task_id is None:
                task_id = self.progress.add_task(
                    f"Downloading: {progress.title}",
                    total=100,
                    status=f"of {progress.total_bytes_str} at {progress.speed} ETA {progress.eta}",
                )
                self.download_tasks[progress.video_id] = task_id

            self.progress.update(
                task_id,
                completed=progress.percent,
                status=f"of {progress.total_bytes_str} at {progress.speed} ETA {progress.eta}",
            )

        elif (
            progress.status == "completed"
            and progress.video_id not in self.completed_videos
        ):
            if task_id:
                self.progress.update(
                    task_id, completed=100, status="[green][OK] Done[/green]"
                )
            self.completed_videos.add(progress.video_id)

        elif progress.status == "error":
            if task_id:
                self.progress.update(task_id, status="[red][FAIL] Error[/red]")


# Global progress display
progress_display = ProgressDisplay()


def initialize_ffmpeg_if_needed():
    """Initialize ffmpeg only when it's actually needed for audio processing."""
    with console.status("[dim]Initializing ffmpeg...[/dim]"):
        # Use module-level shim (real module if available, no-op otherwise)
        try:
            static_ffmpeg.add_paths()  # type: ignore[attr-defined]
        except Exception:
            pass
        ffmpeg_available = shutil.which("ffmpeg") is not None

    if ffmpeg_available:
        console.print("[green][OK] Initialized ffmpeg[/green]")
    else:
        show_warning(
            "Could not automatically configure ffmpeg. Audio conversion and metadata embedding will be skipped."
        )

    return ffmpeg_available


class ColoredGroup(click.Group):
    """Custom Click Group that ensures banner is shown even for help."""

    def main(
        self,
        args=None,
        prog_name=None,
        complete_var=None,
        standalone_mode=True,
        **extra,
    ):
        # Normalize args (Click passes None to mean use sys.argv[1:])
        effective_args = list(args) if args is not None else sys.argv[1:]

        # Show Rich banner for help or no-command scenarios (works across all terminals)
        showing_help = any(a in ("--help", "-h") for a in effective_args)
        no_command = not any(arg for arg in effective_args if not arg.startswith("-"))

        if showing_help or no_command:
            from rich.panel import Panel

            banner_text = f"[bold cyan]YT Music Manager CLI (YTMM CLI)[/bold cyan] [green]v{__version__}[/green]\n[dim]A CLI tool for downloading and syncing YouTube & Youtube Music playlists.[/dim]"
            console.print(Panel.fit(banner_text, border_style="blue", padding=(0, 1)))

        return super().main(args, prog_name, complete_var, standalone_mode, **extra)

    def format_help(self, ctx, formatter):  # type: ignore[override]
        """Override Click's help formatting to prevent raw ANSI codes in the description."""
        # Let Click generate the help normally, but clean up any raw ANSI in the description
        super().format_help(ctx, formatter)

        # Get the help text and clean up raw ANSI escape sequences
        help_text = formatter.getvalue()

        # Remove all raw ANSI escape sequences completely
        import re

        # Pattern to match ANSI escape sequences like \x1b[36m, \x1b[0m, etc.
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        help_text = ansi_escape.sub("", help_text)

        # Also clean up the [36m style codes that show as raw text
        bracket_codes = re.compile(r"\[[0-9]+m")
        help_text = bracket_codes.sub("", help_text)

        # Replace the formatter's buffer with the cleaned text
        formatter.buffer = [help_text]


@click.group(invoke_without_command=True, cls=ColoredGroup)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx, version, config, debug):
    # """YT Music Manager CLI - YouTube Playlist Synchronizer

    # A CLI tool for downloading and syncing YouTube & Youtube Music playlists.
    # """
    if version:
        console.print(
            f"[bold blue]YT Music Manager CLI (YTMM CLI)[/bold blue] v[green]{__version__}[/green]"
        )
        return

    # Setup logging
    setup_logging()

    # Adjust log level based on flags
    if debug:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    # Show banner and initialize (skip if help was already shown)
    help_shown = "--help" in sys.argv or "-h" in sys.argv
    # if not help_shown:
    #     console.print(f"\n[bold blue]YT Music Manager CLI (YTMM CLI)[/bold blue] v{__version__}")
    #     console.print("[dim]YouTube Music Playlist Manager[/dim]\n")

    # Set up context object (ffmpeg will be initialized only when needed)
    ctx.obj = {"ffmpeg_available": None}

    # If no command specified, show help
    if ctx.invoked_subcommand is None and not help_shown:
        console.print(ctx.get_help())


# Provide compact two-line help without blank paragraph using Click's "\b" no-wrap escape.
# We assign to __doc__ so Click processes formatting controls (\b keeps newlines inside paragraph).
# main.help = (
#     f"\b\n\x1b[36mYT Music Manager CLI -\x1b[0m \x1b[32mv{__version__}\x1b[0m\n"
#     "\x1b[90mA CLI tool for downloading and syncing YouTube & Youtube Music playlists.\x1b[0m"
# )


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
def init(force):
    """Initialize configuration and setup.
    Uses a pre-import snapshot (_preexist_*) so we can accurately report what
    existed BEFORE automatic side-effects (config/logs creation) occurred.
    """
    console.print("[blue]Initializing YT Music Manager CLI (YTMM CLI)...[/blue]")

    config_path = _INIT_CONFIG_PATH
    data_dir = _INIT_DATA_DIR
    logs_dir = _INIT_LOGS_DIR

    try:
        # Configuration file handling
        if _preexist_config:
            if force:
                Settings.create_default_config(config_path)
                console.print(
                    f"[green][OK][/green] Overwrote configuration file: {config_path}"
                )
            else:
                console.print(
                    f"[green][OK][/green] Configuration file already exists: {config_path}"
                )
        else:
            # If it didn't exist at startup we create (even if some other import already made it now)
            if not config_path.exists() or force:
                Settings.create_default_config(config_path)
            console.print(
                f"[green][OK][/green] Created configuration file: {config_path}"
            )

        # Data directory
        if _preexist_data:
            console.print(
                f"[green][OK][/green] Data directory already exists: {data_dir}"
            )
        else:
            data_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[green][OK][/green] Created data directory: {data_dir}")

        # Logs directory
        if _preexist_logs:
            if force and logs_dir.exists():
                # Nothing to overwrite really; just acknowledge existence
                console.print(
                    f"[green][OK][/green] Logs directory already exists: {logs_dir}"
                )
            else:
                console.print(
                    f"[green][OK][/green] Logs directory already exists: {logs_dir}"
                )
        else:
            logs_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[green][OK][/green] Created logs directory: {logs_dir}")

        console.print("\n[bold yellow]Next steps:[/bold yellow]")
        console.print(
            "1. Edit config/settings.toml and configure authentication (auto_oauth/manual_oauth/no_auth)"
        )
        console.print("2. Run 'ytmm config' to verify your setup")
        console.print("3. Add your first playlist with 'ytmm add-playlist <url>'")

    except Exception as e:
        console.print(f"[red]Error during initialization: {e}[/red]")
        logger.error(f"Initialization failed: {e}")


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx):  # type: ignore[override]
    """Show current configuration summary & validation.

    Subcommands:
      config list [key]  - Show all config values or a specific one (old: settings get)
      config set <key> <value> - Update a value (old: settings set)

    Running bare `ytmm config` keeps the original rich status view.
    """
    if ctx.invoked_subcommand is not None:
        return  # Defer to subcommand
    try:
        settings = get_settings()

        table = Table(title="Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Status", style="green")

        table.add_row("Auth Method", settings.youtube.auth_method, "[OK]")

        if settings.youtube.auth_method in ("auto_oauth", "manual_oauth"):
            client_id_display = (
                settings.youtube.oauth_client_id[:10] + "..."
                if settings.youtube.oauth_client_id
                else "Not set"
            )
            table.add_row(
                "OAuth Client ID",
                client_id_display,
                "[OK]" if settings.youtube.oauth_client_id else "[FAIL]",
            )
            table.add_row(
                "OAuth Client Secret",
                "Set" if settings.youtube.oauth_client_secret else "Not set",
                "[OK]" if settings.youtube.oauth_client_secret else "[FAIL]",
            )
        else:
            table.add_row("Public Access Only", "Yes", "[OK]")

        table.add_row("Download Path", settings.download.base_path, "[OK]")
        table.add_row("Audio Format", settings.download.audio_format, "[OK]")
        table.add_row(
            "Audio Quality", f"{settings.download.audio_quality} kbps", "[OK]"
        )
        table.add_row(
            "Max Concurrent", str(settings.sync.max_concurrent_downloads), "[OK]"
        )
        table.add_row(
            "Sync Interval", f"{settings.sync.auto_sync_interval} seconds", "[OK]"
        )

        console.print(table)

        console.print("\n[blue]Validating configuration...[/blue]")
        issues = settings.validate_setup()
        if not issues:
            console.print("[green][OK] Configuration is valid[/green]")
            try:
                youtube_client = get_youtube_client()
                if youtube_client.validate_api_access():
                    console.print("[green][OK] YouTube access is working[/green]")
                    auth_info = youtube_client.get_auth_info()
                    if auth_info["method"] == "no_auth":
                        console.print(
                            "[yellow]ℹ Public playlists only (no authentication)[/yellow]"
                        )
                    elif auth_info.get("authenticated"):
                        console.print("[green][OK] OAuth authentication active[/green]")
                    features = youtube_client.get_supported_features()
                    console.print("\n[blue]Supported features:[/blue]")
                    for feature, supported in features.items():
                        status = "[OK]" if supported else "[FAIL]"
                        console.print(f"  {status} {feature.replace('_', ' ').title()}")
                else:
                    console.print("[red][FAIL] YouTube access validation failed[/red]")
            except Exception as e:  # pragma: no cover - defensive
                console.print(f"[red][FAIL] YouTube access error: {e}[/red]")
        else:
            console.print("[red]Configuration issues found:[/red]")
            for issue in issues.values():
                console.print(f"  [red][FAIL][/red] {issue}")

        if settings.youtube.auth_method == "no_auth":
            console.print(
                "\n[yellow]💡 Tip:[/yellow] You're using no-auth mode (public playlists only)"
            )
            console.print("   To access private playlists:")
            console.print(
                "   • Change auth_method to 'auto_oauth' or 'manual_oauth' in config/settings.toml"
            )
            console.print("   • Or run: ytmm auth mode auto_oauth")
    except Exception as e:  # pragma: no cover - unexpected errors
        console.print(f"[red]Error loading configuration: {e}[/red]")
        logger.error(f"Configuration error: {e}")


@main.command(name="add-playlist")
@click.argument("url_or_ids", nargs=-1, required=True)
@click.option("--name", help="Custom name for the playlist (only works with single playlist)")
def add_playlist(url_or_ids, name):
    """Add one or more YouTube playlists to track.

    URL_OR_ID can be:
    - Full YouTube playlist URL: https://www.youtube.com/playlist?list=PLxxx
    - Short URL: https://youtu.be/playlist?list=PLxxx
    - Just the playlist ID: PLxxx

    You can specify multiple playlists: ytmm add-playlist PLxxx PLyyy PLzzz

    Note: --name option only works when adding a single playlist.
    """
    if len(url_or_ids) > 1 and name is not None:
        console.print("[red]Error: --name option can only be used with a single playlist[/red]")
        console.print("When adding multiple playlists, each will use its default name from YouTube.")
        return

    for url_or_id in url_or_ids:
        _add_playlist_sync(url_or_id, name)


def _add_playlist_sync(url_or_id, name):
    """Add a YouTube playlist to track."""
    try:
        # Handle different input formats
        input_value = url_or_id.strip()

        # If it looks like just a playlist ID (starts with PL or UC, no http)
        if input_value.startswith(
            ("PL", "UC", "OLAK", "RDCLAK")
        ) and not input_value.startswith(("http://", "https://")):
            # Convert playlist ID to URL
            playlist_url = f"https://www.youtube.com/playlist?list={input_value}"
            playlist_id = input_value
        else:
            # Validate as URL
            validate_url(input_value)
            playlist_url = input_value
            playlist_id = None  # Will be extracted later

        with console.status(f"[bold green]Adding playlist from: {input_value}..."):
            # Initialize unified client and managers
            youtube_client = get_youtube_client()
            playlist_manager = PlaylistManager()

            # Extract playlist ID if not already done
            if not playlist_id:
                playlist_id = youtube_client.extract_playlist_id(playlist_url)

            # Check if already exists
            if playlist_manager.get_playlist(playlist_id):
                console.print("[yellow]Playlist is already being tracked[/yellow]")
                return

            playlist_info = youtube_client.get_playlist_info(
                playlist_id, include_videos=True
            )

        if name:
            playlist_info.title = name

        # Add to playlist manager
        playlist_manager.add_playlist(playlist_info)

        console.print(
            f"\n[green][OK][/green] Added playlist: [bold]{playlist_info.title}[/bold]"
        )
        console.print(f"  Videos: {len(playlist_info.videos)}")
        console.print(f"  Channel: {playlist_info.channel_title}")
        console.print(f"  ID: {playlist_info.playlist_id}")

        # Ask if user wants to sync immediately
        if click.confirm("Would you like to sync this playlist now?"):
            ffmpeg_available = initialize_ffmpeg_if_needed()
            sync_result = asyncio.run(
                sync_single_playlist(
                    playlist_id,
                    playlist_info=playlist_info,
                    ffmpeg_available=ffmpeg_available,
                )
            )
            display_sync_result(sync_result)

    except ValidationError as e:
        console.print(f"[red]Invalid input: {e.message}[/red]")
    except YTMusicManagerCLIError as e:
        console.print(f"[red]Error: {e.message}[/red]")
    except Exception as e:
        console.print(f"[red]Error adding playlist: {e}[/red]")
        logger.error(f"Add playlist error: {e}", exc_info=True)
    finally:
        progress_display.finish_progress()


def _list_user_playlists_impl(simple):
    """Implementation for listing user playlists."""
    try:
        youtube_client = get_youtube_client()

        # Check if authenticated with OAuth
        auth_info = youtube_client.get_auth_info()
        if not auth_info.get("authenticated"):
            console.print("[red]You need to sign in first.[/red]")
            console.print("Run: ytmm auth mode auto_oauth")
            return

        console.print("[blue]Fetching your playlists from YouTube...[/blue]")

        # Get OAuth handler to access user playlists
        from .oauth_handler import YouTubeOAuth

        oauth_handler = YouTubeOAuth()

        if not oauth_handler._load_existing_credentials():
            console.print(
                "[red]Authentication error. Please run: ytmm auth mode auto_oauth[/red]"
            )
            return

        # Get user's playlists
        playlists = oauth_handler.get_user_playlists()

        if not playlists:
            console.print("[yellow]No playlists found in your account.[/yellow]")
            return

        if simple:
            # Simple text output
            print(f"\nYour YouTube Playlists ({len(playlists)}):")
            print("=" * 50)
            for playlist in playlists:
                snippet = playlist.get("snippet", {})
                content_details = playlist.get("contentDetails", {})

                playlist_id = playlist.get("id", "N/A")
                title = snippet.get("title", "Untitled")
                video_count = content_details.get("itemCount", 0)

                print(f"ID: {playlist_id}")
                print(f"Title: {title}")
                print(f"Videos: {video_count}")
                print("-" * 30)

            print(f"\nTo add a playlist, copy the ID and run:")
            print(f"   ytmm add-playlist <ID>")
            return

        # Display playlists in a table
        table = Table(title=f"Your YouTube Playlists ({len(playlists)})")
        table.add_column("ID", style="cyan", no_wrap=False)
        table.add_column("Title", style="bold", min_width=20)
        table.add_column("Videos", style="green", justify="right")
        table.add_column("Privacy", style="yellow")
        table.add_column("Description", style="dim", max_width=40)

        for playlist in playlists:
            snippet = playlist.get("snippet", {})
            content_details = playlist.get("contentDetails", {})

            playlist_id = playlist.get("id", "N/A")
            title = snippet.get("title", "Untitled")
            video_count = content_details.get("itemCount", 0)
            privacy = snippet.get("privacyStatus", "unknown").title()
            description = (
                snippet.get("description", "")[:50] + "..."
                if len(snippet.get("description", "")) > 50
                else snippet.get("description", "")
            )

            table.add_row(playlist_id, title, str(video_count), privacy, description)

        console.print(table)
        console.print(f"\n[dim]To add a playlist, copy the ID and run:[/dim]")
        console.print(f"[dim]   ytmm add-playlist <ID>[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing playlists: {e}[/red]")
        logger.error(f"List user playlists error: {e}", exc_info=True)


@main.command(name="list-user-playlists")
@click.option("--simple", is_flag=True, help="Simple text output (no fancy table)")
def list_user_playlists(simple):
    """List all playlists from your Google account."""
    _list_user_playlists_impl(simple)


@main.command(name="lup")
@click.option("--simple", is_flag=True, help="Simple text output (no fancy table)")
def list_user_playlists_short(simple):
    """Alias for list-user-playlists."""
    _list_user_playlists_impl(simple)


def _list_playlists_impl(detailed):
    """Implementation for listing tracked playlists."""
    try:
        playlist_manager = PlaylistManager()
        playlists = playlist_manager.get_all_playlists()

        if not playlists:
            console.print("[yellow]No playlists are currently being tracked[/yellow]")
            console.print("Use 'ytmm add-playlist <url>' to add one.")
            return

        if detailed:
            for playlist_state in playlists.values():
                info = playlist_state.playlist_info

                panel_content = f"""
[bold]{info.title}[/bold]
Channel: {info.channel_title}
Videos: {len(info.videos)}
Last Sync: {playlist_state.last_sync or 'Never'}
Downloads: {playlist_state.download_count}
Failures: {playlist_state.failed_count}
Path: {playlist_state.local_path or 'Not set'}
ID: {info.playlist_id}
                """.strip()

                console.print(Panel(panel_content, title="Playlist"))
        else:
            table = Table(title=f"Tracked Playlists ({len(playlists)})")
            table.add_column("Title", style="cyan", no_wrap=True)
            table.add_column("Channel", style="blue")
            table.add_column("Videos", style="green", justify="right")
            table.add_column("Last Sync", style="yellow")
            table.add_column("Status", style="magenta")

            for playlist_state in playlists.values():
                info = playlist_state.playlist_info

                # Determine status
                if playlist_state.last_sync is None:
                    status = "Never synced"
                elif playlist_state.failed_count > 0:
                    status = f"{playlist_state.failed_count} failed"
                else:
                    status = "Up to date"

                last_sync_display = (
                    playlist_state.last_sync[:10]
                    if playlist_state.last_sync
                    else "Never"
                )

                table.add_row(
                    info.title[:40] + "..." if len(info.title) > 40 else info.title,
                    info.channel_title,
                    str(len(info.videos)),
                    last_sync_display,
                    status,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing playlists: {e}[/red]")
        logger.error(f"List playlists error: {e}")


@main.command(name="list-playlists")
@click.option("--detailed", is_flag=True, help="Show detailed information")
def list_playlists(detailed):
    """List all tracked playlists."""
    _list_playlists_impl(detailed)


@main.command(name="lp")
@click.option("--detailed", is_flag=True, help="Show detailed information")
def list_playlists_short(detailed):
    """Alias for list-playlists."""
    _list_playlists_impl(detailed)


@main.command()
@click.argument("playlist_identifier", required=False)
@click.option("--all", is_flag=True, help="Sync all playlists")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without doing it"
)
@click.option("--force", is_flag=True, help="Force sync even if recently synced")
def sync(playlist_identifier, all, dry_run, force):
    """Sync playlists (download new songs, remove old ones)."""
    try:
        if not all and not playlist_identifier:
            console.print("[red]Please specify a playlist or use --all[/red]")
            return

        if dry_run:
            console.print("[yellow]DRY RUN - No files will be modified[/yellow]\n")

        if all:
            ffmpeg_available = initialize_ffmpeg_if_needed()
            asyncio.run(sync_all_playlists(dry_run, ffmpeg_available=ffmpeg_available))
        else:
            # Try to find playlist by name or ID
            playlist_manager = PlaylistManager()
            playlists = playlist_manager.get_all_playlists()

            target_playlist = None
            for playlist_id, playlist_state in playlists.items():
                if (
                    playlist_id == playlist_identifier
                    or playlist_state.playlist_info.title.lower()
                    == playlist_identifier.lower()
                ):
                    target_playlist = playlist_id
                    break

            if not target_playlist:
                console.print(f"[red]Playlist not found: {playlist_identifier}[/red]")
                console.print("Use 'ytmm list-playlists' to see available playlists")
                return

            ffmpeg_available = initialize_ffmpeg_if_needed()
            sync_result = asyncio.run(
                sync_single_playlist(
                    target_playlist, dry_run=dry_run, ffmpeg_available=ffmpeg_available
                )
            )
            display_sync_result(sync_result)

    except Exception as e:
        console.print(f"[red]Sync error: {e}[/red]")
        logger.error(f"Sync error: {e}", exc_info=True)


def _remove_playlist_impl(playlist_identifier, keep_files):
    """Implementation for removing a playlist."""
    try:
        playlist_manager = PlaylistManager()
        playlists = playlist_manager.get_all_playlists()

        # Find playlist
        target_playlist = None
        target_state = None
        for playlist_id, playlist_state in playlists.items():
            if (
                playlist_id == playlist_identifier
                or playlist_state.playlist_info.title.lower()
                == playlist_identifier.lower()
            ):
                target_playlist = playlist_id
                target_state = playlist_state
                break

        if not target_playlist:
            console.print(f"[red]Playlist not found: {playlist_identifier}[/red]")
            return

        console.print(
            f"Removing playlist: [bold]{target_state.playlist_info.title}[/bold]"
        )

        if not keep_files and target_state.local_path:
            local_path = Path(target_state.local_path)
            if local_path.exists():
                if click.confirm(f"Delete all files in {local_path}?"):
                    import shutil

                    shutil.rmtree(local_path)
                    console.print(f"[green][OK][/green] Deleted files: {local_path}")

        # Remove from tracking
        playlist_manager.remove_playlist(target_playlist)
        console.print("[green][OK][/green] Playlist removed from tracking")

    except Exception as e:
        console.print(f"[red]Error removing playlist: {e}[/red]")
        logger.error(f"Remove playlist error: {e}")


@main.command(name="remove-playlist")
@click.argument("playlist_identifiers", nargs=-1, required=True)
@click.option("--keep-files", is_flag=True, help="Keep downloaded files")
def remove_playlist(playlist_identifiers, keep_files):
    """Remove one or more playlists from tracking.

    You can specify multiple playlists: ytmm remove-playlist "Playlist 1" "Playlist 2" PLxxx
    """
    for playlist_identifier in playlist_identifiers:
        _remove_playlist_impl(playlist_identifier, keep_files)


@main.command(name="rp")
@click.argument("playlist_identifiers", nargs=-1, required=True)
@click.option("--keep-files", is_flag=True, help="Keep downloaded files")
def remove_playlist_short(playlist_identifiers, keep_files):
    """Alias for remove-playlist."""
    for playlist_identifier in playlist_identifiers:
        _remove_playlist_impl(playlist_identifier, keep_files)


@main.command()
def status():
    """Show sync status and statistics."""
    try:
        playlist_manager = PlaylistManager()
        stats = playlist_manager.get_statistics()

        # Create status table
        table = Table(title="YT Music Manager CLI (YTMM CLI) Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Playlists", str(stats["total_playlists"]))
        table.add_row("Total Videos", str(stats["total_videos"]))
        table.add_row("Downloaded", str(stats["total_downloaded"]))
        table.add_row("Failed", str(stats["total_failed"]))
        table.add_row("Never Synced", str(stats["never_synced"]))
        table.add_row("Recently Synced", str(stats["recently_synced"]))

        console.print(table)

        # Show API quota if available
        try:
            youtube_client = get_youtube_client()
            quota = youtube_client.get_quota_usage()

            if quota:  # Only show if API-based auth
                quota_table = Table(title="YouTube API Quota")
                quota_table.add_column("Metric", style="cyan")
                quota_table.add_column("Value", style="yellow", justify="right")

                quota_table.add_row("Used Today", str(quota.get("used", "N/A")))
                quota_table.add_row("Remaining", str(quota.get("remaining", "N/A")))
                quota_table.add_row("Daily Limit", str(quota.get("limit", "N/A")))

                console.print(quota_table)
        except Exception:
            pass  # Ignore quota errors

    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")
        logger.error(f"Status error: {e}")


async def sync_single_playlist(
    playlist_id: str,
    dry_run: bool = False,
    playlist_info: Optional["PlaylistInfo"] = None,
    ffmpeg_available: bool = False,
) -> SyncResult:
    """Sync a single playlist, optionally with pre-fetched playlist info."""
    sync_engine = SyncEngine(
        ffmpeg_available=ffmpeg_available,
        progress_callback=progress_display.download_progress_callback,
    )

    with console.status(
        f"[bold green]Syncing playlist: {playlist_info.title if playlist_info else '...'}..."
    ):
        if playlist_info:
            result = await sync_engine.sync_playlist(
                playlist_id, current_playlist=playlist_info, dry_run=dry_run
            )
        else:
            playlist_manager = PlaylistManager()
            playlist_state = playlist_manager.get_playlist(playlist_id)

            if not playlist_state:
                raise ValueError(f"Playlist not found: {playlist_id}")

            result = await sync_engine.sync_playlist(playlist_id, dry_run=dry_run)

    await asyncio.sleep(0.1)  # Allow final UI updates to render
    progress_display.finish_progress()

    return result


async def sync_all_playlists(dry_run: bool = False, ffmpeg_available: bool = False):
    """Sync all tracked playlists."""
    sync_engine = SyncEngine(
        ffmpeg_available=ffmpeg_available,
        progress_callback=progress_display.download_progress_callback,
    )
    playlist_manager = PlaylistManager()

    with console.status("[bold green]Syncing all playlists...[/bold green]"):
        results = await sync_engine.sync_all_playlists(dry_run=dry_run)

    # Display summary
    successful = sum(1 for r in results.values() if r.success)
    failed = len(results) - successful
    total_downloaded = sum(r.items_downloaded for r in results.values())
    total_removed = sum(r.items_removed for r in results.values())

    console.print(f"\n[bold]Sync Summary:[/bold]")
    console.print(f"Playlists: {successful} successful, {failed} failed")
    console.print(f"Actions: {total_downloaded} downloaded, {total_removed} removed")

    # Show individual results
    for playlist_id, result in results.items():
        playlist_state = playlist_manager.get_playlist(playlist_id)
        playlist_name = (
            playlist_state.playlist_info.title if playlist_state else playlist_id
        )

        if result.success:
            console.print(
                f"[green][OK][/green] {playlist_name}: {result.items_downloaded} downloaded"
            )
        else:
            console.print(
                f"[red][FAIL][/red] {playlist_name}: {len(result.errors)} errors"
            )
            if result.errors:
                for error in result.errors[:3]:  # Show first 3 errors
                    console.print(f"    {error}")


def display_sync_result(result: SyncResult):
    """Display sync result information."""
    if result.success:
        console.print(f"[green][OK][/green] Sync completed successfully")
    else:
        console.print(f"[red][FAIL][/red] Sync completed with errors")

    console.print(f"  Downloaded: {result.items_downloaded}")
    console.print(f"  Removed: {result.items_removed}")
    console.print(f"  Skipped: {result.items_skipped}")
    console.print(f"  Failed: {result.items_failed}")
    console.print(f"  Duration: {result.duration_seconds:.1f} seconds")

    if result.errors:
        console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
        for error in result.errors[:5]:  # Show first 5 errors
            console.print(f"  {error}")
        if len(result.errors) > 5:
            console.print(f"  ... and {len(result.errors) - 5} more")


# Authentication commands
@main.group()
def auth():
    """Manage authentication settings."""
    pass


@auth.command()
def status():
    """Show current authentication status."""
    try:
        settings = get_settings()
        youtube_client = get_youtube_client()

        console.print("[blue]Authentication Status[/blue]")
        console.print(f"Method: {settings.youtube.auth_method}")

        if settings.youtube.auth_method == "no_auth":
            console.print("[yellow]Using public access only[/yellow]")
            console.print("• Can access public playlists")
            console.print("• Cannot access private/unlisted playlists")
            console.print("• No quota limits")

        elif settings.youtube.auth_method in ["auto_oauth", "manual_oauth"]:
            method_name = (
                "Auto OAuth"
                if settings.youtube.auth_method == "auto_oauth"
                else "Manual OAuth"
            )
            console.print(f"[cyan]Using {method_name} (Google sign-in)[/cyan]")

            # Check OAuth credentials based on method
            if settings.youtube.auth_method == "auto_oauth":
                console.print("• Using bundled OAuth credentials")
                # Check if authenticated
                auth_info = youtube_client.get_auth_info()
                if auth_info.get("authenticated"):
                    console.print("• [green]Currently authenticated[/green]")
                    if auth_info.get("user_email"):
                        console.print(f"• Signed in as: {auth_info['user_email']}")
                else:
                    console.print("• [yellow]Not currently authenticated[/yellow]")
                    console.print("• Run: ytmm auth mode auto_oauth")
            else:  # manual_oauth
                if (
                    settings.youtube.oauth_client_id
                    and settings.youtube.oauth_client_secret
                ):
                    console.print("• OAuth credentials configured")
                    # Check if authenticated
                    auth_info = youtube_client.get_auth_info()
                    if auth_info.get("authenticated"):
                        console.print("• [green]Currently authenticated[/green]")
                        if auth_info.get("user_email"):
                            console.print(f"• Signed in as: {auth_info['user_email']}")
                    else:
                        console.print("• [yellow]Not currently authenticated[/yellow]")
                        console.print("• Run: ytmm auth mode manual_oauth")
                else:
                    console.print("• [red]OAuth credentials not configured[/red]")
                    console.print("• Run: ytmm auth mode manual_oauth")

        # Show supported features
        features = youtube_client.get_supported_features()
        console.print("\n[blue]Available Features:[/blue]")
        for feature, supported in features.items():
            status = "[green][OK][/green]" if supported else "[red][FAIL][/red]"
            feature_name = feature.replace("_", " ").title()
            console.print(f"  {status} {feature_name}")

    except Exception as e:
        console.print(f"[red]Error checking authentication: {e}[/red]")


@auth.command()
@click.argument("method", type=click.Choice(["no_auth", "auto_oauth", "manual_oauth"]))
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def mode(method, yes):
    """Set authentication method and get guided through setup.

    Authentication methods:

    no_auth      - Public playlists only (no setup required)

    auto_oauth   - Google sign-in with built-in login system

    manual_oauth - Google sign-in with your own OAuth credentials (manual setup)
    """
    try:
        settings = get_settings()
        current_method = settings.youtube.auth_method

        console.print(f"[blue]Setting authentication method to: {method}[/blue]")

        # If same method, check if everything is configured
        if current_method == method:
            console.print(f"[yellow]Already using {method} method[/yellow]")

            if method == "no_auth":
                console.print("[green][OK] No additional setup required[/green]")
                return
            elif method == "auto_oauth":
                # Check if authenticated - wrap in try/except since get_youtube_client can fail
                try:
                    youtube_client = get_youtube_client()
                    auth_info = youtube_client.get_auth_info()
                    if auth_info.get("authenticated"):
                        console.print("[green][OK] Already authenticated[/green]")
                        return
                except Exception:
                    pass  # Fall through to authentication process
                # Fall through to authentication process
            elif method == "manual_oauth":
                if (
                    settings.youtube.oauth_client_id
                    and settings.youtube.oauth_client_secret
                ):
                    # Wrap in try/except since get_youtube_client can fail
                    try:
                        youtube_client = get_youtube_client()
                        auth_info = youtube_client.get_auth_info()
                        if auth_info.get("authenticated"):
                            console.print(
                                "[green][OK] Already configured and authenticated[/green]"
                            )
                            return
                    except Exception:
                        pass  # Fall through to setup process
                # Fall through to setup process

        # Update settings file
        settings_path = Path("config") / "settings.toml"
        content = settings_path.read_text()

        # Replace the auth_method line
        import re

        new_content = re.sub(
            r'auth_method = "[^"]*"', f'auth_method = "{method}"', content
        )

        try:
            # Process based on method
            if method == "no_auth":
                settings_path.write_text(new_content)
                console.print(
                    f"[green][OK] Switched to {method} authentication[/green]"
                )
                console.print("• Can access public playlists only")
                console.print("• No additional setup required")
                return

            elif method == "auto_oauth":
                settings_path.write_text(new_content)
                reload_settings()  # Reload to get new method

                # Check if we already have saved login tokens
                oauth_handler = YouTubeOAuth()
                existing_auth = oauth_handler._load_existing_credentials()

                if existing_auth:
                    # Test if existing credentials still work
                    try:
                        youtube_client = get_youtube_client()
                        auth_info = youtube_client.get_auth_info()
                        if auth_info.get("authenticated"):
                            console.print(
                                "[green][OK] Switched to auto_oauth with existing authentication[/green]"
                            )
                            console.print("You can now access your private playlists.")
                            return
                        else:
                            console.print(
                                "[yellow]Found saved credentials but they need refresh[/yellow]"
                            )
                    except Exception:
                        console.print(
                            "[yellow]Found saved credentials but they need refresh[/yellow]"
                        )

                console.print("[blue]Setting up Auto OAuth...[/blue]")
                console.print("• Uses bundled OAuth credentials")

                if existing_auth:
                    console.print("• Found existing login - attempting to refresh")
                    # Try to refresh without user interaction first
                    with console.status("[bold blue]Refreshing authentication..."):
                        success = oauth_handler._perform_oauth_flow()

                    if success:
                        console.print(
                            "[green][OK] Auto OAuth authentication refreshed![/green]"
                        )
                        console.print("You can now access your private playlists.")
                        return
                    else:
                        # Revert on refresh failure
                        content_revert = re.sub(
                            r'auth_method = "[^"]*"',
                            f'auth_method = "{current_method}"',
                            new_content,
                        )
                        settings_path.write_text(content_revert)
                        reload_settings()
                        console.print(
                            f"[yellow]Reverted to {current_method} method[/yellow]"
                        )
                        return

                console.print("• Will open browser for Google sign-in")
                if yes or click.confirm("Proceed with Google sign-in?"):
                    with console.status("[bold blue]Starting OAuth flow..."):
                        success = oauth_handler._perform_oauth_flow()

                    if success:
                        console.print(
                            "[green][OK] Auto OAuth setup completed successfully![/green]"
                        )
                        console.print("You can now access your private playlists.")
                    else:
                        # Revert on failure
                        content_revert = re.sub(
                            r'auth_method = "[^"]*"',
                            f'auth_method = "{current_method}"',
                            new_content,
                        )
                        settings_path.write_text(content_revert)
                        reload_settings()
                        console.print(
                            f"[yellow]Reverted to {current_method} method[/yellow]"
                        )
                else:
                    # User cancelled, revert
                    content_revert = re.sub(
                        r'auth_method = "[^"]*"',
                        f'auth_method = "{current_method}"',
                        new_content,
                    )
                    settings_path.write_text(content_revert)
                    reload_settings()
                    console.print(
                        f"[yellow]Cancelled. Staying with {current_method} method[/yellow]"
                    )

            elif method == "manual_oauth":
                # Check if we already have both OAuth credentials AND login tokens
                if (
                    settings.youtube.oauth_client_id
                    and settings.youtube.oauth_client_secret
                ):
                    settings_path.write_text(new_content)
                    reload_settings()

                    # Check if we have saved login tokens that still work
                    oauth_handler = YouTubeOAuth()
                    existing_auth = oauth_handler._load_existing_credentials()

                    if existing_auth:
                        # Test if existing credentials still work
                        try:
                            youtube_client = get_youtube_client()
                            auth_info = youtube_client.get_auth_info()
                            if auth_info.get("authenticated"):
                                console.print(
                                    "[green][OK] Switched to manual_oauth with existing authentication[/green]"
                                )
                                console.print(
                                    "You can now access your private playlists."
                                )
                                return
                            else:
                                console.print(
                                    "[yellow]Found saved credentials but they need refresh[/yellow]"
                                )
                                # Try to refresh without user interaction first
                                with console.status(
                                    "[bold blue]Refreshing authentication..."
                                ):
                                    success = oauth_handler._perform_oauth_flow()

                                if success:
                                    console.print(
                                        "[green][OK] Manual OAuth authentication refreshed![/green]"
                                    )
                                    console.print(
                                        "You can now access your private playlists."
                                    )
                                    return
                                else:
                                    # Revert on refresh failure
                                    content_revert = re.sub(
                                        r'auth_method = "[^"]*"',
                                        f'auth_method = "{current_method}"',
                                        new_content,
                                    )
                                    settings_path.write_text(content_revert)
                                    reload_settings()
                                    console.print(
                                        f"[yellow]Reverted to {current_method} method[/yellow]"
                                    )
                                    return
                        except Exception:
                            console.print(
                                "[yellow]Found saved credentials but they need refresh[/yellow]"
                            )

                    console.print("[green][OK] Switched to manual_oauth[/green]")
                    console.print("OAuth credentials already configured.")

                    if existing_auth:
                        console.print("[yellow]Login tokens need refresh[/yellow]")

                    if yes or click.confirm("Authenticate with Google now?"):
                        oauth_handler = YouTubeOAuth()
                        with console.status("[bold blue]Starting OAuth flow..."):
                            success = oauth_handler._perform_oauth_flow()

                        if success:
                            console.print(
                                "[green][OK] Manual OAuth authentication successful![/green]"
                            )
                            console.print("You can now access your private playlists.")
                            return
                        else:
                            # Revert on authentication failure
                            content_revert = re.sub(
                                r'auth_method = "[^"]*"',
                                f'auth_method = "{current_method}"',
                                new_content,
                            )
                            settings_path.write_text(content_revert)
                            reload_settings()
                            console.print(
                                f"[yellow]Reverted to {current_method} method[/yellow]"
                            )
                            return
                    else:
                        console.print(
                            "You can authenticate later by running this command again."
                        )
                    return

                # No OAuth credentials - need to set them up
                console.print("[blue]Setting up Manual OAuth...[/blue]")
                console.print("You'll need to provide your own OAuth credentials.")
                console.print("\nIf you don't have OAuth credentials yet:")
                console.print("1. Go to https://console.cloud.google.com")
                console.print("2. Create a project and enable YouTube Data API v3")
                console.print("3. Create OAuth 2.0 credentials (Desktop application)")
                console.print("4. Copy the client ID and secret\n")

                # Get new credentials
                try:
                    client_id = click.prompt("Enter OAuth Client ID", type=str).strip()
                    client_secret = click.prompt(
                        "Enter OAuth Client Secret", type=str, hide_input=True
                    ).strip()

                    if not client_id or not client_secret:
                        console.print(
                            "[red]Both client ID and secret are required[/red]"
                        )
                        console.print(
                            f"[yellow]Staying with {current_method} method[/yellow]"
                        )
                        return

                    # Save OAuth credentials
                    if OAuthClientConfig.save_user_config(client_id, client_secret):
                        # Update auth method
                        settings_path.write_text(new_content)
                        reload_settings()

                        console.print("[green][OK] OAuth credentials saved[/green]")

                        if yes or click.confirm("Authenticate with Google now?"):
                            oauth_handler = YouTubeOAuth()
                            with console.status("[bold blue]Starting OAuth flow..."):
                                success = oauth_handler._perform_oauth_flow()

                            if success:
                                console.print(
                                    "[green][OK] Manual OAuth setup completed successfully![/green]"
                                )
                                console.print(
                                    "You can now access your private playlists."
                                )
                            else:
                                # Revert on authentication failure
                                content_revert = re.sub(
                                    r'auth_method = "[^"]*"',
                                    f'auth_method = "{current_method}"',
                                    new_content,
                                )
                                settings_path.write_text(content_revert)
                                reload_settings()
                                console.print(
                                    f"[yellow]Reverted to {current_method} method[/yellow]"
                                )
                        else:
                            console.print(f"[green][OK] Switched to {method}[/green]")
                            console.print(
                                "Run 'ytmm auth mode manual_oauth' again to authenticate."
                            )
                    else:
                        console.print(
                            "[red][FAIL] Failed to save OAuth configuration[/red]"
                        )
                        console.print(
                            f"[yellow]Staying with {current_method} method[/yellow]"
                        )

                except (click.Abort, KeyboardInterrupt):
                    console.print(
                        f"\n[yellow]Setup cancelled. Staying with {current_method} method[/yellow]"
                    )

        except Exception as e:
            # Revert on any error
            settings_path.write_text(content)  # Revert to original content
            reload_settings()
            # Only print error if it's not an OAuth authentication failure (already handled)
            if "OAuth authentication failed" not in str(e):
                console.print(f"[red]Error during setup: {e}[/red]")
            console.print(f"[yellow]Staying with {current_method} method[/yellow]")

    except Exception as e:
        # Only print error if it's not an OAuth authentication failure (already handled)
        if "OAuth authentication failed" not in str(e):
            console.print(f"[red]Error setting authentication method: {e}[/red]")


@auth.command()
@click.argument("target", type=click.Choice(["login", "creds"]))
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def remove(target, yes):
    """Remove authentication data.

    Targets:

    login - Remove stored login tokens (sign out)

    creds - Remove OAuth credentials (manual_oauth only)
    """

    def _reset_auth_method_to_no_auth():
        """Helper function to reset auth method to no_auth and update config file."""
        try:
            settings_path = Path("config") / "settings.toml"
            content = settings_path.read_text()

            # Replace the auth_method line
            import re

            new_content = re.sub(
                r'auth_method = "[^"]*"', 'auth_method = "no_auth"', content
            )

            settings_path.write_text(new_content)
            reload_settings()
            console.print("[blue]Authentication method reset to 'no_auth'[/blue]")
            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Could not reset auth method: {e}[/yellow]")
            return False

    try:
        if target == "login":
            if not yes:
                if not click.confirm("Remove stored login tokens (sign out)?"):
                    console.print("[yellow]Cancelled[/yellow]")
                    return

            oauth_handler = YouTubeOAuth()
            removed = oauth_handler.revoke_authentication()

            if removed:
                console.print(
                    "[green][OK] Successfully signed out and removed login tokens[/green]"
                )
                _reset_auth_method_to_no_auth()
            else:
                console.print("[yellow]No active authentication found[/yellow]")
                # Still reset auth method even if no tokens were found
                _reset_auth_method_to_no_auth()

        elif target == "creds":
            settings = get_settings()
            if settings.youtube.auth_method != "manual_oauth":
                console.print(
                    "[yellow]OAuth credentials are only used with manual_oauth method[/yellow]"
                )
                console.print(f"Current method: {settings.youtube.auth_method}")
                return

            if (
                not settings.youtube.oauth_client_id
                and not settings.youtube.oauth_client_secret
            ):
                console.print("[yellow]No OAuth credentials configured[/yellow]")
                return

            if not yes:
                if not click.confirm(
                    "Remove OAuth credentials? This will also sign you out."
                ):
                    console.print("[yellow]Cancelled[/yellow]")
                    return

            # Remove login tokens first
            oauth_handler = YouTubeOAuth()
            oauth_handler.revoke_authentication()

            # Remove OAuth credentials
            if OAuthClientConfig.remove_user_config():
                console.print(
                    "[green][OK] Successfully removed OAuth credentials and signed out[/green]"
                )
                _reset_auth_method_to_no_auth()
                console.print("Run 'ytmm auth mode manual_oauth' to reconfigure.")
            else:
                console.print("[red][FAIL] Failed to remove OAuth credentials[/red]")

    except Exception as e:
        console.print(f"[red]Error removing authentication data: {e}[/red]")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value (was: settings set)."""
    try:
        settings = get_settings()

        # Parse nested keys like youtube.auth_method
        keys = key.split(".")
        if len(keys) != 2:
            console.print("[red]Invalid key format. Use format: section.key[/red]")
            console.print("Example: ytmm config set youtube.auth_method auto_oauth")
            return

        section, setting = keys

        # Update the setting
        if section == "youtube":
            if setting == "auth_method":
                if value not in ["no_auth", "auto_oauth", "manual_oauth"]:
                    console.print(
                        "[red]Invalid auth_method. Must be: no_auth, auto_oauth, or manual_oauth[/red]"
                    )
                    return
                settings.youtube.auth_method = value
            elif setting == "oauth_client_id":
                settings.youtube.oauth_client_id = value
            elif setting == "oauth_client_secret":
                settings.youtube.oauth_client_secret = value
            else:
                console.print(f"[red]Unknown YouTube setting: {setting}[/red]")
                return
        elif section == "download":
            if setting == "base_path":
                settings.download.base_path = value
            elif setting == "audio_format":
                allowed_formats = ["mp3", "aac", "ogg", "wav", "flac"]
                if value.lower() not in allowed_formats:
                    console.print(
                        f"[red]Invalid audio format '{value}'. Must be one of: {', '.join(allowed_formats)}[/red]"
                    )
                    return
                settings.download.audio_format = value.lower()
            elif setting == "audio_quality":
                try:
                    quality = int(value)
                    if quality < 64 or quality > 320:
                        console.print(
                            "[red]Invalid audio quality. Must be between 64 and 320 kbps[/red]"
                        )
                        return
                    settings.download.audio_quality = quality
                except ValueError:
                    console.print("[red]Audio quality must be a valid integer[/red]")
                    return
            else:
                console.print(f"[red]Unknown download setting: {setting}[/red]")
                return
        elif section == "sync":
            if setting == "max_concurrent_downloads":
                try:
                    concurrent = int(value)
                    if concurrent < 1 or concurrent > 10:
                        console.print(
                            "[red]Invalid max concurrent downloads. Must be between 1 and 10[/red]"
                        )
                        return
                    settings.sync.max_concurrent_downloads = concurrent
                except ValueError:
                    console.print(
                        "[red]Max concurrent downloads must be a valid integer[/red]"
                    )
                    return
            elif setting == "auto_sync_interval":
                try:
                    interval = int(value)
                    if interval < 300:
                        console.print(
                            "[red]Invalid auto sync interval. Must be at least 300 seconds (5 minutes)[/red]"
                        )
                        return
                    settings.sync.auto_sync_interval = interval
                except ValueError:
                    console.print(
                        "[red]Auto sync interval must be a valid integer[/red]"
                    )
                    return
            else:
                console.print(f"[red]Unknown sync setting: {setting}[/red]")
                return
        elif section == "logging":
            if setting == "level":
                allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if value.upper() not in allowed_levels:
                    console.print(
                        f"[red]Invalid log level '{value}'. Must be one of: {', '.join(allowed_levels)}[/red]"
                    )
                    return
                settings.logging.level = value.upper()
            elif setting in ("file_path", "log_file"):
                # Normalize to the Settings.LogginConfig field name 'log_file'
                settings.logging.log_file = value
            elif setting == "backup_count":
                try:
                    backup_count = int(value)
                    if backup_count < 1 or backup_count > 20:
                        console.print(
                            "[red]Invalid backup count. Must be between 1 and 20[/red]"
                        )
                        return
                    settings.logging.backup_count = backup_count
                except ValueError:
                    console.print("[red]Backup count must be a valid integer[/red]")
                    return
            else:
                console.print(f"[red]Unknown logging setting: {setting}[/red]")
                return
        elif section == "advanced":
            if setting == "retry_attempts":
                try:
                    attempts = int(value)
                    if attempts < 1 or attempts > 10:
                        console.print(
                            "[red]Invalid retry attempts. Must be between 1 and 10[/red]"
                        )
                        return
                    settings.advanced.retry_attempts = attempts
                except ValueError:
                    console.print("[red]Retry attempts must be a valid integer[/red]")
                    return
            elif setting == "retry_delay":
                try:
                    delay = int(value)
                    if delay < 1 or delay > 60:
                        console.print(
                            "[red]Invalid retry delay. Must be between 1 and 60 seconds[/red]"
                        )
                        return
                    settings.advanced.retry_delay = delay
                except ValueError:
                    console.print("[red]Retry delay must be a valid integer[/red]")
                    return
            elif setting == "connection_timeout":
                try:
                    timeout = int(value)
                    if timeout < 5 or timeout > 300:
                        console.print(
                            "[red]Invalid connection timeout. Must be between 5 and 300 seconds[/red]"
                        )
                        return
                    settings.advanced.connection_timeout = timeout
                except ValueError:
                    console.print(
                        "[red]Connection timeout must be a valid integer[/red]"
                    )
                    return
            else:
                console.print(f"[red]Unknown advanced setting: {setting}[/red]")
                return
        else:
            console.print(f"[red]Unknown section: {section}[/red]")
            return

        # Save the updated settings
        settings_path = Path("config/settings.toml")
        import toml

        with open(settings_path, "w") as f:
            toml.dump(settings.model_dump(), f)

        console.print(f"[green][OK] Set {key} = {value}[/green]")
        console.print("Please restart the application for changes to take effect.")

    except Exception as e:
        console.print(f"[red]Error setting configuration: {e}[/red]")


@config.command("list")
@click.argument("key", required=False)
def config_list(key):
    """List configuration (optionally a single key)."""
    try:
        settings = get_settings()

        if key:
            # Parse nested keys
            keys = key.split(".")
            if len(keys) != 2:
                console.print("[red]Invalid key format. Use format: section.key[/red]")
                return

            section, setting = keys
            value = None

            if section == "youtube":
                if setting == "auth_method":
                    value = settings.youtube.auth_method
                elif setting == "oauth_client_id":
                    value = (
                        settings.youtube.oauth_client_id[:10] + "..."
                        if settings.youtube.oauth_client_id
                        else None
                    )
                elif setting == "oauth_client_secret":
                    value = "Set" if settings.youtube.oauth_client_secret else None
            elif section == "download":
                if setting == "base_path":
                    value = settings.download.base_path
                elif setting == "audio_format":
                    value = settings.download.audio_format
                elif setting == "audio_quality":
                    value = settings.download.audio_quality
            elif section == "sync":
                if setting == "max_concurrent_downloads":
                    value = settings.sync.max_concurrent_downloads
                elif setting == "auto_sync_interval":
                    value = settings.sync.auto_sync_interval
            elif section == "logging":
                if setting == "level":
                    value = settings.logging.level
                elif setting in ("file_path", "log_file"):
                    value = settings.logging.log_file

            if value is not None:
                console.print(f"{key} = {value}")
            else:
                console.print(f"[red]Setting not found or not set: {key}[/red]")
        else:
            # Show all settings
            console.print("[blue]Current Configuration:[/blue]")
            data = settings.model_dump()
            for section_name, section_data in data.items():
                console.print(f"\n[bold]{section_name}:[/bold]")
                if isinstance(section_data, dict):
                    for k, v in section_data.items():
                        if "secret" in k.lower() or "key" in k.lower():
                            v = (str(v)[:10] + "...") if v else "Not set"
                        console.print(f"  {k} = {v}")
                else:
                    console.print(f"  {section_data}")

    except Exception as e:
        console.print(f"[red]Error getting configuration: {e}[/red]")


if __name__ == "__main__":
    main()
