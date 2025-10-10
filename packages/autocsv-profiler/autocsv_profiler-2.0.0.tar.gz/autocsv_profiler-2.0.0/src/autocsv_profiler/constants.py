"""
Constants module for AutoCSV Profiler.

This module contains all hardcoded values used throughout the package,
organized by category for better maintainability and consistency.
"""

# =====================================
# PERFORMANCE & MEMORY CONSTANTS
# =====================================

# Default processing parameters
DEFAULT_CHUNK_SIZE = 10000
DEFAULT_MEMORY_LIMIT_GB = 1.0
DEFAULT_MAX_FILE_SIZE_MB = 500
DELIMITER_TEST_SAMPLE_ROWS = 5
DELIMITER_VALIDATION_ROWS = 5
DELIMITER_DETECTION_SAMPLE_LINES = 20

# Memory conversion factors
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024  # 1024**2
BYTES_PER_GB = 1024 * 1024 * 1024  # 1024**3

# File size thresholds
ENCODING_SAMPLE_SIZE_BYTES = 8192
ENCODING_DETECTION_SAMPLE_SIZE = 10000  # 10KB
ENCODING_DETECTION_SAMPLE_SIZE_LARGE = 100000  # 100KB
ENCODING_LARGE_ALT = 16384  # 16KB for interactive mode

# Processing limits and validation
MAX_CHUNK_SIZE = 100000
MAX_MEMORY_LIMIT_GB = 32
MIN_CHUNK_SIZE = 1
MIN_MEMORY_LIMIT_GB = 0.1
FILE_SIZE_SMALL_MB = 50  # 50MB threshold for small files
FALLBACK_CONFIDENCE = 0.5
DECIMAL_PRECISION = 4

# =====================================
# UI & DISPLAY CONSTANTS
# =====================================

# Table formatting
DEFAULT_COLUMN_WIDTH = 35
MAX_SUBPLOTS_PER_FIGURE = 12
TABLE_SEPARATOR_LENGTH = 60
REPORT_SEPARATOR_LENGTH = 80

# Progress and visualization
DEFAULT_DPI = 300
MULTIPROCESSING_CPU_FRACTION = 0.75
MIN_WORKERS = 1
MAX_WORKERS = 4
PATH_TRUNCATION_LENGTH = 60

# Rich UI styling
UI_COLORS = {
    "primary": "cyan",
    "secondary": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "accent": "magenta",
    "dim": "dim white",
}

# Column styling for Rich tables
CATEGORICAL_COLUMN_STYLE = "cyan"
NUMERICAL_COLUMN_STYLE = "green"

# =====================================
# ANALYSIS & VALIDATION CONSTANTS
# =====================================

# Statistical thresholds
HIGH_CARD_THRESH = 20
CONF_THRESH = 0.7
DELIM_MIN_COLS = 2
DELIM_MAX_COLS = 50
IQR_MULTIPLIER = 1.5
DELIMITER_CONSISTENCY_THRESHOLD = 0.8
DELIMITER_COMMON_BONUS = 1.2
DELIMITER_MIN_SCORE = 2.0
DELIMITER_MAX_LENGTH = 3
MAX_DELIMITER_TEST_ROWS = 20
MIN_ROWS_FOR_VALIDATION = 2
CONSISTENCY_HIGH_THRESHOLD = 0.8
VALIDATION_NROWS = 2
PERCENTAGE_MULTIPLIER = 100
CENTER_OFFSET_DIVISOR = 2.0
DECIMAL_ROUND_PLACES = 2
QUANTILE_INDEX_75 = 2
QUANTILE_INDEX_25 = 0

# Quantile values for statistical analysis
QUANTILE_25 = 0.25
QUANTILE_50 = 0.50
QUANTILE_75 = 0.75
IQR_OUTLIER_MULTIPLIER = 1.5

# Display limits
MAX_DISTINCT = 20
MAX_DISPLAY_COLUMNS = 3
MAX_ROWS_PER_COLUMN = 20
TABULAR_MAX_COLUMNS = 3

