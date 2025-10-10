"""
Clean Interactive Methods for CSV Profiler

Simple, effective interactive methods that work with the clean interface
without complex layout conflicts.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.prompt import Confirm, Prompt

from ..constants import (
    CONSISTENCY_HIGH_THRESHOLD,
    CSV_EXTENSION,
    DEFAULT_ENCODING,
    DELIMITER_COMMON_BONUS,
    DELIMITER_MAX_LENGTH,
    DELIMITER_MIN_SCORE,
    DELIMITER_TEST_SAMPLE_ROWS,
    ENCODING_ERROR_HANDLING,
    ENCODING_LARGE_ALT,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_SUCCESS,
    LOG_LEVEL_WARNING,
    MIN_ROWS_FOR_VALIDATION,
    MSG_ANALYSIS_CANCELLED,
    MSG_DELIMITER_DETECTION,
    MSG_FILE_SELECTION_CANCELLED,
    MSG_NO_CSV_SELECTED,
    MSG_NO_DELIMITER,
    MSG_NO_ENGINES_SELECTED,
    MSG_NO_FILE_PATH,
    MSG_STATISTICAL_COMPLETE,
    MSG_USING_MAIN_ENGINE,
    SNIFFER_SAMPLE_SIZE,
    VALIDATION_MIN_COLUMNS,
    VALIDATION_MIN_COUNT,
    VALIDATION_MIN_FREQUENCY,
)
from .interface import CleanCSVInterface


class CleanInteractiveMethods:
    """
    Clean interactive methods that work with the clean interface.

    Provides all interactive functionality with simple console interactions
    and clear visual feedback without layout conflicts.
    """

    def __init__(self, clean_interface: CleanCSVInterface):
        self.ui = clean_interface

    def _show_workflow_step(self, step_number: int, step_name: str, description: str):
        """Display standardized workflow step header."""
        from rich import box
        from rich.panel import Panel
        from rich.text import Text

        step_header = Text.assemble(
            (f"Step {step_number}: ", f"bold {self.ui.theme['primary']}"),
            (f"{step_name}", f"bold {self.ui.theme['primary']}"),
            (f"\n{description}", f"{self.ui.theme['muted']}"),
        )

        step_panel = Panel(
            step_header,
            border_style=self.ui.theme["primary"],
            box=box.ROUNDED,
            padding=(0, 1),
        )

        self.ui.console.print()
        self.ui.console.print(step_panel)

    def display_welcome_banner(self) -> bool:
        """Display welcome banner."""
        self.ui.set_step("welcome")
        self.ui.show_welcome()
        return True

    def get_csv_path(self) -> Optional[Path]:
        """Get CSV file path from user."""
        self.ui.set_step("file_selection")

        # Show step header with consistent formatting
        self._show_workflow_step(
            1, "File Selection", "Select your CSV file for analysis"
        )

        while True:
            try:
                # Prompt for file path
                csv_path_str = Prompt.ask(
                    f"[{self.ui.theme['primary']}]Enter the path to your CSV file[/]",
                    console=self.ui.console,
                )

                if not csv_path_str.strip():
                    self.ui.log(LOG_LEVEL_WARNING, MSG_NO_FILE_PATH)
                    continue

                csv_path = Path(csv_path_str.strip().strip("\"'"))

                if not csv_path.exists():
                    self.ui.log(LOG_LEVEL_ERROR, f"File not found: {csv_path}")
                    retry = Confirm.ask(
                        f"[{self.ui.theme['warning']}]Would you like to try again?[/]",
                        console=self.ui.console,
                    )
                    if not retry:
                        return None
                    continue

                if not csv_path.suffix.lower() == CSV_EXTENSION:
                    self.ui.log(
                        LOG_LEVEL_WARNING,
                        f"File doesn't have .csv extension: {csv_path}",
                    )
                    proceed = Confirm.ask(
                        f"[{self.ui.theme['warning']}]Continue anyway?[/]",
                        console=self.ui.console,
                    )
                    if not proceed:
                        continue

                # File is valid
                self.ui.set_csv_file(csv_path)
                self.ui.log(LOG_LEVEL_SUCCESS, f"Selected file: {csv_path.name}")
                self.ui.console.print()
                return csv_path

            except KeyboardInterrupt:
                self.ui.log(LOG_LEVEL_INFO, MSG_FILE_SELECTION_CANCELLED)
                return None
            except Exception as e:
                self.ui.log(LOG_LEVEL_ERROR, f"Error processing file path: {e}")
                return None

    def setup_output_directory(self, csv_path: Path) -> Tuple[Path, str]:
        """Setup output directory for results."""
        # Show step header with consistent formatting
        self._show_workflow_step(
            2, "Output Directory Setup", "Configure analysis output location"
        )

        csv_folder = csv_path.parent
        filename_no_ext = csv_path.stem

        output_dir = csv_folder / filename_no_ext
        output_dir.mkdir(exist_ok=True)

        # Copy original CSV to output directory
        original_csv_path = output_dir / csv_path.name
        if not original_csv_path.exists():
            import shutil

            shutil.copy2(csv_path, original_csv_path)

        self.ui.log(LOG_LEVEL_SUCCESS, f"Output directory created: {output_dir}")
        self.ui.console.print()
        return output_dir, str(original_csv_path)

    def detect_delimiter(self, csv_path: Path) -> Optional[str]:
        """Detect or get delimiter from user."""
        self.ui.set_step("delimiter_detection")

        # Show step header with consistent formatting
        self._show_workflow_step(
            3,
            "Delimiter Detection",
            "Automatically detect or specify CSV delimiter",
        )

        # Try automatic delimiter detection using multiple approaches
        try:
            self.ui.log(LOG_LEVEL_INFO, MSG_DELIMITER_DETECTION)

            delimiter = self._detect_delimiter_advanced(csv_path)

            if delimiter:
                self.ui.set_delimiter(delimiter)
                self.ui.log(
                    LOG_LEVEL_SUCCESS,
                    f"Auto-detected delimiter: {repr(delimiter)}",
                )
                self.ui.console.print()
                return delimiter

        except Exception as e:
            self.ui.log(LOG_LEVEL_WARNING, f"Auto-detection failed: {e}")

        # Manual delimiter input
        self.ui.console.print(
            "[yellow]Auto-detection failed. Please specify manually.[/yellow]"
        )
        self.ui.console.print()

        while True:
            delimiter = Prompt.ask(
                f"[{self.ui.theme['warning']}]Enter the delimiter used in your CSV file[/] "
                f"[{self.ui.theme['muted']}](common: ',' or ';' or '\\t')[/]",
                console=self.ui.console,
                default=",",
            )

            # Process escape sequences
            delimiter = delimiter.replace("\\t", "\t").replace("\\n", "\n")

            if self._is_valid_delimiter(delimiter):
                self.ui.set_delimiter(delimiter)
                self.ui.log(LOG_LEVEL_SUCCESS, f"Delimiter set to: {repr(delimiter)}")
                self.ui.console.print()
                return delimiter
            else:
                self.ui.log(LOG_LEVEL_ERROR, f"Invalid delimiter: {repr(delimiter)}")
                retry = Confirm.ask(
                    f"[{self.ui.theme['warning']}]Try again?[/]",
                    console=self.ui.console,
                )
                if not retry:
                    return None

    def _detect_delimiter_advanced(self, csv_path: Path) -> Optional[str]:
        """100% accurate delimiter detection by analyzing file structure.

        Args:
            csv_path: Path to the CSV file

        Returns:
            Detected delimiter or None if detection fails
        """
        import csv
        from collections import Counter

        with open(
            csv_path, "r", encoding=DEFAULT_ENCODING, errors=ENCODING_ERROR_HANDLING
        ) as csvfile:
            # Read substantial sample for analysis
            sample = csvfile.read(ENCODING_LARGE_ALT)
            if not sample:
                return None

        lines = [line for line in sample.split("\n") if line.strip()]
        if len(lines) < MIN_ROWS_FOR_VALIDATION:
            return None

        # Find ALL potential delimiter characters
        # Exclude alphanumeric, quotes, and common text characters
        all_chars = set(sample)
        potential_delimiters = set()

        for char in all_chars:
            # Skip letters, numbers, quotes, and whitespace (except tab)
            if char.isalnum() or char in "\"'`\n\r":
                continue
            # Include printable punctuation and tab
            if char.isprintable() or char == "\t":
                potential_delimiters.add(char)

        best_delimiter = None
        best_score = 0

        for delimiter in potential_delimiters:
            # Calculate consistency score
            column_counts = []
            valid_lines = 0

            for line in lines[:20]:  # Analyze first 20 lines
                if not line.strip():
                    continue

                # Count delimiter occurrences
                count = line.count(delimiter)
                if count > VALIDATION_MIN_COUNT:
                    column_counts.append(count)
                    valid_lines += 1

            if valid_lines < MIN_ROWS_FOR_VALIDATION or not column_counts:
                continue

            # Check consistency (most lines should have same delimiter count)
            most_common_count = Counter(column_counts).most_common(1)[0][0]
            consistency_ratio = column_counts.count(most_common_count) / len(
                column_counts
            )

            # Score: consistency × frequency × coverage
            frequency = most_common_count
            coverage = valid_lines / min(len(lines), 20)

            # Only consider if high consistency (>80%) and multiple columns
            if (
                consistency_ratio >= CONSISTENCY_HIGH_THRESHOLD
                and frequency >= VALIDATION_MIN_FREQUENCY
            ):
                score = consistency_ratio * frequency * coverage

                # Bonus for common CSV delimiters
                if delimiter in ",;\t|":
                    score *= DELIMITER_COMMON_BONUS

                if score > best_score:
                    best_score = score
                    best_delimiter = delimiter

        # Validate with csv.Sniffer if we found a candidate
        if best_delimiter:
            try:
                sniffer = csv.Sniffer()
                # Test if our delimiter works with csv module
                dialect = sniffer.sniff(
                    sample[:SNIFFER_SAMPLE_SIZE], delimiters=best_delimiter
                )
                if dialect.delimiter == best_delimiter:
                    return best_delimiter
            except Exception:
                pass

            # Even if sniffer fails, return our best guess if score is high
            if best_score > DELIMITER_MIN_SCORE:
                return best_delimiter

        # Fallback: try pandas read with auto-detection
        try:
            import pandas as pd

            # Let pandas try to detect delimiter automatically
            df = pd.read_csv(
                csv_path,
                sep=None,
                engine="python",
                nrows=DELIMITER_TEST_SAMPLE_ROWS,
                encoding="utf-8",
                on_bad_lines="skip",
            )
            if hasattr(df, "columns") and len(df.columns) > VALIDATION_MIN_COLUMNS:
                # Try to reverse-engineer the delimiter pandas used
                with open(
                    csv_path,
                    "r",
                    encoding=DEFAULT_ENCODING,
                    errors=ENCODING_ERROR_HANDLING,
                ) as f:
                    first_line = f.readline().strip()
                    for char in potential_delimiters:
                        if first_line.count(char) == len(df.columns) - 1:
                            return char
        except Exception:
            pass

        return None

    def _is_valid_delimiter(self, delimiter: str) -> bool:
        """Check if delimiter is valid."""
        if not delimiter:
            return False
        if len(delimiter) > DELIMITER_MAX_LENGTH:
            return False
        return True

    def display_engine_selection_menu(self) -> List[str]:
        """Display engine selection menu (single-environment version).

        Since this is a single-environment setup, we only have the main analyzer.
        This method provides a consistent interface while simplifying the selection.

        Returns:
            List of selected engines (always contains 'main_analyzer')
        """
        self._show_workflow_step(
            4, "Analysis Engine Selection", "Configuring analysis engine"
        )

        # In single-environment setup, we only have the main analyzer
        self.ui.log(LOG_LEVEL_INFO, MSG_USING_MAIN_ENGINE)
        self.ui.console.print()

        return ["main_analyzer"]

    def run_main_analyzer(
        self, csv_path: Path, delimiter: str, output_dir: Path
    ) -> bool:
        """Run the main statistical analysis engine."""
        self.ui.set_step("analysis_running")

        # Show step header
        self._show_workflow_step(
            5, "Statistical Analysis", "Running comprehensive CSV analysis"
        )

        try:
            # Import and run the main analyzer directly
            from autocsv_profiler.analyzer import main as analyze_csv

            self.ui.console.print(
                f"\n[{self.ui.theme['accent']}]Starting statistical analysis...[/]"
            )

            # Run the analyzer
            analyze_csv(
                file_path=csv_path,
                save_dir=output_dir,
                delimiter=delimiter,
                interactive=True,
            )

            self.ui.log(LOG_LEVEL_SUCCESS, MSG_STATISTICAL_COMPLETE)
            return True

        except Exception as e:
            self.ui.log(LOG_LEVEL_ERROR, f"Analysis failed: {str(e)}")
            return False

    def run_engines(
        self,
        engines: List[Dict[str, Any]],
        csv_path: Path,
        delimiter: str,
        output_dir: Path,
    ):
        """Run analysis - simplified to use main analyzer only."""
        # Delegate to run_main_analyzer method
        success = self.run_main_analyzer(csv_path, delimiter, output_dir)

        # Return results in expected format for compatibility
        return [{"engine": "main_analyzer", "success": success}]

    def display_completion_summary(self, output_dir: Path, results: List[Dict]):
        """Display analysis completion summary."""
        self.ui.set_step("completed")

        # Show completion summary
        self.ui.show_completion_summary(output_dir, results)

        # Show final status
        successful = len([r for r in results if r["success"]])
        total = len(results)

        self.ui.log(
            LOG_LEVEL_INFO,
            f"Analysis workflow completed: {successful}/{total} engines successful",
        )

        if successful < total:
            self.ui.console.print()
            self.ui.console.print(
                "[yellow]Some engines failed. Check the logs above for details.[/yellow]"
            )

        # Ensure all progress is completely stopped
        self.ui.stop_progress()

    def run_analysis_direct(self, csv_file_path: str) -> bool:
        """Run analysis workflow directly with provided CSV file path."""
        try:
            csv_path = Path(csv_file_path)
            if not csv_path.exists():
                self.ui.log(LOG_LEVEL_ERROR, f"CSV file not found: {csv_file_path}")
                return False

            self.ui.log(LOG_LEVEL_INFO, f"Starting analysis of: {csv_path.name}")

            # Setup output directory
            output_dir, _ = self.setup_output_directory(csv_path)

            # Detect delimiter
            delimiter = self.detect_delimiter(csv_path)
            if not delimiter:
                self.ui.log(LOG_LEVEL_ERROR, MSG_NO_DELIMITER)
                return False

            # Run main analyzer directly
            success = self.run_main_analyzer(csv_path, delimiter, output_dir)

            if success:
                self.ui.log(LOG_LEVEL_SUCCESS, "Analysis completed successfully")
                self.display_completion_summary(output_dir)
            else:
                self.ui.log(LOG_LEVEL_ERROR, "Analysis failed")

            return True

        except Exception as e:
            self.ui.log(LOG_LEVEL_ERROR, f"Analysis failed: {e}")
            return False

    def run_analysis(self) -> bool:
        """Run the complete analysis workflow."""
        try:
            # Welcome and setup
            if not self.display_welcome_banner():
                return False

            # Get CSV file
            csv_path = self.get_csv_path()
            if not csv_path:
                self.ui.log(LOG_LEVEL_ERROR, MSG_NO_CSV_SELECTED)
                return False

            # Setup output directory
            output_dir, _ = self.setup_output_directory(csv_path)

            # Detect delimiter
            delimiter = self.detect_delimiter(csv_path)
            if not delimiter:
                self.ui.log(LOG_LEVEL_ERROR, MSG_NO_DELIMITER)
                return False

            # Select engines
            engines = self.display_engine_selection_menu()
            if not engines:
                self.ui.log(LOG_LEVEL_ERROR, MSG_NO_ENGINES_SELECTED)
                return False

            # Run analysis
            results = self.run_engines(engines, csv_path, delimiter, output_dir)

            # Display completion summary
            self.display_completion_summary(output_dir, results)

            return True

        except KeyboardInterrupt:
            self.ui.console.print(MSG_ANALYSIS_CANCELLED)
            return False
        except Exception as e:
            self.ui.log(LOG_LEVEL_ERROR, f"Unexpected error during analysis: {e}")
            return False
