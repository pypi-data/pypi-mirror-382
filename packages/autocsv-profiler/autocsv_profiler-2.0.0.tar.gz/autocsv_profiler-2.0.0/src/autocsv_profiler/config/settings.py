import logging
import os
from typing import Any, List, Optional, Union, cast

from autocsv_profiler.constants import (
    CONF_THRESH,
    DEFAULT_BACKUP_COUNT,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_LOG_MAX_BYTES,
    DEFAULT_MEMORY_LIMIT_GB,
    HIGH_CARD_THRESH,
    VALID_LOG_LEVELS,
    VALIDATION_CONFIDENCE_MAX,
    VALIDATION_CONFIDENCE_MIN,
    VALIDATION_NON_NEGATIVE_MIN,
    VALIDATION_POSITIVE_VALUE_MIN,
)
from autocsv_profiler.types import ConfigDict, SettingsDict


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""


class Settings:
    _instance: Optional["Settings"] = None
    _settings: SettingsDict

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance - useful for testing."""
        cls._instance = None

    def _load_settings(self) -> None:
        """Load default configuration settings."""
        # Use default settings for single-environment setup
        self._settings = {
            "project": {
                "name": "AutoCSV Profiler",
                "version": "2.0.0",
                "description": "CSV data analysis toolkit with statistical profiling and visualization",
            },
            "performance": {
                "chunk_size": DEFAULT_CHUNK_SIZE,
                "memory_limit_gb": DEFAULT_MEMORY_LIMIT_GB,
            },
            "logging": {
                "level": "INFO",
                "console": {
                    "enabled": True,
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "file": {
                    "enabled": False,  # Disabled by default, enabled when output dir is set
                    "level": "DEBUG",
                    "filename": "autocsv_profiler.log",
                    "max_bytes": DEFAULT_LOG_MAX_BYTES,
                    "backup_count": DEFAULT_BACKUP_COUNT,
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "app": {"structured_debug": False},
            },
            "delimiter_detection": {"confidence_threshold": CONF_THRESH},
            "analysis": {"high_cardinality_threshold": HIGH_CARD_THRESH},
        }

        # Apply environment variable overrides
        self._apply_env_overrides()

        # Validate configuration
        self._validate_config()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # Environment variables should be in format: AUTOCSV_<SECTION>_<KEY>
        prefix: str = "AUTOCSV_"

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue

            # Convert env key to config path (remove AUTOCSV_ prefix)
            config_path = env_key[len(prefix) :].lower().replace("_", ".")

            # Try to convert value to appropriate type
            converted_value: Union[str, int, float, bool] = self._convert_env_value(
                env_value
            )

            # Set the value in config
            self._set_nested_value(self._settings, config_path, converted_value)

            logging.info(
                f"Applied environment override: {config_path} = {converted_value}"
            )

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Try boolean conversion first
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Try numeric conversion
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _set_nested_value(self, config: ConfigDict, path: str, value: Any) -> None:
        """Set a nested value in the configuration dictionary."""
        parts: List[str] = path.split(".")
        current: ConfigDict = config

        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = cast(ConfigDict, current[part])

        # Set the final value
        current[parts[-1]] = value

    def _validate_config(self) -> None:
        """Validate configuration values."""
        try:
            # Validate performance settings
            perf_config = self._settings.get("performance", {})
            if isinstance(perf_config, dict):
                chunk_size = perf_config.get("chunk_size", DEFAULT_CHUNK_SIZE)
                memory_limit = perf_config.get("memory_limit_gb", 1)

                if (
                    isinstance(chunk_size, (int, float))
                    and chunk_size <= VALIDATION_POSITIVE_VALUE_MIN
                ):
                    raise ConfigValidationError(
                        "performance.chunk_size must be positive"
                    )
                if (
                    isinstance(memory_limit, (int, float))
                    and memory_limit <= VALIDATION_POSITIVE_VALUE_MIN
                ):
                    raise ConfigValidationError(
                        "performance.memory_limit_gb must be positive"
                    )

            # Validate delimiter detection settings
            delim_config = self._settings.get("delimiter_detection", {})
            if isinstance(delim_config, dict):
                confidence = delim_config.get("confidence_threshold", CONF_THRESH)
                if isinstance(confidence, (int, float)) and not (
                    VALIDATION_CONFIDENCE_MIN <= confidence <= VALIDATION_CONFIDENCE_MAX
                ):
                    raise ConfigValidationError(
                        "delimiter_detection.confidence_threshold must be between 0 and 1"
                    )

            # Validate analysis settings
            analysis_config = self._settings.get("analysis", {})
            if isinstance(analysis_config, dict):
                threshold = analysis_config.get(
                    "high_cardinality_threshold", HIGH_CARD_THRESH
                )
                if (
                    isinstance(threshold, (int, float))
                    and threshold <= VALIDATION_POSITIVE_VALUE_MIN
                ):
                    raise ConfigValidationError(
                        "analysis.high_cardinality_threshold must be positive"
                    )

            # Validate logging settings
            log_config = self._settings.get("logging", {})
            if isinstance(log_config, dict):
                valid_levels = VALID_LOG_LEVELS

                level_value = log_config.get("level", "INFO")
                if (
                    isinstance(level_value, str)
                    and level_value.upper() not in valid_levels
                ):
                    raise ConfigValidationError(
                        f"logging.level must be one of: {valid_levels}"
                    )

                # Check file logging config
                file_config = log_config.get("file", {})
                if isinstance(file_config, dict):
                    max_bytes = file_config.get("max_bytes", DEFAULT_LOG_MAX_BYTES)
                    if (
                        isinstance(max_bytes, (int, float))
                        and max_bytes <= VALIDATION_POSITIVE_VALUE_MIN
                    ):
                        raise ConfigValidationError(
                            "logging.file.max_bytes must be positive"
                        )

                    backup_count = file_config.get("backup_count", DEFAULT_BACKUP_COUNT)
                    if (
                        isinstance(backup_count, (int, float))
                        and backup_count < VALIDATION_NON_NEGATIVE_MIN
                    ):
                        raise ConfigValidationError(
                            "logging.file.backup_count must be non-negative"
                        )

            logging.info("Configuration validation passed")

        except Exception as e:
            raise ConfigValidationError(f"Configuration validation failed: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting by its key. Supports dot notation for nested keys."""
        parts: List[str] = key.split(".")
        current: Any = self._settings
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value at runtime. Supports dot notation."""
        self._set_nested_value(self._settings, key, value)
        logging.info(f"Runtime configuration update: {key} = {value}")

    def reload(self) -> None:
        """Reload configuration from files and environment."""
        self._load_settings()
        logging.info("Configuration reloaded")

    def get_section(self, section: str) -> ConfigDict:
        """Get an entire configuration section."""
        result = self.get(section, {})
        if isinstance(result, dict):
            return cast(ConfigDict, result)
        return {}

    def __getattr__(self, name: str) -> Any:
        """Allows accessing settings as attributes (e.g., settings.project.name)."""
        value: Any = self.get(name)
        if value is None:
            raise AttributeError(f"Setting '{name}' not found.")
        return value

    def to_dict(self) -> SettingsDict:
        """Return the entire configuration as a dictionary."""
        return self._settings.copy()


# Global settings instance
settings = Settings()