# =====================================
# FILE & IO CONSTANTS
# =====================================

# Common delimiters for auto-detection
COMMON_DELIMITERS = [",", ";", "\t", "|", ":", " "]
TEST_DELIMITERS = [",", ";", "\t", "|"]  # Used in analyzer delimiter detection

# Fallback encoding chain
FALLBACK_ENCODINGS = ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252", "ascii"]

# Environment variables
ENV_VAR_PREFIX = "AUTOCSV_"
TF_LOG_LEVEL_ENV = "TF_CPP_MIN_LOG_LEVEL"
TF_LOG_LEVEL_VALUE = "3"
DEBUG_ENV_VAR = "DEBUG"
TESTING_ENV_VAR = "TESTING"

# File and path constants
DEFAULT_LOG_FILENAME = "autocsv_profiler.log"
TEMP_FILE_PREFIX = "autocsv_"

# File extensions and suffixes
CSV_EXTENSION = ".csv"
PKL_SUFFIX = ".pkl"
YAML_EXTENSION = ".yaml"
YML_EXTENSION = ".yml"
TXT_EXTENSION = ".txt"
PNG_EXTENSION = ".png"
LOG_EXTENSION = ".log"

# File operation modes
FILE_MODE_READ = "r"
FILE_MODE_WRITE = "w"
FILE_MODE_APPEND = "a"
FILE_MODE_READ_BINARY = "rb"
FILE_MODE_WRITE_BINARY = "wb"

# Default encoding
DEFAULT_ENCODING = "utf-8"
ENCODING_ERROR_HANDLING = "replace"

# File read sizes
TEST_READ_SIZE = 1024
SNIFFER_SAMPLE_SIZE = 1024

# Memory conversion factors for calculations
BYTES_TO_MB_DIVISOR = 1024 * 1024  # For direct division calculations

# =====================================
# DATA TYPE CONSTANTS
# =====================================

# Pandas data type classifications
NUMERICAL_DTYPES = [
    "int64",
    "float64",
    "int8",
    "int16",
    "int32",
    "float16",
    "float32",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
]

CATEGORICAL_DTYPES = ["object", "category"]

# Common data type groupings for select_dtypes
DTYPE_NUMBER = "number"
DTYPE_NUMERICAL_LIST = ["float64", "int64"]  # Common numerical types
DTYPE_ALL_NUMERICAL = [
    "int64",
    "float64",
    "int8",
    "int16",
    "int32",
    "float16",
    "float32",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
]
DTYPE_CATEGORICAL_LIST = ["object", "category"]

# NumPy data type references
NUMPY_NUMBER = "numpy.number"  # For np.number references

# =====================================
# PLOTTING CONSTANTS
# =====================================

# Figure dimensions and layout
SUBPLOT_WIDTH = 7
SUBPLOT_HEIGHT = 5
SUBPLOT_COLS = 3
FIGURE_PADDING = 3.0
TITLE_RECT = (0, 0, 1, 0.95)

# Plot styling parameters
DEFAULT_BINS = 20
DEFAULT_ALPHA = 0.7
LINE_WIDTH = 2
POINT_SIZE = 10
FLIER_SIZE = 5

# Font and text settings
TITLE_FONT_SIZE = 14
LABEL_FONT_SIZE = 12
TICK_FONT_SIZE = 10
LEGEND_FONT_SIZE = 10
HEADER_FONT_SIZE = 16
XLABEL_FONT_SIZE = 10
YLABEL_FONT_SIZE = 10
XTICKLABEL_FONT_SIZE = 9
PIE_LABEL_FONT_SIZE = 8

# Plot grid calculations
GRID_COLS_ADJUSTMENT = 2
GRID_DIVISOR = 3
BAR_CHART_WIDTH = 8
BAR_CHART_HEIGHT = 6
PIE_CHART_WIDTH = 7
PIE_CHART_HEIGHT = 5
PIE_OVERVIEW_WIDTH = 10
PIE_OVERVIEW_HEIGHT = 6

# Plot styling
SCATTER_POINT_SIZE = 10
SCATTER_ALPHA = 0.6

