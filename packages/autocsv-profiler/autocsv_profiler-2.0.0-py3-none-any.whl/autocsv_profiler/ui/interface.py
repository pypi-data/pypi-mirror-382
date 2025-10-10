"""
Clean CSV Profiler Interface

A simple, effective interface that avoids Rich Live display conflicts
while maintaining clean appearance and functionality.
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from ..constants import (
    BYTES_TO_MB_DIVISOR,
    DEFAULT_ENCODING,
    FILE_MODE_READ,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_SUCCESS,
    LOG_LEVEL_WARNING,
    PATH_LENGTH_THRESHOLD,
    PATH_PARTS_KEEP,
    REPORT_COLUMN_WIDTH_ENGINE,
    REPORT_COLUMN_WIDTH_STATUS,
    UI_PADDING_HORIZONTAL,
    UI_PADDING_VERTICAL,
    VALIDATION_ERROR_MESSAGE_LENGTH,
    VALIDATION_PATH_LENGTH,
    VALIDATION_PATH_PARTS_MIN,
)


@dataclass
class SystemInfo:
    """System information for status display."""

    app_name: str = "AutoCSV Profiler"
    version: str = "2.0.0"
    python_version: str = ""
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    active_environment: str = "main"

    def __post_init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


class CleanCSVInterface:
    """
    Clean CSV Profiler Interface

    Simple, effective interface without complex layout conflicts.
    Uses Rich components individually without Live display system.
    """

    def __init__(self, config_path: Optional[Path] = None):
        # Initialize console
        self.console = Console(force_terminal=True, legacy_windows=True)

        # Use embedded settings configuration
        from autocsv_profiler.config.settings import settings

        self.config = settings.to_dict()
        # Optional external config override (deprecated but maintained for compatibility)
        self.config_path = config_path

        # System information (initialized but not populated until needed)
        self.system_info = SystemInfo()

        # UI state
        self.current_step = "initializing"
        self.current_csv_path = None
        self.current_delimiter = None
        self.selected_engines = []

        # Progress tracking
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=False,
        )

        # Color theme
        self.theme = {
            "primary": "cyan",
            "secondary": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "blue",
            "accent": "magenta",
            "muted": "dim white",
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from embedded settings with optional external override."""
        # Use embedded settings as the base
        from autocsv_profiler.config.settings import settings

        base_config = settings.to_dict()

        # Optional external config override (maintained for compatibility)
        if self.config_path and self.config_path.exists():
            try:
                with open(
                    self.config_path, FILE_MODE_READ, encoding=DEFAULT_ENCODING
                ) as f:
                    external_config = yaml.safe_load(f)
                    if external_config:
                        # Merge external config with embedded settings
                        merged_config = base_config.copy()
                        merged_config.update(external_config)
                        return merged_config
            except Exception as e:
                self.console.print(
                    f"[red]Warning: Could not load external config: {e}[/red]"
                )

        return base_config

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process(os.getpid())
            memory_bytes = process.memory_info().rss
            return memory_bytes / BYTES_TO_MB_DIVISOR  # Convert to MB
        except Exception:
            return 0.0

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            # Use interval=None for immediate reading to avoid delays
            return psutil.cpu_percent(interval=None)
        except Exception:
            return 0.0

    def show_welcome(self):
        """Display welcome message and system information."""

        # Update system info just before display (avoid initialization delays)
        self.system_info.memory_usage = self._get_memory_usage()
        self.system_info.cpu_usage = self._get_cpu_usage()

        version_str = self.config.get("project", {}).get(
            "version", self.system_info.version
        )

        # Simple, clean header that works across all terminals
        app_title = "AutoCSV Profiler"
        version_line = f"Version {version_str}"

        # Create clean header content without complex formatting
        welcome_text = f"[bold {self.theme['primary']}]{app_title}[/bold {self.theme['primary']}]\n"
        welcome_text += (
            f"[{self.theme['accent']}]{version_line}[/{self.theme['accent']}]\n"
        )
        welcome_text += f"\n[{self.theme['muted']}]CSV Data Analysis Toolkit[/{self.theme['muted']}]"

        welcome_panel = Panel(
            Align.center(welcome_text),
            title="[bold]Welcome[/bold]",
            border_style=self.theme["primary"],
            padding=(UI_PADDING_VERTICAL, UI_PADDING_HORIZONTAL),
            box=box.ROUNDED,
        )
        self.console.print(welcome_panel)
        self.console.print()

    def show_step_header(self, step_number: int, step_name: str, description: str):
        """Display step header."""
        step_panel = Panel(
            f"{description}",
            title=f"[{self.theme['primary']}]Step {step_number}: {step_name}[/{self.theme['primary']}]",
            border_style=self.theme["primary"],
        )
        self.console.print(step_panel)
        self.console.print()

    def show_step_content(self, step_number: int, step_name: str, content: str):
        """Display step content with Rule header."""
        from rich.rule import Rule

        self.console.print(
            Rule(
                f"[{self.theme['primary']}]Step {step_number}: {step_name}[/{self.theme['primary']}]",
                style=self.theme["primary"],
            )
        )
        self.console.print(content)
        self.console.print()

    def start_step_panel(self, step_number: int, step_name: str, description: str):
        """Start a step panel that will collect content."""
        self.current_step_number = step_number
        self.current_step_name = step_name
        self.current_step_description = description
        self.step_content_lines = [f"{description}\n"]

    def add_step_content(self, content: str):
        """Add content to the current step panel."""
        if hasattr(self, "step_content_lines"):
            self.step_content_lines.append(content)

    def finish_step_panel(self):
        """Display the completed step panel with all content."""
        if hasattr(self, "step_content_lines"):
            content = "\n".join(self.step_content_lines)
            step_panel = Panel(
                content,
                title=(
                    f"[{self.theme['primary']}]Step {self.current_step_number}: "
                    f"{self.current_step_name}[/{self.theme['primary']}]"
                ),
                border_style=self.theme["primary"],
            )
            self.console.print(step_panel)
            self.console.print()
            # Clear the content
            del self.step_content_lines

    def show_status_line(self):
        """Show current status line."""
        # Update system info
        self.system_info.memory_usage = self._get_memory_usage()

        file_name = self.current_csv_path.name if self.current_csv_path else "None"
        engine_count = len(self.selected_engines)
        delimiter_display = (
            repr(self.current_delimiter) if self.current_delimiter else "Not set"
        )

        status_text = (
            f"[{self.theme['info']}]Status:[/{self.theme['info']}] "
            f"[{self.theme['accent']}]{self.current_step.replace('_', ' ').title()}[/{self.theme['accent']}] | "
            f"[{self.theme['success']}]File: {file_name}[/{self.theme['success']}] | "
            f"[{self.theme['warning']}]Delimiter: {delimiter_display}[/{self.theme['warning']}] | "
            f"[{self.theme['secondary']}]Engines: {engine_count}[/{self.theme['secondary']}] | "
            f"[{self.theme['muted']}]Memory: {self.system_info.memory_usage:.1f}MB[/{self.theme['muted']}]"
        )

        status_panel = Panel(status_text, border_style="dim blue", box=box.SIMPLE)
        self.console.print(status_panel)
        self.console.print()

    def show_completion_summary(self, output_dir: Path, results: List[Dict]):
        """Display analysis completion summary with improved formatting."""
        successful_engines = [r for r in results if r["success"]]
        failed_engines = [r for r in results if not r["success"]]

        # Results summary with consistent styling
        summary_table = Table(
            title="[bold]Analysis Results[/bold]",
            show_header=True,
            header_style=f"bold {self.theme['primary']}",
            box=box.ROUNDED,
            border_style=self.theme["primary"],
        )
        summary_table.add_column(
            "Engine", style=self.theme["secondary"], width=REPORT_COLUMN_WIDTH_ENGINE
        )
        summary_table.add_column(
            "Status", style="bold", width=REPORT_COLUMN_WIDTH_STATUS, justify="center"
        )
        summary_table.add_column("Details", style=self.theme["muted"])

        for result in results:
            if result["success"]:
                status_symbol = "[green]+ SUCCESS[/green]"
                details = "Analysis completed successfully"
            else:
                status_symbol = "[red]X FAILED[/red]"
                error_msg = result.get("error", "Unknown error")
                details = (
                    error_msg[:VALIDATION_ERROR_MESSAGE_LENGTH] + "..."
                    if len(error_msg) > VALIDATION_ERROR_MESSAGE_LENGTH
                    else error_msg
                )

            # Clean up engine name for display
            engine_name = result["engine"].replace(".py", "")
            summary_table.add_row(engine_name, status_symbol, details)

        self.console.print(summary_table)
        self.console.print()

        # Create success indicator
        if len(successful_engines) == len(results):
            status_indicator = "[SUCCESS]"
            status_text = "All engines completed successfully!"
            status_color = self.theme["success"]
        elif successful_engines:
            status_indicator = "[PARTIAL]"
            status_text = (
                f"{len(successful_engines)} of {len(results)} engines completed"
            )
            status_color = self.theme["warning"]
        else:
            status_indicator = "[FAILED]"
            status_text = "All engines failed"
            status_color = self.theme["error"]

        # Truncate output directory path for display
        display_path = (
            self._truncate_file_path(str(output_dir))
            if len(str(output_dir)) > VALIDATION_PATH_LENGTH
            else str(output_dir)
        )

        # Final summary panel with clean formatting
        summary_text = f"""[bold {status_color}]{status_indicator} {status_text}[/bold {status_color}]

[{self.theme['info']}]Results saved to:[/{self.theme['info']}]
[bold]{display_path}[/bold]

[{self.theme['success']}]Successful:[/{self.theme['success']}] {len(successful_engines)} engines"""

        if failed_engines:
            summary_text += f"""
[{self.theme['error']}]Failed:[/{self.theme['error']}] {len(failed_engines)} engines"""

        final_panel = Panel(
            Align.center(summary_text),
            title="[bold]Analysis Complete[/bold]",
            border_style=status_color,
            box=box.ROUNDED,
            padding=(UI_PADDING_VERTICAL, UI_PADDING_HORIZONTAL),
        )

        self.console.print(final_panel)

    def log(self, level: str, message: str, show_timestamp: bool = False):
        """Log a message with consistent formatting and optional timestamp."""
        level_symbols = {
            LOG_LEVEL_INFO: "*",
            LOG_LEVEL_SUCCESS: "+",
            LOG_LEVEL_WARNING: "!",
            LOG_LEVEL_ERROR: "X",
            LOG_LEVEL_DEBUG: "-",
        }

        level_colors = {
            LOG_LEVEL_INFO: self.theme["info"],
            LOG_LEVEL_SUCCESS: self.theme["success"],
            LOG_LEVEL_WARNING: self.theme["warning"],
            LOG_LEVEL_ERROR: self.theme["error"],
            LOG_LEVEL_DEBUG: self.theme["muted"],
        }

        symbol = level_symbols.get(level, "*")
        color = level_colors.get(level, "white")

        # Truncate very long file paths for readability
        if len(message) > PATH_LENGTH_THRESHOLD and ("\\" in message or "/" in message):
            message = self._truncate_file_path(message)

        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_text = f"[dim]{timestamp}[/dim] [{color}]{symbol}[/{color}] {message}"
        else:
            log_text = f"[{color}]{symbol}[/{color}] {message}"

        self.console.print(log_text)

    def _truncate_file_path(self, message: str) -> str:
        """Truncate long file paths in messages for better readability."""
        import re
        from pathlib import Path

        # Find path-like strings in the message
        path_candidates = []

        # Look for Windows-style paths
        windows_paths = re.findall(r"[A-Za-z]:\\[^\\]+(?:\\[^\\]+)*", message)
        path_candidates.extend(windows_paths)

        # Look for Unix-style paths
        unix_paths = re.findall(r"/[^/\s]+(?:/[^/\s]+)+", message)
        path_candidates.extend(unix_paths)

        # Truncate each path found
        for path_str in path_candidates:
            if (
                len(path_str) > VALIDATION_PATH_LENGTH
            ):  # Only truncate if significantly long
                try:
                    path = Path(path_str)
                    # Keep first PATH_PARTS_KEEP parts, last PATH_PARTS_KEEP parts, and show meaningful truncation
                    parts = path.parts
                    if len(parts) > VALIDATION_PATH_PARTS_MIN:
                        # For Windows: C:\...\parent\filename
                        # For Unix: /home/...parent/filename
                        truncated = str(
                            Path(*parts[:PATH_PARTS_KEEP])
                            / "..."
                            / Path(*parts[-PATH_PARTS_KEEP:])
                        )
                        message = message.replace(path_str, truncated)
                except Exception:
                    # Fallback: simple string truncation
                    if len(path_str) > VALIDATION_PATH_LENGTH:
                        truncated = path_str[:30] + "..." + path_str[-25:]
                        message = message.replace(path_str, truncated)

        return message

    def start_progress(self, description: str, total: int = None):
        """Start a progress task."""
        task = self.progress.add_task(description, total=total)
        if not self.progress.live.is_started:
            self.progress.start()
        return task

    def update_progress(self, task_id, advance: int = 1):
        """Update progress for a task."""
        self.progress.update(task_id, advance=advance)

    def finish_progress(self, task_id, success: bool = True):
        """Finish a progress task."""
        self.progress.update(task_id, completed=True)

    def stop_progress(self):
        """Stop the progress display and clear all tasks."""
        try:
            if hasattr(self.progress, "live") and self.progress.live.is_started:
                self.progress.stop()
            # Clear any remaining tasks
            self.progress.reset()
            # Force a console refresh to clear any lingering progress artifacts
            self.console.print("", end="")
        except Exception:
            # Silently handle any progress cleanup issues
            pass

    # State management methods
    def set_step(self, step: str):
        """Set current step."""
        self.current_step = step

    def set_csv_file(self, csv_path: Path):
        """Set current CSV file."""
        self.current_csv_path = csv_path

    def set_delimiter(self, delimiter: str):
        """Set current delimiter."""
        self.current_delimiter = delimiter

    def set_selected_engines(self, engines: List[Dict]):
        """Set selected engines."""
        self.selected_engines = engines
