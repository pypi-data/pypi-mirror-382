"""Progress indicators for CLI"""

import sys
import time
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console


console = Console()


class ProgressBar:
    """Progress bar for file uploads/downloads"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        )
        self.task_id = None

    def __enter__(self):
        self.progress.start()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

    def update(self, advance: int = 1):
        """Update progress"""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=advance)


class Spinner:
    """Spinner for long-running operations"""

    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )
        self.task_id = None

    def __enter__(self):
        self.progress.start()
        self.task_id = self.progress.add_task(self.message, total=None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

    def update(self, message: str):
        """Update spinner message"""
        if self.task_id is not None:
            self.progress.update(self.task_id, description=message)