# Additional display constants
SEPARATOR_LENGTH = 60
REPORT_SEPARATOR_80 = 80
WORKER_CPU_FRACTION = 0.75
MIN_WORKERS = 1
MAX_WORKERS = 4
COLUMN_WIDTH_ADJUSTMENT = 4
INDEX_FORMAT_WIDTH = 2
PATH_LENGTH_THRESHOLD = 80
PATH_PARTS_KEEP = 2
UI_PADDING_HORIZONTAL = 2
UI_PADDING_VERTICAL = 1

# Plot colors and themes
PLOT_COLORS = {
    "complete_style": "green",
    "finished_style": "green",
    "histogram": "skyblue",
    "kde": "red",
    "boxplot": "lightblue",
}

# =====================================
# LOGGING CONSTANTS
# =====================================

# Log file settings
DEFAULT_LOG_MAX_BYTES = 10485760  # 10MB
DEFAULT_BACKUP_COUNT = 5

# Valid log levels
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Default log level
DEFAULT_LOG_LEVEL = "INFO"

# Individual log level constants
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"
LOG_LEVEL_SUCCESS = "SUCCESS"  # Custom level for UI

# Logger names
LOGGER_AUTOCSV = "autocsv"
LOGGER_ROOT = ""  # Root logger

# Log format patterns
LOG_FORMAT_TIMESTAMP = "timestamp"
LOG_FORMAT_LEVEL = "level"
LOG_FORMAT_LOGGER = "logger"
LOG_FORMAT_MESSAGE = "message"
LOG_FORMAT_MODULE = "module"
LOG_FORMAT_FUNCTION = "function"
LOG_FORMAT_LINE = "line"

# Default logging configuration values
DEFAULT_CONSOLE_LOG_LEVEL = "INFO"
DEFAULT_FILE_LOG_LEVEL = "DEBUG"

# =====================================
# VALIDATION CONSTANTS
# =====================================

# Delimiter validation
MAX_DELIMITER_LENGTH = 5
DANGEROUS_DELIMITER_CHARS = ["\n", "\r", "\x00"]

# Boolean conversion
BOOLEAN_TRUE_VALUES = ("true", "yes", "1", "on")
BOOLEAN_FALSE_VALUES = ("false", "no", "0", "off")

# Validation thresholds and limits
VALIDATION_MIN_COLUMNS = 1
VALIDATION_MAX_COLUMNS = 4  # For UI path truncation
VALIDATION_MIN_COUNT = 0
VALIDATION_MIN_FREQUENCY = 1  # For delimiter detection
VALIDATION_ERROR_MESSAGE_LENGTH = 60  # Max length before truncation
VALIDATION_PATH_LENGTH = 60  # Path truncation threshold
VALIDATION_PATH_PARTS_MIN = 4  # Minimum path parts for intelligent truncation

# Validation ranges
VALIDATION_CONFIDENCE_MIN = 0
VALIDATION_CONFIDENCE_MAX = 1
VALIDATION_POSITIVE_VALUE_MIN = 0  # For values that must be positive
VALIDATION_NON_NEGATIVE_MIN = 0  # For values that must be non-negative

# Column and data validation
VALIDATION_TABLE_COLUMNS_MIN = 1  # Minimum columns for valid table
VALIDATION_ROW_DATA_EMPTY = 0  # Empty row data check

# Validation error messages
VALIDATION_MSG_DELIMITER_EMPTY = "Delimiter cannot be empty"
VALIDATION_MSG_DELIMITER_STRING = "Delimiter must be a string"
VALIDATION_MSG_DELIMITER_TOO_LONG = "Delimiter is too long (max 5 characters)"
VALIDATION_MSG_DELIMITER_DANGEROUS = "Delimiter contains dangerous characters"
VALIDATION_MSG_CHUNK_SIZE_INTEGER = "Chunk size must be an integer"
VALIDATION_MSG_CHUNK_SIZE_POSITIVE = "Chunk size must be positive"
VALIDATION_MSG_CHUNK_SIZE_TOO_LARGE = "Chunk size too large (max 100,000 rows)"
VALIDATION_MSG_MEMORY_LIMIT_NUMBER = "Memory limit must be a number"
VALIDATION_MSG_MEMORY_LIMIT_POSITIVE = "Memory limit must be positive"
VALIDATION_MSG_MEMORY_LIMIT_TOO_LARGE = "Memory limit too large (max 32GB)"

