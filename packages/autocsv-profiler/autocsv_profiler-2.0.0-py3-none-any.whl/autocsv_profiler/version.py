"""Version management for AutoCSV Profiler"""

import sys

# Version information
__version__ = "2.0.0"
__version_info__ = (2, 0, 0)

# Package metadata
__title__ = "AutoCSV Profiler"
__description__ = (
    "CSV data analysis toolkit with statistical profiling and visualization"
)
__author__ = "dhaneshbb"
__author_email__ = "dhaneshbb5@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025 dhaneshbb"

# URLs
__url__ = "https://github.com/dhaneshbb/autocsv-profiler"

__status__ = "Beta"

# Define public API
__all__ = [
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
]


# Compatibility check
if sys.version_info[:2] < (3, 8):
    import warnings

    warnings.warn(
        f"AutoCSV Profiler {__version__} requires Python 3.8 "
        f"or higher. "
        f"You are using Python {sys.version}",
        UserWarning,
    )
