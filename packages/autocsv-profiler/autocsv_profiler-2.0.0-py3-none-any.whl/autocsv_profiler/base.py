"""AutoCSV Profiler Base Classes

Base classes for all profiling engines in the AutoCSV Profiler.
Supports both package integration and standalone engine execution.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .constants import (
    BYTES_PER_GB,
    BYTES_PER_KB,
    BYTES_PER_MB,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MEMORY_LIMIT_GB,
    FILE_SIZE_SMALL_MB,
    PROG_LOADING_DATA,
)

# Optional imports
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class ProfilerError(Exception):
    """Base exception for profiler errors."""


class FileProcessingError(ProfilerError):
    """Exception raised for file processing errors."""


class ReportGenerationError(ProfilerError):
    """Exception raised for report generation errors."""


class BaseProfiler(ABC):
    """Base class for all CSV profiling engines.

    Provides common functionality for loading data, error handling,
    and report generation.
    """

    def __init__(
        self,
        csv_path: Union[str, Path],
        delimiter: str,
        output_dir: Union[str, Path],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        memory_limit_gb: float = DEFAULT_MEMORY_LIMIT_GB,
    ):
        """Initialize the profiler.

        Args:
            csv_path: Path to the CSV file to profile
            delimiter: CSV delimiter character
            output_dir: Directory to save reports
            chunk_size: Chunk size for processing large files
            memory_limit_gb: Memory limit in GB
        """
        self.csv_path = Path(csv_path)
        self.delimiter = delimiter
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.memory_limit_gb = memory_limit_gb

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load CSV data with chunking and memory management."""
        try:
            if not self.csv_path.exists():
                raise FileProcessingError(f"File not found: {self.csv_path}")

            file_size = self.csv_path.stat().st_size

            # For small files, load directly
            if file_size < FILE_SIZE_SMALL_MB * BYTES_PER_MB:  # Small file threshold
                return pd.read_csv(self.csv_path, sep=self.delimiter)

            # For larger files, use chunking
            chunks = []
            chunk_iterator = pd.read_csv(
                self.csv_path, sep=self.delimiter, chunksize=self.chunk_size
            )

            if HAS_TQDM:
                total_chunks = max(1, file_size // (self.chunk_size * BYTES_PER_KB))
                chunk_iterator = tqdm(
                    chunk_iterator,
                    total=total_chunks,
                    desc=PROG_LOADING_DATA,
                    unit="chunk",
                )

            for chunk in chunk_iterator:
                if HAS_PSUTIL:
                    memory_usage = psutil.Process().memory_info().rss / BYTES_PER_GB
                    if memory_usage > self.memory_limit_gb:
                        raise MemoryError(
                            f"Memory usage exceeded {self.memory_limit_gb}GB"
                        )

                chunks.append(chunk)

            return pd.concat(chunks, ignore_index=True)

        except FileNotFoundError:
            raise FileProcessingError(f"File not found: {self.csv_path}")
        except pd.errors.ParserError as e:
            raise FileProcessingError(f"Error parsing CSV file: {e}")
        except Exception as e:
            raise FileProcessingError(f"Unexpected error loading data: {e}")

    @abstractmethod
    def generate_report(self) -> str:
        """Generate the profiling report.

        Returns:
            Path to the generated report file
        """

    @abstractmethod
    def get_report_name(self) -> str:
        """Return the name/type of the report.

        Returns:
            Report name as string
        """

    def run(self) -> Optional[str]:
        """Execute the profiling and generate the report.

        Returns:
            Path to generated report, or None if failed
        """
        try:
            report_path = self.generate_report()
            print(
                f"SUCCESS: {self.get_report_name()} report saved to: " f"{report_path}"
            )
            return report_path

        except ReportGenerationError as e:
            print(f"Error generating {self.get_report_name()} report: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_data_summary(self) -> dict:
        """Get basic summary of the loaded data."""
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_usage_mb": (self.df.memory_usage(deep=True).sum() / BYTES_PER_MB),
            "column_names": list(self.df.columns),
            "dtypes": dict(self.df.dtypes.astype(str)),
        }
