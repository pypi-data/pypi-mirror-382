"""
Color utilities for YT Music Manager CLI (YTMM CLI).
Provides consistent cross-platform color output functions.
"""

from typing import Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .logging_utils import get_console


def print_success(message: str, console: Optional[Console] = None) -> None:
    """Print a success message with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(message: str, console: Optional[Console] = None) -> None:
    """Print a warning message with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_error(message: str, console: Optional[Console] = None) -> None:
    """Print an error message with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str, console: Optional[Console] = None) -> None:
    """Print an info message with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_banner(
    title: str, subtitle: str = "", version: str = "", console: Optional[Console] = None
) -> None:
    """Print a styled banner with consistent formatting."""
    if console is None:
        console = get_console()

    banner_text = f"[bold cyan]{title}[/bold cyan]"
    if version:
        banner_text += f" [green]v{version}[/green]"
    if subtitle:
        banner_text += f"\n[dim]{subtitle}[/dim]"

    console.print(Panel.fit(banner_text, border_style="blue", padding=(0, 1)))


def print_table_row(
    label: str, value: Any, status: str = "", console: Optional[Console] = None
) -> None:
    """Print a formatted table-like row with consistent styling."""
    if console is None:
        console = get_console()

    # Format status with color
    status_text = ""
    if status:
        if status.upper() in ["OK", "SUCCESS", "VALID"]:
            status_text = f" [bold green][OK][/bold green]"
        elif status.upper() in ["FAIL", "ERROR", "INVALID"]:
            status_text = f" [bold red][FAIL][/bold red]"
        elif status.upper() in ["WARN", "WARNING"]:
            status_text = f" [bold yellow][WARN][/bold yellow]"
        else:
            status_text = f" [dim]{status}[/dim]"

    console.print(f"[cyan]{label}[/cyan]: [white]{value}[/white]{status_text}")


def print_progress_update(message: str, console: Optional[Console] = None) -> None:
    """Print a progress update with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"[bold blue]→[/bold blue] {message}")


def print_section_header(title: str, console: Optional[Console] = None) -> None:
    """Print a section header with consistent styling."""
    if console is None:
        console = get_console()
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("─" * len(title))


# For backwards compatibility - these match your existing functions in logging_utils
def styled_print(
    message: str, style: str = "", console: Optional[Console] = None
) -> None:
    """Print a message with custom Rich markup styling."""
    if console is None:
        console = get_console()

    if style:
        console.print(f"[{style}]{message}[/{style}]")
    else:
        console.print(message)


# Convenience functions that match common patterns
ok = lambda msg: print_success(msg)
warn = lambda msg: print_warning(msg)
error = lambda msg: print_error(msg)
info = lambda msg: print_info(msg)
