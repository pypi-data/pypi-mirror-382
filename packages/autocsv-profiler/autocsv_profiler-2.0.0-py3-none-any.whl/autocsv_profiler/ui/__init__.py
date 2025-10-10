"""User Interface module for AutoCSV Profiler

Contains user interface components:
- Clean interface for terminal display
- Interactive methods for user input
- Rich UI components for improved display
- Unified interface for complex layouts
"""

try:
    from .components import (
        TableOne_groupby_column_improved,
        exclude_columns_improved,
        select_and_execute_visualizations_improved,
    )
    from .interactive import CleanInteractiveMethods
    from .interface import CleanCSVInterface

    __all__ = [
        "exclude_columns_improved",
        "TableOne_groupby_column_improved",
        "select_and_execute_visualizations_improved",
        "CleanInteractiveMethods",
        "CleanCSVInterface",
    ]
except ImportError as e:
    raise ImportError(f"UI components unavailable: {e}") from e