# =====================================
# PROGRESS & TASK CONSTANTS
# =====================================

# Progress bar configuration
PROGRESS_UNIT_CHUNK = "chunk"
PROG_PROCESSING = "Processing Chunks"
PROG_INIT = "Initializing analysis..."
PROG_DATASET = "Generating complete dataset report..."
PROG_STATS = "Computing statistical summaries..."
PROG_DESC_STATS = "Creating descriptive statistics..."
PROG_DISTINCT = "Generating distinct values analysis..."
PROG_COMPLETE = "Analysis reports completed!"
PROG_SCAN = "Scanning generated reports..."
PROG_DONE = "Analysis complete!"

# Task tracking
DEFAULT_PROGRESS_TOTAL = 4
PROGRESS_TOTAL_SCANNING = 100

# =====================================
# CLI & COMMAND CONSTANTS
# =====================================

# CLI configuration
CLI_VALID_ARGUMENT_COUNTS = [2, 3]
CLI_MIN_ARGS = 2  # Minimum CLI arguments required
CLI_USAGE_MESSAGE = (
    "Usage: python analyzer.py <file_path> <save_dir> [--non-interactive]"
)
CLI_CHUNK_SIZE_HELP_DEFAULT = "10000"  # Default chunk size mentioned in help text
CLI_PROJECT_URL = "https://github.com/dhaneshbb/autocsv-profiler"
ANALYZER_PROGRESS_TOTAL = 4

# Analysis workflow messages
ANALYSIS_START_MESSAGE = "Starting analysis of: {}"
ANALYSIS_SUCCESS_MESSAGE = "Analysis completed successfully!"
ANALYSIS_RESULTS_MESSAGE = "Results saved to: {}"
ANALYSIS_CANCELLED_MESSAGE = "[INFO] Operation cancelled by user"
ANALYSIS_FAILED_MESSAGE = "Analysis failed or was cancelled"

# Progress descriptions
PROG_LOADING_DATA = "Loading data"
PROG_VISUALIZATIONS = "Processing Visualizations"
PROG_ENCODING_DETECTION = "[cyan]=== File Encoding Detection ===[/cyan]"
PROG_SAVED_FILES = "\n[bold green]Saved files:[/bold green]"
PROG_ALL_SAVED_FILES = "\n[bold green]All saved files:[/bold green]"

# Error and status messages
MSG_NO_FILES_FOUND = "[yellow]No additional files found[/yellow]"
MSG_ANALYSIS_CANCELLED = "\\n[yellow]Analysis cancelled by user.[/yellow]"
MSG_NO_FILE_PATH = "No file path entered"
MSG_FILE_SELECTION_CANCELLED = "File selection cancelled by user"
MSG_DELIMITER_DETECTION = "Attempting automatic delimiter detection..."
MSG_USING_MAIN_ENGINE = "Using main statistical analysis engine"
MSG_STATISTICAL_COMPLETE = "Statistical analysis completed successfully"
MSG_NO_DELIMITER = "Could not determine delimiter"
MSG_NO_CSV_SELECTED = "No CSV file selected"
MSG_NO_ENGINES_SELECTED = "No engines selected"

# Print messages for interactive components
MSG_VIZ_SELECTION = "Visualization Selection - Choose analysis plots"
MSG_VIZ_SKIPPED = "Visualization generation skipped."
MSG_NO_VIZ_SELECTED = "No valid visualizations selected."
MSG_SKIP_INTERACTIVE = "Skipping interactive phases, generating standard analysis only"
MSG_TRACEBACK = "Traceback:"
MSG_USAGE = "Usage: python analyzer.py <file_path> <save_dir> [--non-interactive]"
MSG_PACKAGE_INSTALL = "Please ensure the package is properly installed."
MSG_DEBUG_FLAG = "Run with --debug flag for detailed error information"

