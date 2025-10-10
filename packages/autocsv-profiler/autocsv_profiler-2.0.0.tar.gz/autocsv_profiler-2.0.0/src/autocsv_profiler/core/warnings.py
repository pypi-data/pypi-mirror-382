"""
Warning management for AutoCSV Profiler
Handles warnings appropriately for single-environment operation
"""

import logging
import sys
import warnings
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional

from autocsv_profiler.core.logger import get_logger


class WarningsManager:
    """Manages warnings for AutoCSV Profiler"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.warning_config = self._load_warning_config()

    def _get_environment_name(self) -> str:
        """Get a simple environment identifier for logging purposes"""
        return "autocsv-profiler"

    def _load_warning_config(self) -> Dict[str, Any]:
        """Load unified warning configuration"""
        return {
            "capture_to_logging": True,
            "suppress_categories": [
                "pandas.errors.PerformanceWarning",
                "pandas.errors.DtypeWarning",
                "sklearn.utils._deprecation",
            ],
            "specific_filters": [
                {"message": ".*use_inf_as_na.*", "action": "ignore"},
                {
                    "message": ".*is_categorical_dtype is deprecated.*",
                    "action": "ignore",
                },
                {"message": ".*Passing a BlockManager.*", "action": "ignore"},
            ],
        }

    def setup_warnings(self) -> None:
        """Set up warning handling"""
        if self.warning_config["capture_to_logging"]:
            # Capture warnings to logging system
            logging.captureWarnings(True)

            # Set up custom warning handler
            warnings.showwarning = self._custom_warning_handler  # type: ignore[assignment]

        # Apply warning filters
        self._apply_warning_filters()

    def _custom_warning_handler(
        self,
        message: str,
        category: type,
        filename: str,
        lineno: int,
        file: Optional[Any] = None,
        line: Optional[str] = None,
    ) -> None:
        """Custom warning handler that logs warnings appropriately"""
        # Check if this warning should be suppressed
        message_str = str(message)

        # Suppress specific warning patterns
        suppress_patterns = [
            "Setting an item of incompatible dtype is deprecated",
            "isnull is deprecated",
            "vert: bool will be deprecated",
            "Passing.*palette.*without assigning.*hue.*is deprecated",
            "pkg_resources is deprecated",
            "pkg_resources.*declare_namespace",
            "Deprecated call to.*pkg_resources.declare_namespace",
            "frame.append method is deprecated",
            "Using categorical units to plot",
        ]

        for pattern in suppress_patterns:
            import re

            if re.search(pattern, message_str, re.IGNORECASE):
                return  # Don't log this warning

        # Suppress warnings from specific modules
        if any(module in filename for module in ["researchpy", "tableone"]):
            if category.__name__ in [
                "FutureWarning",
                "DeprecationWarning",
                "PendingDeprecationWarning",
            ]:
                return  # Don't log deprecated API warnings from third-party modules

        warning_msg = warnings.formatwarning(message, category, filename, lineno, line)

        # Determine log level based on warning category and environment
        log_level = self._get_warning_log_level(category, str(message))

        # Log the warning
        self.logger.log(
            log_level,
            f"Warning: {warning_msg.strip()}",
        )

        # Optionally also write to stderr for critical warnings
        if log_level >= logging.WARNING:
            sys.stderr.write(f"Warning: {message}\n")

    def _get_warning_log_level(self, category: type, message: str) -> int:
        """Determine appropriate log level for warning"""
        # Critical warnings that should always be visible
        critical_patterns = ["memory", "performance", "deprecated", "error"]

        message_lower = message.lower()
        if any(pattern in message_lower for pattern in critical_patterns):
            return logging.WARNING

        # Default log level for non-critical warnings
        return logging.INFO

    def _apply_warning_filters(self) -> None:
        """Apply warning filters"""
        # Reset warning filters first
        warnings.resetwarnings()

        # Apply specific filters
        for filter_config in self.warning_config.get("specific_filters", []):
            warnings.filterwarnings(
                action=filter_config["action"],
                message=filter_config["message"],
            )

        # Suppress specific categories
        for category in self.warning_config.get("suppress_categories", []):
            try:
                # Try to import and suppress the category
                parts = category.split(".")
                if len(parts) > 1:
                    warnings.filterwarnings("ignore", category=category)
                else:
                    warnings.filterwarnings("ignore", module=category)
            except Exception:
                # If can't suppress specifically, log it
                self.logger.debug(f"Could not suppress warning category: {category}")

    @contextmanager
    def capture_warnings(
        self,
        action: Literal[
            "default", "error", "ignore", "always", "module", "once"
        ] = "always",
    ) -> Any:
        """Context manager to capture warnings temporarily"""
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter(action)
            yield warning_list

    @contextmanager
    def suppress_warnings(self, categories: Optional[List[str]] = None) -> Any:
        """Context manager to temporarily suppress warnings"""
        with warnings.catch_warnings():
            if categories:
                for category in categories:
                    warnings.filterwarnings("ignore", module=category)
            else:
                warnings.simplefilter("ignore")
            yield

    def log_warning_summary(self, warning_list: List[warnings.WarningMessage]) -> None:
        """Log a summary of captured warnings"""
        if not warning_list:
            return

        warning_counts: Dict[str, int] = {}
        for warning in warning_list:
            category = warning.category.__name__
            warning_counts[category] = warning_counts.get(category, 0) + 1

        summary = f"Generated {len(warning_list)} warnings: "
        summary += ", ".join(
            f"{count} {category}" for category, count in warning_counts.items()
        )

        self.logger.info(summary)


# Global instance
warnings_manager = WarningsManager()


def setup_warnings() -> None:
    """Set up warning handling"""
    warnings_manager.setup_warnings()


def with_warning_suppression(
    categories: Optional[List[str]] = None,
) -> Callable:
    """Decorator to suppress warnings for a function"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with warnings_manager.suppress_warnings(categories):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def log_and_suppress_warnings(func: Callable) -> Callable:
    """Decorator to capture and log warnings from a function"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with warnings_manager.capture_warnings() as warning_list:
            result = func(*args, **kwargs)
            warnings_manager.log_warning_summary(warning_list)
            return result

    return wrapper


@contextmanager
def warning_context(action: str = "log") -> Any:
    """Context manager for warning handling"""
    if action == "suppress":
        with warnings_manager.suppress_warnings():
            yield
    elif action == "log":
        with warnings_manager.capture_warnings() as warning_list:
            yield warning_list
            warnings_manager.log_warning_summary(warning_list)
    else:
        yield


def auto_configure_warnings() -> None:
    """Automatically configure warnings"""
    setup_warnings()


auto_configure_warnings()
