import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from autocsv_profiler.config import settings
from autocsv_profiler.constants import (
    BYTES_PER_KB,
    DEFAULT_ENCODING,
    DTYPE_CATEGORICAL_LIST,
    DTYPE_NUMBER,
    ENCODING_DETECTION_SAMPLE_SIZE_LARGE,
    FILE_MODE_READ_BINARY,
    HIGH_CARD_THRESH,
    INDEX_FORMAT_WIDTH,
    MSG_COLUMN_EXCLUSION,
    MSG_COLUMN_HEADERS,
    MSG_EXCLUDED_SAVED,
    MSG_NO_COLUMNS_EXCLUDED,
    VALIDATION_ROW_DATA_EMPTY,
    VALIDATION_TABLE_COLUMNS_MIN,
)
from autocsv_profiler.core.logger import log_print
from autocsv_profiler.types import ColumnName, PathLike

if TYPE_CHECKING:
    from autocsv_profiler.types import DataFrameType
else:
    DataFrameType = pd.DataFrame

try:
    from charset_normalizer import from_bytes

    ENCODING_DETECTOR_AVAILABLE = True
except ImportError:
    ENCODING_DETECTOR_AVAILABLE = False


def memory_usage() -> None:
    """Display current memory usage of the process."""
    pass


def safe_float_conversion(value: any, default: float = 0.0) -> float:  # type: ignore[valid-type]
    """
    Safely convert value to float with fallback.

    Args:
        value: Value to convert to float
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError, AttributeError):
        return default


def safe_int_conversion(value: any, default: int = 0) -> int:  # type: ignore[valid-type]
    """
    Safely convert value to integer with fallback.

    Args:
        value: Value to convert to integer
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError, AttributeError):
        return default


def format_file_size(size_bytes: Union[int, float]) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == VALIDATION_ROW_DATA_EMPTY:
        return "0 B"

    size_units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size_bytes >= BYTES_PER_KB and unit_index < len(size_units) - 1:
        size_bytes /= float(BYTES_PER_KB)
        unit_index += 1

    return f"{size_bytes:.2f} {size_units[unit_index]}"


