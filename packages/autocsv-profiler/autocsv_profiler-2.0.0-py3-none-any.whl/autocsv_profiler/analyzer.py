import contextlib
import logging
import os
import sys
from io import StringIO
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import psutil
from tqdm import tqdm

from autocsv_profiler.constants import (
    ANALYZER_PROGRESS_TOTAL,
    BYTES_PER_GB,
    BYTES_PER_KB,
    CLI_MIN_ARGS,
    CLI_VALID_ARGUMENT_COUNTS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DELIMITER,
    DEFAULT_ENCODING,
    DEFAULT_MEMORY_LIMIT_GB,
    DEFAULT_MEMORY_LIMIT_INT,
    DELIMITER_TEST_SAMPLE_ROWS,
    ENCODING_DETECTION_SAMPLE_SIZE,
    ERROR_CSV_READING_FAILED,
    ERROR_FILE_NOT_FOUND,
    ERROR_MEMORY_EXCEEDED,
    ERROR_NO_DATA_CHUNKS,
    ERROR_PARSING_CSV,
    FALLBACK_CONFIDENCE,
    FILE_MODE_READ,
    FILE_MODE_READ_BINARY,
    HEADER_GENERATING_REPORTS,
    HEADER_SEPARATOR,
    LOGGER_AUTOCSV,
    MSG_NO_FILES_FOUND,
    MSG_SKIP_INTERACTIVE,
    MSG_TRACEBACK,
    MSG_USAGE,
    OUTPUT_CATEGORICAL_STATS,
    OUTPUT_CATEGORICAL_SUMMARY,
    OUTPUT_DATASET_ANALYSIS,
    OUTPUT_DISTINCT_VALUES,
    OUTPUT_NUMERICAL_STATS,
    OUTPUT_NUMERICAL_SUMMARY,
    PROG_ALL_SAVED_FILES,
    PROG_ENCODING_DETECTION,
    PROG_PROCESSING,
    PROG_SAVED_FILES,
    PROGRESS_SCAN_COMPLETE,
    PROGRESS_SCAN_TOTAL,
    PROGRESS_UNIT_CHUNK,
    SCAN_CSV_PATTERN,
    SCAN_PNG_PATTERN,
    SCAN_TXT_PATTERN,
    TEST_DELIMITERS,
    TF_LOG_LEVEL_ENV,
    TF_LOG_LEVEL_VALUE,
    WARNING_DELIMITER_DEFAULT,
)
from autocsv_profiler.core.dataset_info import (
    data_table_range_min_max_distinct,
    distinct_val_tabular_txt,
    generate_complete_report,
)
from autocsv_profiler.core.exceptions import FileProcessingError
from autocsv_profiler.core.utils import exclude_columns, memory_usage
from autocsv_profiler.core.warnings import auto_configure_warnings
from autocsv_profiler.plots import select_and_execute_visualizations
from autocsv_profiler.stats import TableOne_groupby_column, researchpy_descriptive_stats

PathLike = Union[str, Path]

try:
    from autocsv_profiler.ui.components import (
        TableOne_groupby_column_improved,
        exclude_columns_improved,
        select_and_execute_visualizations_improved,
    )

    HAS_UI_COMPONENTS = True
except ImportError:
    # Create compatible wrapper functions for fallbacks
    def exclude_columns_improved(  # type: ignore[misc]
        df: Any,
        output_path: PathLike,
        console: Optional[Any] = None,
        delimiter: str = ",",
    ) -> Any:
        return exclude_columns(df, output_path, delimiter)

    def TableOne_groupby_column_improved(  # type: ignore[misc]
        df: Any, output_path: PathLike, console: Optional[Any] = None
    ) -> Any:
        return TableOne_groupby_column(df, output_path)

    def select_and_execute_visualizations_improved(  # type: ignore[misc]
        df: Any, columns: Any, console: Optional[Any] = None
    ) -> Any:
        return select_and_execute_visualizations(df, columns)

    HAS_UI_COMPONENTS = False

auto_configure_warnings()


