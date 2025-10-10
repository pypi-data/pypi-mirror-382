"""
Core functionality for AutoCSV Profiler

This package provides core utilities and classes including:
- Custom exceptions and error handling
- Data information and analysis utilities
- Memory usage and performance monitoring
- Logging management system
- File encoding detection
- Dataset information extraction
"""

# Import dataset information functions
from .dataset_info import (
    columns_info,
    data_table_range_min_max_distinct,
    format_dataset_info,
    generate_complete_report,
    get_dataset_info,
    missing_inf_values,
)

# Import exceptions
from .exceptions import (
    AutoCSVProfilerError,
    DelimiterDetectionError,
    FileProcessingError,
    ReportGenerationError,
)

# Import logging components
from .logger import (
    LoggingManager,
    StructuredFormatter,
    get_logger,
    log_analysis_step,
    log_performance_metric,
    log_print,
    log_structured,
    log_user_input,
)

# Import utility functions
from .utils import (
    cat_high_cardinality,
    dataframe_memory_usage,
    detect_file_encoding,
    detect_mixed_data_types,
    exclude_columns,
    memory_usage,
)

# Data info functionality moved to dataset_info module


__all__ = [
    # Exceptions
    "AutoCSVProfilerError",
    "FileProcessingError",
    "DelimiterDetectionError",
    "ReportGenerationError",
    # Logging
    "LoggingManager",
    "StructuredFormatter",
    "get_logger",
    "log_print",
    "log_user_input",
    "log_analysis_step",
    "log_performance_metric",
    "log_structured",
    # Utilities
    "memory_usage",
    "dataframe_memory_usage",
    "cat_high_cardinality",
    "detect_mixed_data_types",
    "detect_file_encoding",
    "exclude_columns",
    # Data info functionality available in dataset_info
    # Dataset info
    "get_dataset_info",
    "format_dataset_info",
    "data_table_range_min_max_distinct",
    "columns_info",
    "missing_inf_values",
    "generate_complete_report",
]