def validate_file_path(file_path: PathLike) -> bool:
    """
    Validate that a file path exists and is readable.

    Args:
        file_path: Path to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        path_obj = Path(file_path)
        return path_obj.exists() and path_obj.is_file()
    except (OSError, TypeError):
        return False


def clean_column_names(columns: List[any]) -> List[str]:  # type: ignore[valid-type]
    """
    Clean column names for better display.

    Args:
        columns: List of column names

    Returns:
        List of cleaned column names
    """
    if not columns:
        return []

    cleaned: List[str] = []
    for col in columns:
        if isinstance(col, str):
            # Remove leading/trailing whitespace and replace spaces with underscores
            clean_name = col.strip().replace(" ", "_").replace(".", "_")
            # Remove special characters except underscore
            clean_name = "".join(c for c in clean_name if c.isalnum() or c == "_")
            cleaned.append(clean_name if clean_name else f"col_{len(cleaned)}")
        else:
            cleaned.append(str(col))  # type: ignore[unreachable]

    return cleaned


def dataframe_memory_usage(df: "pd.DataFrame") -> float:
    """
    Calculate DataFrame memory usage in MB.

    Args:
        df: Pandas DataFrame to analyze

    Returns:
        Memory usage in megabytes
    """
    try:
        # Use explicit min_count=0 to avoid pandas compatibility issues
        mem_usage_bytes = df.memory_usage(deep=True).sum(min_count=0)  # type: ignore[no-any-return]
        return mem_usage_bytes / (BYTES_PER_KB**2)  # type: ignore[no-any-return]
    except TypeError:
        # Fallback for older pandas versions
        mem_usage_bytes = df.memory_usage(deep=True).sum()  # type: ignore[no-any-return]
        return mem_usage_bytes / (BYTES_PER_KB**2)  # type: ignore[no-any-return]


def cat_high_cardinality(
    data: "pd.DataFrame", threshold: Optional[int] = None
) -> List[ColumnName]:
    """
    Identify categorical columns with high cardinality.

    Args:
        data: Pandas DataFrame to analyze
        threshold: Minimum unique values to be considered high cardinality

    Returns:
        List of column names with high cardinality
    """
    if threshold is None:
        threshold = settings.get(
            "analysis.high_cardinality_threshold", HIGH_CARD_THRESH
        )

    high_cardinality_cols: List[ColumnName] = [
        col
        for col in data.select_dtypes(include=DTYPE_CATEGORICAL_LIST).columns
        if data[col].nunique() > threshold
    ]
    return high_cardinality_cols


def detect_mixed_data_types(
    data: "pd.DataFrame",
) -> Dict[ColumnName, List[str]]:
    """
    Detect columns with mixed data types.

    Args:
        data: Pandas DataFrame to analyze

    Returns:
        Dictionary mapping column names to lists of detected data types
    """
    mixed_columns: Dict[ColumnName, List[str]] = {}
    for col in data.columns:
        unique_types: Set[str] = {
            type(val).__name__ for val in data[col].dropna().values
        }
        if len(unique_types) > VALIDATION_TABLE_COLUMNS_MIN:
            mixed_columns[col] = sorted(unique_types)
    return mixed_columns


def detect_file_encoding(file_path: PathLike) -> Dict[str, Union[str, float]]:
    """
    Detect file encoding using charset-normalizer.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dictionary with encoding information including confidence score
    """
    if ENCODING_DETECTOR_AVAILABLE:
        try:
            with open(file_path, FILE_MODE_READ_BINARY) as f:
                raw_data: bytes = f.read(ENCODING_DETECTION_SAMPLE_SIZE_LARGE)
                result = from_bytes(raw_data).best()

            if result:
                return {
                    "encoding": result.encoding,
                    "confidence": 0.9,  # charset-normalizer is generally more reliable
                    "language": getattr(result, "language", "unknown"),
                }
            else:
                return {
                    "encoding": DEFAULT_ENCODING,
                    "confidence": 0.5,
                    "note": "fallback to utf-8",
                }

        except (UnicodeDecodeError, IOError, OSError) as e:
            return {"encoding": "unknown", "confidence": 0.0, "error": str(e)}
        except Exception as e:
            # Fallback for unexpected errors
            return {
                "encoding": "unknown",
                "confidence": 0.0,
                "error": f"Unexpected error: {str(e)}",
            }
    else:
        return {
            "encoding": DEFAULT_ENCODING,
            "confidence": 0.5,
            "note": "charset-normalizer not available, using utf-8",
        }


def exclude_columns(
    data_copy: "pd.DataFrame", save_dir: PathLike, delimiter: str = ","
) -> "pd.DataFrame":
    """
    Allows user to exclude specific columns from the dataset and saves the excluded data.

    Args:
        data_copy: Pandas DataFrame to modify
        save_dir: Directory to save excluded column data
        delimiter: CSV delimiter to use when saving excluded data (default: ',')

    Returns:
        Modified DataFrame with excluded columns removed
    """
    os.makedirs(save_dir, exist_ok=True)

    columns: List[ColumnName] = list(data_copy.columns)
    categorical_columns: List[ColumnName] = data_copy.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()
    numerical_columns: List[ColumnName] = data_copy.select_dtypes(
        include=[DTYPE_NUMBER]
    ).columns.tolist()

    # Analysis completed - files saved
    print("\n" + "=" * 60)
    print(MSG_COLUMN_EXCLUSION)
    print("=" * 60)
    print(MSG_COLUMN_HEADERS)
    print("-" * 60)

    # Create indexed lists maintaining original column indices for consistency
    cat_indexed: List[Tuple[int, ColumnName]] = [
        (i, col) for i, col in enumerate(columns) if col in categorical_columns
    ]
    num_indexed: List[Tuple[int, ColumnName]] = [
        (i, col) for i, col in enumerate(columns) if col in numerical_columns
    ]

    # Display columns with clear separation and original indices
    max_rows: int = max(len(cat_indexed), len(num_indexed))
    for i in range(max_rows):
        cat_part: str = (
            f"[{cat_indexed[i][0]:{INDEX_FORMAT_WIDTH}}] {cat_indexed[i][1]}"
            if i < len(cat_indexed)
            else ""
        )
        num_part: str = (
            f"[{num_indexed[i][0]:{INDEX_FORMAT_WIDTH}}] {num_indexed[i][1]}"
            if i < len(num_indexed)
            else ""
        )
        print(f"{cat_part:<35} | {num_part}")
    print(
        "Examples: 0,2,5 (exclude specific by original index) | skip/enter (exclude none)"
    )
    print("=" * 60)

    while True:
        try:
            user_input: str = input(
                "\n  >>> Enter column indices (comma-separated) or skip/enter: "
            ).strip()

            if user_input == "" or user_input.lower() in ["skip", "none"]:
                print(MSG_NO_COLUMNS_EXCLUDED)
                return data_copy
            else:
                indices: List[int] = [int(idx.strip()) for idx in user_input.split(",")]

                if all(0 <= idx < len(columns) for idx in indices):
                    break
                else:
                    print(
                        f"Invalid indices. Please enter numbers between 0 and {len(columns)-1}"
                    )
        except ValueError:
            print(
                "Invalid input. Please enter comma-separated numbers, 'all', 'skip', or just press Enter"
            )

    columns_to_exclude: List[ColumnName] = [columns[idx] for idx in indices]

    print(f"Columns to exclude: {columns_to_exclude}")

    data_modified: "pd.DataFrame" = data_copy.drop(columns=columns_to_exclude)

    excluded_data: "pd.DataFrame" = data_copy[columns_to_exclude]
    os.makedirs(save_dir, exist_ok=True)
    excluded_path: str = os.path.join(save_dir, "excluded_columns.csv")
    excluded_data.to_csv(excluded_path, index=False, sep=delimiter)

    log_print(MSG_EXCLUDED_SAVED)
    print(
        f"Modified dataset now has {len(data_modified.columns)} columns (originally {len(data_copy.columns)})"
    )
    print()  # Add blank line for better formatting

    return data_modified