def main(
    file_path: PathLike,
    save_dir: PathLike,
    delimiter: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    memory_limit_gb: Union[int, float] = DEFAULT_MEMORY_LIMIT_GB,  # type: ignore[assignment]
    interactive: bool = True,
) -> None:
    """Execute the full data analysis workflow.

    Args:
        file_path: Path to the CSV file to analyze
        save_dir: Directory to save analysis results
        delimiter: CSV delimiter. If None, will try to detect.
        chunk_size: Number of rows to read at a time. Defaults to DEFAULT_CHUNK_SIZE.
        memory_limit_gb: Memory limit in GB. Defaults to DEFAULT_MEMORY_LIMIT_GB.
        interactive: Whether to run in interactive mode.
    """
    os.environ[TF_LOG_LEVEL_ENV] = TF_LOG_LEVEL_VALUE

    try:
        try:
            file_size = os.path.getsize(file_path)
            total_chunks = file_size // (
                chunk_size * BYTES_PER_KB
            )  # Approximate number of chunks

            chunks = []

            with tqdm(
                total=total_chunks, desc=PROG_PROCESSING, unit=PROGRESS_UNIT_CHUNK
            ) as pbar:
                # Use provided delimiter or try to detect it
                if delimiter is None:
                    with open(file_path, FILE_MODE_READ) as f:
                        first_line = f.readline()
                        delimiter = (
                            DEFAULT_DELIMITER
                            if DEFAULT_DELIMITER in first_line
                            else (";" if ";" in first_line else None)
                        )

                    if not delimiter:
                        for test_delimiter in TEST_DELIMITERS:
                            try:
                                pd.read_csv(
                                    file_path,
                                    sep=test_delimiter,
                                    nrows=DELIMITER_TEST_SAMPLE_ROWS,
                                )
                                delimiter = test_delimiter
                                break
                            except Exception:
                                continue

                        if not delimiter:
                            delimiter = DEFAULT_DELIMITER
                            print(WARNING_DELIMITER_DEFAULT)

                try:
                    for chunk in pd.read_csv(
                        file_path, sep=delimiter, chunksize=chunk_size
                    ):
                        memory_usage_gb = (
                            psutil.Process(os.getpid()).memory_info().rss / BYTES_PER_GB
                        )
                        if memory_usage_gb > memory_limit_gb:
                            raise MemoryError(
                                ERROR_MEMORY_EXCEEDED.format(memory_limit_gb)
                            )

                        chunks.append(chunk)
                        pbar.update(1)
                except Exception as csv_error:
                    print(
                        f"[ERROR] Failed to read CSV with delimiter {repr(delimiter)}: {csv_error}"
                    )
                    raise FileProcessingError(
                        ERROR_CSV_READING_FAILED.format(repr(delimiter), csv_error)
                    )

            if not chunks:
                raise FileProcessingError(ERROR_NO_DATA_CHUNKS)

            data = pd.concat(chunks, ignore_index=True)

            # Keep original data unchanged
            data_copy = data.copy()
        except FileNotFoundError:
            raise FileProcessingError(ERROR_FILE_NOT_FOUND.format(file_path))
        except pd.errors.ParserError as e:
            raise FileProcessingError(ERROR_PARSING_CSV.format(e))

        # Configure logging to save in output directory (if file logging is enabled)
        from autocsv_profiler.config import settings as config_settings
        from autocsv_profiler.core.logger import logging_manager

        if config_settings.get("logging.file.enabled", False):
            config_settings.set("logging.file.log_dir", str(save_dir))
            # Reinitialize logging with output directory
            logging_manager._initialized = False
            logging_manager.initialize()

        # Detect file encoding first and display it
        print(f"\n{HEADER_GENERATING_REPORTS}")
        print(HEADER_SEPARATOR)

        # Show encoding detection before progress bar
        from charset_normalizer import from_bytes

        with open(file_path, FILE_MODE_READ_BINARY) as file_handle:
            raw_data = file_handle.read(
                ENCODING_DETECTION_SAMPLE_SIZE
            )  # Read first 10KB for detection
            result = from_bytes(raw_data).best()
            if result:
                encoding_result = {"encoding": result.encoding, "confidence": 0.9}
            else:
                encoding_result = {
                    "encoding": DEFAULT_ENCODING,
                    "confidence": FALLBACK_CONFIDENCE,
                }

        from rich.console import Console

        console = Console()
        console.print(PROG_ENCODING_DETECTION)
        console.print(
            f"[green]Encoding: {encoding_result['encoding']} (Confidence: {encoding_result['confidence']:.2%})[/green]"
        )
        console.print()

        # Temporarily suppress all logging during progress display

        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
            TimeElapsedColumn,
        )

        original_level = logging.getLogger().level
        autocsv_logger = logging.getLogger(LOGGER_AUTOCSV)
        original_autocsv_level = autocsv_logger.level

        logging.getLogger().setLevel(logging.CRITICAL)
        autocsv_logger.setLevel(logging.CRITICAL)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task(
                "Initializing analysis...", total=ANALYZER_PROGRESS_TOTAL
            )
            saved_files = []

            # Generate reports with progress updates and suppressed output
            with (
                contextlib.redirect_stdout(StringIO()),
                contextlib.redirect_stderr(StringIO()),
            ):
                progress.update(
                    task,
                    description="Generating complete dataset report...",
                )
                generate_complete_report(
                    data_copy, save_dir, file_path, delimiter=delimiter
                )
                saved_files.extend([OUTPUT_DATASET_ANALYSIS])
                progress.advance(task)

                progress.update(task, description="Computing statistical summaries...")
                data_table_range_min_max_distinct(
                    data_copy, save_dir, delimiter=delimiter
                )
                saved_files.extend(
                    [OUTPUT_NUMERICAL_SUMMARY, OUTPUT_CATEGORICAL_SUMMARY]
                )
                progress.advance(task)

                progress.update(task, description="Creating descriptive statistics...")
                researchpy_descriptive_stats(data_copy, save_dir, delimiter=delimiter)
                saved_files.extend([OUTPUT_NUMERICAL_STATS, OUTPUT_CATEGORICAL_STATS])
                progress.advance(task)

                progress.update(
                    task, description="Generating distinct values analysis..."
                )
                distinct_val_tabular_txt(
                    data_copy, os.path.join(save_dir, OUTPUT_DISTINCT_VALUES)
                )
                saved_files.extend([OUTPUT_DISTINCT_VALUES])
                progress.advance(task)

                progress.update(task, description="Analysis reports completed!")

        # Display saved files instead of generic message
        console.print(PROG_SAVED_FILES)
        for file_name in saved_files:
            console.print(f"[green]- {file_name}[/green]")
        if interactive:
            print("\n" + "[*] STARTING INTERACTIVE ANALYSIS PHASE")
            print(HEADER_SEPARATOR)

            print("\n[Phase 1] Column Exclusion Selection")
            data_copy = exclude_columns_improved(
                data_copy, save_dir, delimiter=delimiter
            )

            print("\n[Phase 2] TableOne Groupby Analysis")
            data_copy = TableOne_groupby_column_improved(data_copy, save_dir)

            print("\n[Phase 3] Visualization Selection")
            select_and_execute_visualizations_improved(data_copy, save_dir)

            logging.getLogger().setLevel(original_level)
            autocsv_logger.setLevel(original_autocsv_level)
        else:
            print("\n" + "[*] RUNNING NON-INTERACTIVE ANALYSIS")
            print(MSG_SKIP_INTERACTIVE)

            logging.getLogger().setLevel(original_level)
            autocsv_logger.setLevel(original_autocsv_level)

        # Final report generation summary with progress tracking
        print("\n[*] FINALIZING ANALYSIS REPORTS")
        print(HEADER_SEPARATOR)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task(
                "Scanning generated reports...", total=PROGRESS_SCAN_TOTAL
            )

            import glob

            all_files = []

            original_csv_name = os.path.basename(str(file_path))
            for ext in [SCAN_CSV_PATTERN, SCAN_TXT_PATTERN]:
                files = glob.glob(os.path.join(save_dir, ext))
                for file_path in files:
                    filename = os.path.basename(file_path)
                    if not (ext == SCAN_CSV_PATTERN and filename == original_csv_name):
                        all_files.append(filename)

            # Check visualization subdirectories for PNG files
            viz_dirs = [
                "kde_plots",
                "box_plots",
                "qq_plots",
                "bar_charts",
                "pie_charts",
            ]
            for viz_dir in viz_dirs:
                viz_path = os.path.join(save_dir, viz_dir, SCAN_PNG_PATTERN)
                files = glob.glob(viz_path)
                for file_path in files:
                    rel_path = os.path.relpath(file_path, save_dir)
                    all_files.append(rel_path)

            progress.update(
                task, advance=PROGRESS_SCAN_COMPLETE, description="Analysis complete!"
            )

        console.print(PROG_ALL_SAVED_FILES)
        if all_files:
            for file_name in sorted(all_files):
                console.print(f"[green]- {file_name}[/green]")
        else:
            console.print(MSG_NO_FILES_FOUND)

    except FileProcessingError as e:
        logging.error(f"Error during analysis: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except MemoryError as e:
        logging.error(f"Memory limit exceeded: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback

        error_msg = str(e)
        logging.error(f"An unexpected error occurred: {error_msg}")
        logging.error(traceback.format_exc())

        # Print detailed error information for debugging
        print(f"An unexpected error occurred: {error_msg}")
        print(f"Arguments received: {sys.argv}")
        print(MSG_TRACEBACK)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    memory_usage()

    args = [arg for arg in sys.argv[1:] if arg != "--non-interactive"]
    non_interactive = "--non-interactive" in sys.argv[1:]

    if len(args) not in CLI_VALID_ARGUMENT_COUNTS:
        print(MSG_USAGE)
        print(
            "   or: python analyzer.py <file_path> <delimiter> <save_dir> [--non-interactive]"
        )
        sys.exit(1)
    else:
        if len(args) == CLI_MIN_ARGS:
            file_path = args[0]
            save_dir = args[1]
            delimiter = None
        else:
            file_path = args[0]
            delimiter = args[1]
            save_dir = args[2]

        main(file_path, save_dir, delimiter, interactive=not non_interactive)

    memory_usage()


def run_analysis(
    file_path: PathLike,
    save_dir: Optional[PathLike] = None,
    delimiter: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    memory_limit_gb: int = DEFAULT_MEMORY_LIMIT_INT,
) -> str:
    """Run CSV analysis interactively.

    Args:
        file_path: Path to the CSV file to analyze
        save_dir: Directory to save results. If None, creates default directory.
        delimiter: CSV delimiter. If None, will try to detect.
        chunk_size: Chunk size for processing. Defaults to DEFAULT_CHUNK_SIZE.
        memory_limit_gb: Memory limit in GB. Defaults to 1.

    Returns:
        Path to the analysis results directory
    """
    if save_dir is None:
        base_name = os.path.splitext(os.path.basename(str(file_path)))[0]
        save_dir = f"{base_name}_analysis"

    main(file_path, save_dir, delimiter, chunk_size, memory_limit_gb)
    return str(save_dir)
