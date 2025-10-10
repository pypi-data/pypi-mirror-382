"""
Cross-environment input validation for AutoCSV Profiler
Provides validation that works across all conda environments
"""

import os
from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd
from charset_normalizer import from_bytes

from autocsv_profiler.config import settings
from autocsv_profiler.constants import (
    BYTES_TO_MB_DIVISOR,
    DANGEROUS_DELIMITER_CHARS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_MEMORY_LIMIT_GB,
    DELIM_MAX_COLS,
    DELIM_MIN_COLS,
    DELIMITER_DETECTION_SAMPLE_LINES,
    ENCODING_SAMPLE_SIZE_BYTES,
    FILE_MODE_READ,
    FILE_MODE_READ_BINARY,
    MAX_CHUNK_SIZE,
    MAX_DELIMITER_LENGTH,
    MAX_MEMORY_LIMIT_GB,
    MIN_ROWS_FOR_VALIDATION,
    REPORT_SAMPLE_ROWS,
    REPORT_VALIDATION_HEADER_NROWS,
    REPORT_VALIDATION_NROWS,
    TEST_READ_SIZE,
    VALIDATION_MIN_COLUMNS,
    VALIDATION_MSG_CHUNK_SIZE_INTEGER,
    VALIDATION_MSG_CHUNK_SIZE_POSITIVE,
    VALIDATION_MSG_CHUNK_SIZE_TOO_LARGE,
    VALIDATION_MSG_DELIMITER_DANGEROUS,
    VALIDATION_MSG_DELIMITER_EMPTY,
    VALIDATION_MSG_DELIMITER_STRING,
    VALIDATION_MSG_DELIMITER_TOO_LONG,
    VALIDATION_MSG_MEMORY_LIMIT_NUMBER,
    VALIDATION_MSG_MEMORY_LIMIT_POSITIVE,
    VALIDATION_MSG_MEMORY_LIMIT_TOO_LARGE,
    VALIDATION_NROWS,
    VALIDATION_POSITIVE_VALUE_MIN,
)
from autocsv_profiler.core.exceptions import (
    DelimiterDetectionError,
    FileProcessingError,
)
from autocsv_profiler.types import DelimiterType, PathLike


