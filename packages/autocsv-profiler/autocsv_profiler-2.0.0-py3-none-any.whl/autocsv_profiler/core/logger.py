"""Centralized logging system for AutoCSV Profiler."""

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Any, Dict, Optional

from autocsv_profiler.config.settings import settings
from autocsv_profiler.constants import (
    DEFAULT_BACKUP_COUNT,
    DEFAULT_CONSOLE_LOG_LEVEL,
    DEFAULT_ENCODING,
    DEFAULT_FILE_LOG_LEVEL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_MAX_BYTES,
    LOG_FORMAT_FUNCTION,
    LOG_FORMAT_LEVEL,
    LOG_FORMAT_LINE,
    LOG_FORMAT_LOGGER,
    LOG_FORMAT_MESSAGE,
    LOG_FORMAT_MODULE,
    LOG_FORMAT_TIMESTAMP,
    LOGGER_AUTOCSV,
)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""

    def format(self, record: logging.LogRecord) -> str:
        if settings.get("logging.app.structured_debug", False):
            log_data = {
                LOG_FORMAT_TIMESTAMP: self.formatTime(record),
                LOG_FORMAT_LEVEL: record.levelname,
                LOG_FORMAT_LOGGER: record.name,
                LOG_FORMAT_MESSAGE: record.getMessage(),
                LOG_FORMAT_MODULE: record.module,
                LOG_FORMAT_FUNCTION: record.funcName,
                LOG_FORMAT_LINE: record.lineno,
            }

            if hasattr(record, "extra_data"):
                log_data.update(getattr(record, "extra_data"))

            return json.dumps(log_data)
        else:
            return super().format(record)


class LoggingManager:
    """Centralized logging management system."""

    def __init__(self) -> None:
        self._loggers: Dict[str, logging.Logger] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the logging system based on configuration."""
        if self._initialized:
            return

        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        log_level_str = settings.get("logging.level", DEFAULT_LOG_LEVEL).upper()
        log_level = getattr(logging, log_level_str)
        root_logger.setLevel(log_level)

        if settings.get("logging.console.enabled", True):
            self._setup_console_logging()

        if settings.get("logging.file.enabled", True):
            self._setup_file_logging()

        self._initialized = True

    def _setup_console_logging(self) -> None:
        """Setup console logging handler."""
        console_handler = logging.StreamHandler()
        console_level = settings.get("logging.console.level", DEFAULT_CONSOLE_LOG_LEVEL)
        console_handler.setLevel(getattr(logging, console_level.upper()))

        console_format = settings.get(
            "logging.console.format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        console_formatter = StructuredFormatter(console_format)
        console_handler.setFormatter(console_formatter)

        logging.getLogger().addHandler(console_handler)

    def _setup_file_logging(self, log_dir: Optional[Path] = None) -> None:
        """Setup file logging with rotation."""
        if log_dir is None:
            # Use output directory from settings if available, otherwise current directory
            log_dir_str = settings.get("logging.file.log_dir", ".")
            log_dir = Path(log_dir_str)

        log_dir.mkdir(exist_ok=True)

        log_filename = settings.get("logging.file.filename", "autocsv_profiler.log")
        log_file = log_dir / log_filename

        max_bytes = settings.get("logging.file.max_bytes", DEFAULT_LOG_MAX_BYTES)
        backup_count = settings.get("logging.file.backup_count", DEFAULT_BACKUP_COUNT)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=DEFAULT_ENCODING,
        )

        file_level = settings.get("logging.file.level", DEFAULT_FILE_LOG_LEVEL)
        file_handler.setLevel(getattr(logging, file_level.upper()))

        file_format = settings.get(
            "logging.file.format",
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        )
        file_formatter = StructuredFormatter(file_format)
        file_handler.setFormatter(file_formatter)

        logging.getLogger().addHandler(file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the specified name."""
        if not self._initialized:
            self.initialize()

        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)

        return self._loggers[name]

    def log_user_interaction(
        self, message: str, extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user interaction events if enabled."""
        if settings.get("logging.app.user_interaction", True):
            logger = self.get_logger("user_interaction")
            if extra_data:
                logger.info(message, extra={"extra_data": extra_data})
            else:
                logger.info(message)

    def log_analysis_progress(
        self, message: str, extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log analysis progress events if enabled."""
        if settings.get("logging.app.analysis_progress", True):
            logger = self.get_logger("analysis_progress")
            if extra_data:
                logger.info(message, extra={"extra_data": extra_data})
            else:
                logger.info(message)

    def log_performance(self, message: str, metrics: Dict[str, Any]) -> None:
        """Log performance metrics if enabled."""
        if settings.get("logging.app.performance_metrics", False):
            logger = self.get_logger("performance")
            logger.info(message, extra={"extra_data": metrics})


# Global logging manager instance
logging_manager = LoggingManager()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return logging_manager.get_logger(name)


def log_print(
    message: str, level: str = DEFAULT_LOG_LEVEL, logger_name: str = LOGGER_AUTOCSV
) -> None:
    """Print message to console and log it."""
    print(message)
    logger = get_logger(logger_name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)


def log_user_input(prompt: str, user_input: str, context: str = "") -> None:
    """Log user input interactions."""
    logging_manager.log_user_interaction(
        f"User Input - {prompt}: {user_input}",
        {"prompt": prompt, "input": user_input, "context": context},
    )


def log_analysis_step(step: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log analysis step progress."""
    logging_manager.log_analysis_progress(f"Analysis Step: {step}", details)


def log_performance_metric(operation: str, **metrics: Any) -> None:
    """Log performance metrics."""
    logging_manager.log_performance(f"Performance - {operation}", metrics)


def log_structured(
    logger_name: str, level: str, message: str, **extra_fields: Any
) -> None:
    """Log with structured data."""
    logger = get_logger(logger_name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message, extra={"extra_data": extra_fields})


# Do not initialize logging on import - it will be initialized when needed
# This prevents creating log files in the wrong location
