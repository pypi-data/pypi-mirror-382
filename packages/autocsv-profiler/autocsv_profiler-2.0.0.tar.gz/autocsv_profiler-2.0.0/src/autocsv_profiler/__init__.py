"""AutoCSV Profiler - Automated CSV Data Analysis

A toolkit for automated CSV data analysis with statistical profiling,
visualization, and comprehensive reporting capabilities.

Copyright (c) 2025 dhaneshbb
Licensed under the MIT License
"""

from typing import Optional, Union

# Import package components
from .config import ConfigValidationError, Settings, settings
from .constants import DEFAULT_CHUNK_SIZE, DEFAULT_MEMORY_LIMIT_GB
from .core import (
    AutoCSVProfilerError,
    DelimiterDetectionError,
    FileProcessingError,
    ReportGenerationError,
    get_logger,
    log_print,
)

# Import version information
from .version import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __status__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

# Import main analysis components directly
try:
    from .analyzer import main as analyze_csv
    from .base import BaseProfiler as ProfilerBase
except ImportError as e:
    raise ImportError(f"Critical package components missing: {e}") from e

# Aliases for backward compatibility
auto_csv_main = analyze_csv
run_analysis = analyze_csv


# Package metadata

# Define public API
__all__ = [
    # Version information
    "__version__",
    "__version_info__",
    "__title__",
    "__description__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__url__",
    "__status__",
    # Main analysis functions
    "run_analysis",
    "auto_csv_main",
    "analyze_csv",
    # Base classes
    "ProfilerBase",
    # Configuration
    "Settings",
    "ConfigValidationError",
    "settings",
    # Core utilities and exceptions
    "AutoCSVProfilerError",
    "FileProcessingError",
    "DelimiterDetectionError",
    "ReportGenerationError",
    "get_logger",
    "log_print",
    # Convenience functions
    "analyze",
]


# Convenience function for quick access
def analyze(
    csv_file_path: str,
    output_dir: Optional[str] = None,
    delimiter: Optional[str] = None,
    interactive: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    memory_limit_gb: Union[int, float] = DEFAULT_MEMORY_LIMIT_GB,  # type: ignore[assignment]
) -> str:
    """Analyze a CSV file using the main statistical analysis engine.

    Args:
        csv_file_path: Path to the CSV file to analyze
        output_dir: Directory to save outputs (optional)
        delimiter: CSV delimiter (auto-detected if None)
        interactive: Enable interactive analysis mode
        chunk_size: Chunk size for processing large files
        memory_limit_gb: Memory limit in GB

    Returns:
        Path to the generated analysis output directory

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        AutoCSVProfilerError: If analysis fails
        ImportError: If main analysis engine is not available
    """
    from pathlib import Path

    csv_path = Path(csv_file_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    if output_dir is None:
        output_dir = str(csv_path.parent / csv_path.stem)  # type: ignore[assignment]

    output_path = Path(output_dir)  # type: ignore[arg-type]
    output_path.mkdir(exist_ok=True)

    analyze_csv(
        file_path=csv_path,
        save_dir=output_path,
        delimiter=delimiter,
        chunk_size=chunk_size,
        memory_limit_gb=memory_limit_gb,
        interactive=interactive,
    )

    return str(output_path)