class CrossEnvironmentValidator:
    """Validator that works across all conda environments"""

    def __init__(self) -> None:
        self.max_file_size_mb = settings.get(
            "performance.max_file_size_mb", DEFAULT_MAX_FILE_SIZE_MB
        )
        self.sample_size = settings.get(
            "delimiter_detection.sample_lines", DELIMITER_DETECTION_SAMPLE_LINES
        )
        self.encoding_sample_size = settings.get(
            "performance.encoding_sample_size", ENCODING_SAMPLE_SIZE_BYTES
        )

    def validate_csv_file(self, file_path: PathLike) -> Dict[str, Any]:
        """
        Complete CSV file validation that works across environments

        Args:
            file_path: Path to CSV file

        Returns:
            Dict with validation results and metadata

        Raises:
            FileProcessingError: If file validation fails
        """
        file_path = Path(file_path)

        # Basic file validation
        self._validate_file_exists(file_path)
        self._validate_file_size(file_path)
        self._validate_file_permissions(file_path)

        # CSV structure validation
        encoding = self._detect_encoding(file_path)
        delimiter = self._detect_delimiter(file_path, encoding)
        structure_info = self._validate_csv_structure(file_path, delimiter, encoding)

        return {
            "file_path": str(file_path),
            "file_size_mb": file_path.stat().st_size / BYTES_TO_MB_DIVISOR,
            "encoding": encoding,
            "delimiter": delimiter,
            "num_columns": structure_info["num_columns"],
            "num_rows": structure_info["num_rows"],
            "column_names": structure_info["column_names"],
            "has_header": structure_info["has_header"],
            "validation_status": "valid",
        }

    def _validate_file_exists(self, file_path: Path) -> None:
        """Validate file exists and is accessible"""
        if not file_path.exists():
            raise FileProcessingError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise FileProcessingError(f"Path is not a file: {file_path}")

    def _validate_file_size(self, file_path: Path) -> None:
        """Validate file size is within limits"""
        size_mb = file_path.stat().st_size / BYTES_TO_MB_DIVISOR
        if size_mb > self.max_file_size_mb:
            raise FileProcessingError(
                f"File size ({size_mb:.1f}MB) exceeds maximum limit ({self.max_file_size_mb}MB)"
            )

    def _validate_file_permissions(self, file_path: Path) -> None:
        """Validate file has read permissions"""
        if not os.access(file_path, os.R_OK):
            raise FileProcessingError(f"No read permission for file: {file_path}")

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding with fallback chain"""
        try:
            with open(file_path, FILE_MODE_READ_BINARY) as f:
                sample = f.read(self.encoding_sample_size)

            result = from_bytes(sample).best()
            if result and result.encoding:
                return result.encoding

        except Exception:
            pass

        # Fallback chain
        fallback_encodings = settings.get(
            "encoding.fallback_encodings",
            ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252", "ascii"],
        )

        for encoding in fallback_encodings:
            try:
                with open(file_path, FILE_MODE_READ, encoding=encoding) as f:
                    f.read(TEST_READ_SIZE)  # Test read
                return str(encoding)
            except UnicodeDecodeError:
                continue

        raise FileProcessingError(f"Unable to detect encoding for file: {file_path}")

    def _detect_delimiter(self, file_path: Path, encoding: str) -> str:
        """Detect CSV delimiter with validation"""
        try:
            with open(file_path, FILE_MODE_READ, encoding=encoding) as f:
                sample_lines = [f.readline().strip() for _ in range(self.sample_size)]

            # Filter out empty lines
            sample_lines = [line for line in sample_lines if line]
            if not sample_lines:
                raise DelimiterDetectionError("CSV file appears to be empty")

            # Test common delimiters
            delimiters = settings.get(
                "delimiter_detection.common_delimiters",
                [",", ";", "\t", "|", ":", " "],
            )

            delimiter_scores = {}
            first_line = sample_lines[0]

            for delimiter in delimiters:
                if delimiter in first_line:
                    count = first_line.count(delimiter)

                    # Check consistency across lines
                    consistent = all(
                        line.count(delimiter) == count
                        for line in sample_lines[1 : min(5, len(sample_lines))]
                    )

                    if (
                        consistent and DELIM_MIN_COLS <= count + 1 <= DELIM_MAX_COLS
                    ):  # Reasonable column count
                        delimiter_scores[delimiter] = count + (10 if consistent else 0)

            if delimiter_scores:
                return str(
                    max(
                        delimiter_scores.keys(),
                        key=lambda k: delimiter_scores[k],
                    )
                )

            raise DelimiterDetectionError("No consistent delimiter pattern found")

        except Exception as e:
            raise DelimiterDetectionError(f"Delimiter detection failed: {e}")

    def _validate_csv_structure(
        self, file_path: Path, delimiter: str, encoding: str
    ) -> Dict[str, Any]:
        """Validate CSV structure and extract metadata"""
        try:
            # Read first few rows to validate structure
            df_sample = pd.read_csv(
                file_path,
                sep=delimiter,
                encoding=encoding,
                nrows=REPORT_VALIDATION_NROWS,
            )

            # Get full row count efficiently
            with open(file_path, FILE_MODE_READ, encoding=encoding) as f:
                row_count = sum(1 for _ in f) - 1  # Subtract header

            # Detect if header exists
            has_header = self._detect_header(file_path, delimiter, encoding)

            return {
                "num_columns": len(df_sample.columns),
                "num_rows": max(row_count, len(df_sample)),
                "column_names": list(df_sample.columns),
                "has_header": has_header,
                "sample_data": df_sample.head(REPORT_SAMPLE_ROWS).to_dict("records"),
            }

        except Exception as e:
            raise FileProcessingError(f"CSV structure validation failed: {e}")

    def _detect_header(self, file_path: Path, delimiter: str, encoding: str) -> bool:
        """Detect if CSV has header row"""
        try:
            # Read first two rows
            df_no_header = pd.read_csv(
                file_path,
                sep=delimiter,
                encoding=encoding,
                nrows=VALIDATION_NROWS,
                header=None,
            )
            # Read with header to detect if first row is header
            pd.read_csv(
                file_path,
                sep=delimiter,
                encoding=encoding,
                nrows=REPORT_VALIDATION_HEADER_NROWS,
            )

            if len(df_no_header) < MIN_ROWS_FOR_VALIDATION:
                return True  # Default assumption for single row

            # Check if first row has different data types than second row
            first_row = df_no_header.iloc[0]
            second_row = df_no_header.iloc[1]

            # If first row is all strings and second row has mixed types, likely header
            first_all_strings = all(isinstance(val, str) for val in first_row)
            second_mixed_types = not all(isinstance(val, str) for val in second_row)

            return first_all_strings and second_mixed_types

        except Exception:
            return True  # Default to assuming header exists


class ParameterValidator:
    """Validate parameters passed between environments"""

    @staticmethod
    def validate_delimiter(delimiter: DelimiterType) -> str:
        """Validate delimiter parameter"""
        if not delimiter:
            raise ValueError(VALIDATION_MSG_DELIMITER_EMPTY)

        if not isinstance(delimiter, str):
            raise ValueError(VALIDATION_MSG_DELIMITER_STRING)

        # Check if it's a reasonable delimiter
        if len(delimiter) > MAX_DELIMITER_LENGTH:
            raise ValueError(VALIDATION_MSG_DELIMITER_TOO_LONG)

        # Check for dangerous characters
        if any(char in delimiter for char in DANGEROUS_DELIMITER_CHARS):
            raise ValueError(VALIDATION_MSG_DELIMITER_DANGEROUS)

        return delimiter

    @staticmethod
    def validate_output_directory(output_dir: PathLike) -> Path:
        """Validate and prepare output directory"""
        output_path = Path(output_dir)

        # Create directory if it doesn't exist
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create output directory {output_path}: {e}")

        # Check write permissions
        if not os.access(output_path, os.W_OK):
            raise ValueError(f"No write permission for output directory: {output_path}")

        return output_path

    @staticmethod
    def validate_chunk_size(chunk_size: int) -> int:
        """Validate chunk size parameter"""
        if not isinstance(chunk_size, int):
            raise ValueError(VALIDATION_MSG_CHUNK_SIZE_INTEGER)

        if chunk_size < VALIDATION_MIN_COLUMNS:
            raise ValueError(VALIDATION_MSG_CHUNK_SIZE_POSITIVE)

        if chunk_size > MAX_CHUNK_SIZE:
            raise ValueError(VALIDATION_MSG_CHUNK_SIZE_TOO_LARGE)

        return chunk_size

    @staticmethod
    def validate_memory_limit(memory_limit_gb: Union[int, float]) -> float:
        """Validate memory limit parameter"""
        if not isinstance(memory_limit_gb, (int, float)):
            raise ValueError(VALIDATION_MSG_MEMORY_LIMIT_NUMBER)

        if memory_limit_gb <= VALIDATION_POSITIVE_VALUE_MIN:
            raise ValueError(VALIDATION_MSG_MEMORY_LIMIT_POSITIVE)

        if memory_limit_gb > MAX_MEMORY_LIMIT_GB:  # Reasonable upper limit
            raise ValueError(VALIDATION_MSG_MEMORY_LIMIT_TOO_LARGE)

        return float(memory_limit_gb)


# Convenience functions for easy import
def validate_csv_file(file_path: PathLike) -> Dict[str, Any]:
    """Validate CSV file - convenience function"""
    validator = CrossEnvironmentValidator()
    return validator.validate_csv_file(file_path)


def validate_parameters(
    file_path: PathLike,
    delimiter: DelimiterType,
    output_dir: PathLike,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    memory_limit_gb: float = DEFAULT_MEMORY_LIMIT_GB,
) -> Dict[str, Any]:
    """Validate all parameters for cross-environment processing"""
    csv_info = validate_csv_file(file_path)

    return {
        "csv_info": csv_info,
        "delimiter": ParameterValidator.validate_delimiter(delimiter),
        "output_dir": ParameterValidator.validate_output_directory(output_dir),
        "chunk_size": ParameterValidator.validate_chunk_size(chunk_size),
        "memory_limit_gb": ParameterValidator.validate_memory_limit(memory_limit_gb),
    }
