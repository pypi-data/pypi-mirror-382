"""
Type definitions and aliases for the AutoCSV Profiler.

This module provides type aliases and custom types used throughout the package
for better type safety and code readability.
"""

from io import StringIO
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
)

# Import pandas types only for type checking to avoid runtime issues
if TYPE_CHECKING:
    import pandas as pd
else:
    # For runtime, create placeholder types
    class _DataFramePlaceholder:
        pass

    class _SeriesPlaceholder:
        pass

    pd = type(
        "Module",
        (),
        {"DataFrame": _DataFramePlaceholder, "Series": _SeriesPlaceholder},
    )

# Basic type aliases - use TypeAlias for clarity (Python 3.10+) or plain assignment for 3.8+
PathLike = Union[str, Path]
FilePathType = Union[str, Path]

# Use forward references for pandas types
if TYPE_CHECKING:
    DataFrameType = pd.DataFrame
    SeriesType = pd.Series
else:
    DataFrameType = "pd.DataFrame"
    SeriesType = "pd.Series"

# Configuration types
ConfigDict = Dict[str, Any]
ConfigSection = Dict[str, Union[str, int, float, bool, Dict[str, Any]]]
SettingsDict = Dict[str, ConfigSection]

# Analysis types
DelimiterType = str
EncodingType = str
ColumnName = str
ColumnIndex = int
ColumnSpec = Union[ColumnName, ColumnIndex]

# Statistical types
StatisticsDict = Dict[str, Union[int, float, str]]
SummaryStats = Dict[str, Any]
NumericValue = Union[int, float]
CategoricalValue = Union[str, int]

# Visualization types
PlotFunction = Callable[..., None]
ColorType = Union[str, Tuple[float, float, float], Tuple[float, float, float, float]]
FigureSize = Tuple[float, float]

# File and I/O types
BufferType = Union[StringIO, IO[str]]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Engine types
EngineType = Literal["auto", "main"]
ReportFormat = Literal["html", "json", "txt", "csv"]


# Version information
class VersionInfo(NamedTuple):
    """Version information structure."""

    major: int
    minor: int
    patch: int
    pre_release: str = ""
    build: str = ""


# Generic types
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# Protocol definitions for better type checking
@runtime_checkable
class Analyzable(Protocol):
    """Protocol for objects that can be analyzed."""

    def analyze(self) -> Dict[str, Any]:
        """Perform analysis and return results."""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Protocol for objects that can be configured."""

    def configure(self, config: ConfigDict) -> None:
        """Configure the object with given configuration."""
        ...


@runtime_checkable
class Reportable(Protocol):
    """Protocol for objects that can generate reports."""

    def generate_report(self, output_path: PathLike) -> str:
        """Generate a report and return the output path."""
        ...


# Complex type aliases
if TYPE_CHECKING:
    AnalysisResult = Dict[str, Union["pd.DataFrame", StatisticsDict, str, Path]]
    AnalysisFunction = Callable[["pd.DataFrame"], AnalysisResult]
    TransformFunction = Callable[["pd.DataFrame"], "pd.DataFrame"]
    ChunkProcessor = Callable[["pd.DataFrame"], "pd.DataFrame"]
    DataFilter = Callable[["pd.DataFrame"], "pd.DataFrame"]
    DataTransformer = Callable[["pd.DataFrame"], "pd.DataFrame"]
else:
    AnalysisResult = Dict[str, Union[Any, StatisticsDict, str, Path]]
    AnalysisFunction = Callable[[Any], Any]
    TransformFunction = Callable[[Any], Any]
    ChunkProcessor = Callable[[Any], Any]
    DataFilter = Callable[[Any], Any]
    DataTransformer = Callable[[Any], Any]

ProfilerConfig = Dict[str, Union[str, int, float, bool, List[str]]]
ValidationResult = Tuple[bool, Optional[str]]  # (is_valid, error_message)

# Function type aliases
ValidationFunction = Callable[[Any], ValidationResult]

# Logging types
LogFormatter = Callable[[str], str]
LogHandler = Callable[[str, LogLevel], None]

# CLI types
CommandFunction = Callable[[], int]
ArgumentParser = Any  # argparse.ArgumentParser type

# Memory and performance types
MemoryInfo = Dict[str, Union[int, float, str]]
PerformanceMetrics = Dict[str, Union[float, int]]

# Exception types
ErrorContext = Dict[str, Any]
ErrorHandler = Callable[[Exception, ErrorContext], None]