# Column and analysis messages
MSG_COLUMN_EXCLUSION = "Column Exclusion - Select columns to exclude"
MSG_COLUMN_HEADERS = "CATEGORICAL COLUMNS                 | NUMERICAL COLUMNS"
MSG_NO_COLUMNS_EXCLUDED = "No columns excluded."
MSG_EXCLUDED_SAVED = "Excluded columns data saved successfully"
MSG_TABLEONE_WARNING = (
    "WARNING: tableone library not available. Skipping TableOne analysis."
)
MSG_TABLEONE_ANALYSIS = "TableOne Analysis - Select variables to group by"
MSG_TABLEONE_EXAMPLES = (
    "Examples: 0,2,5 (specific columns) | skip/enter (skip analysis)"
)
MSG_TABLEONE_SKIPPED = "TableOne analysis skipped."
MSG_NO_VALID_COLUMNS = "No valid column indices selected. Skipping TableOne analysis."
MSG_REPORTS_SUCCESS = "SUCCESS: Reports generation completed."
MSG_NO_NUMERICAL_COLS = "No numerical columns found."

# Logger messages
LOG_NO_NUMERICAL_SUMMARY = "No numerical columns found for summary"
LOG_NO_CATEGORICAL_SUMMARY = "No categorical columns found for summary"

# =====================================
# OUTPUT & REPORT CONSTANTS
# =====================================

# Generated file names
OUTPUT_FILES = {
    "dataset_analysis": "dataset_analysis.txt",
    "numerical_summary": "numerical_summary.csv",
    "categorical_summary": "categorical_summary.csv",
    "numerical_stats": "numerical_stats.csv",
    "categorical_stats": "categorical_stats.csv",
    "distinct_values": "distinct_values.txt",
}

# Individual output file names for direct reference
OUTPUT_DATASET_ANALYSIS = "dataset_analysis.txt"
OUTPUT_NUMERICAL_SUMMARY = "numerical_summary.csv"
OUTPUT_CATEGORICAL_SUMMARY = "categorical_summary.csv"
OUTPUT_NUMERICAL_STATS = "numerical_stats.csv"
OUTPUT_CATEGORICAL_STATS = "categorical_stats.csv"
OUTPUT_DISTINCT_VALUES = "distinct_values.txt"

# Plot file naming patterns
PLOT_FILENAME_KDE_BATCH = "kde_plots_batch_{}.png"
PLOT_FILENAME_BOX_BATCH = "box_plots_batch_{}.png"
PLOT_FILENAME_QQ_BATCH = "qq_plots_batch_{}.png"
PLOT_FILENAME_BAR_BATCH = "bar_charts_batch_{}.png"
PLOT_FILENAME_PIE_BATCH = "pie_charts_batch_{}.png"
PLOT_FILENAME_HIGH_CARD = "high_cardinality_{}_distribution.png"

# TableOne file naming pattern
OUTPUT_TABLEONE_PATTERN = "tableone_summary_{}.csv"

# Report formatting constants
REPORT_COLUMN_WIDTH_ENGINE = 30  # Width for engine column in summary table
REPORT_COLUMN_WIDTH_STATUS = 12  # Width for status column in summary table
REPORT_COLUMN_WIDTH_CATEGORICAL = 35  # Width for categorical columns display
REPORT_COLUMN_WIDTH_NUMERICAL = 35  # Width for numerical columns display
REPORT_SAMPLE_ROWS = 3  # Number of sample rows to show in validation
REPORT_VALIDATION_NROWS = 10  # Number of rows for CSV validation
REPORT_VALIDATION_HEADER_NROWS = 1  # Number of header rows for validation

# Visualization directories
VISUALIZATION_DIRS = ["kde_plots", "box_plots", "qq_plots", "bar_charts", "pie_charts"]

# File extensions for scanning
SCAN_EXTENSIONS = ["*.csv", "*.txt", "*.png"]
SCAN_CSV_PATTERN = "*.csv"
SCAN_TXT_PATTERN = "*.txt"
SCAN_PNG_PATTERN = "*.png"

