"""Output formatting utilities"""

from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table as RichTable


console = Console()


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size"""
    if bytes_size is None or bytes_size == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration"""
    if seconds is None or seconds == 0:
        return "-"

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp to relative time"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except Exception:
        return timestamp


def format_table(headers: List[str], rows: List[List[Any]], title: str = None) -> None:
    """Print formatted table using rich"""
    table = RichTable(title=title, show_header=True, header_style="bold cyan")

    for header in headers:
        table.add_column(header)

    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    console.print(table)


def print_success(message: str) -> None:
    """Print success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message"""
    console.print(f"[red]✗[/red] {message}", style="red")


def print_warning(message: str) -> None:
    """Print warning message"""
    console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def print_info(message: str) -> None:
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {message}")
