"""Configuration module for AutoCSV Profiler

Contains all configuration-related components:
- Settings management and validation
- Visualization configuration
- Default configuration files
"""

# Import main configuration components
try:
    from .settings import ConfigValidationError, Settings, settings

    __all__ = ["Settings", "ConfigValidationError", "settings"]
except ImportError as e:
    raise ImportError(f"Configuration module unavailable: {e}") from e