# Progress and scanning constants
PROGRESS_SCAN_TOTAL = 100  # Total for scanning reports progress
PROGRESS_SCAN_COMPLETE = 100  # Value when scanning is complete
DEFAULT_MEMORY_LIMIT_INT = 1  # Default memory limit as integer

# =====================================
# ERROR & WARNING CONSTANTS
# =====================================

# Error messages
ERROR_MEMORY_EXCEEDED = "Memory usage exceeded {}GB"
ERROR_CSV_READING_FAILED = "CSV reading failed with delimiter {}: {}"
ERROR_NO_COLUMNS_TO_PARSE = "No columns to parse from file"
ERROR_FILE_NOT_FOUND = "File not found: {}"
ERROR_PARSING_CSV = "Error parsing CSV file: {}"
ERROR_NO_DATA_CHUNKS = "No data chunks were loaded from the CSV file"

# Warning messages
WARNING_DELIMITER_DEFAULT = (
    "Warning: Could not detect delimiter, defaulting to comma (',')"
)

# Default delimiter fallback
DEFAULT_DELIMITER = ","

# =====================================
# MATPLOTLIB BACKEND CONSTANTS
# =====================================

# Backend configuration for non-interactive environments
MATLIB_BACKEND_ENV_VAR = "MPLBACKEND"
MATLIB_BACKEND_ALT_ENV_VAR = "MATPLOTLIB_BACKEND"
MATLIB_BACKEND_VALUE = "Agg"

# =====================================
# ANALYSIS PHASE CONSTANTS
# =====================================

# Interactive analysis phases
PHASE_DESCRIPTIONS = {
    "column_exclusion": "[Phase 1] Column Exclusion Selection",
    "tableone_analysis": "[Phase 2] TableOne Groupby Analysis",
    "visualization": "[Phase 3] Visualization Selection",
}

# Analysis section headers
ANALYSIS_SECTION_NUMERICAL = "=== Numerical Analysis ==="
ANALYSIS_SECTION_CATEGORICAL = "=== Categorical Analysis ==="

# Plot section titles
PLOT_TITLE_KDE = "KDE Plots (All Numerical)"
PLOT_TITLE_BOX = "Box Plots (All Numerical)"
PLOT_TITLE_QQ = "QQ Plots (All Numerical)"
PLOT_TITLE_BAR = "Categorical Summary (Bar charts)"
PLOT_TITLE_PIE = "Pie Charts (All Categorical)"

# Interactive prompts
PROMPT_COLUMN_SELECTION = "Examples: 0,2,5 (specific) | 0-3 (range) | all (select all) | skip/enter (skip all)"
PROMPT_SKIP_KEYWORDS = ["skip", "none"]
PROMPT_SKIP_MESSAGE = "No valid column indices selected. Skipping TableOne analysis."

# Analysis modes
ANALYSIS_MODE_INTERACTIVE = "INTERACTIVE ANALYSIS PHASE"
ANALYSIS_MODE_NON_INTERACTIVE = "NON-INTERACTIVE ANALYSIS"

# Analysis headers
HEADER_GENERATING_REPORTS = "[*] GENERATING ANALYSIS REPORTS"
HEADER_STARTING_INTERACTIVE = "[*] STARTING INTERACTIVE ANALYSIS PHASE"
HEADER_RUNNING_NON_INTERACTIVE = "[*] RUNNING NON-INTERACTIVE ANALYSIS"
HEADER_FINALIZING_REPORTS = "[*] FINALIZING ANALYSIS REPORTS"
HEADER_NON_INTERACTIVE_MESSAGE = (
    "Skipping interactive phases, generating standard analysis only"
)

# Header separator
HEADER_SEPARATOR = "=" * 60

# =====================================
# TYPE CHECKING CONSTANTS
# =====================================

# Type variable names (used in types.py)
TYPE_VAR_T = "T"
TYPE_VAR_K = "K"
TYPE_VAR_V = "V"
