"""
Rich UI Components for Core Interactive Functions
Improved versions of the traditional console functions with Rich styling.
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..constants import (
    DTYPE_CATEGORICAL_LIST,
    DTYPE_NUMBER,
    FILE_MODE_WRITE_BINARY,
    INDEX_FORMAT_WIDTH,
    MSG_TABLEONE_WARNING,
    PKL_SUFFIX,
    REPORT_COLUMN_WIDTH_CATEGORICAL,
    REPORT_COLUMN_WIDTH_NUMERICAL,
    VALIDATION_MIN_COUNT,
    VALIDATION_ROW_DATA_EMPTY,
    VALIDATION_TABLE_COLUMNS_MIN,
)


# Lazy import for core logger
def _import_log_print():
    """Lazy import log_print only when needed."""
    try:
        from autocsv_profiler.core.logger import log_print

        return log_print
    except ImportError:
        return print  # Fallback to standard print


# Lazy imports - deferred until needed
def _import_pandas():
    """Lazy import pandas only when needed."""
    try:
        import pandas as pd

        return pd
    except ImportError:
        return None


def _import_numpy():
    """Lazy import numpy only when needed."""
    try:
        import numpy as np

        return np
    except ImportError:
        return None


def _import_types():
    """Lazy import types only when needed."""
    try:
        from autocsv_profiler.types import ColumnName, PathLike

        return ColumnName, PathLike
    except ImportError:
        return None, None


class RichInteractiveComponents:
    """Rich-improved interactive components for CSV analysis"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.theme = {
            "primary": "cyan",
            "secondary": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "blue",
            "accent": "magenta",
            "dim": "dim white",
        }

    def exclude_columns_rich(self, data_copy, save_dir, delimiter: str = ","):
        """
        Rich-improved column exclusion interface
        Replaces autocsv_profiler.core.utils.exclude_columns with Rich styling

        Args:
            data_copy: Pandas DataFrame to modify
            save_dir: Directory to save excluded column data
            delimiter: CSV delimiter to use when saving data (default: ',')

        Returns:
            Modified DataFrame with excluded columns removed
        """
        # Lazy import pandas and numpy only when this method is called
        pd = _import_pandas()
        np = _import_numpy()
        if pd is None or np is None:
            raise ImportError("pandas and numpy are required for this operation")

        os.makedirs(save_dir, exist_ok=True)

        columns = list(data_copy.columns)
        categorical_columns = data_copy.select_dtypes(
            include=DTYPE_CATEGORICAL_LIST
        ).columns.tolist()
        numerical_columns = data_copy.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        # Create Rich table for column display
        column_table = Table(
            title="Column Exclusion - Select columns to exclude",
            box=box.SIMPLE,
        )
        column_table.add_column(
            "CATEGORICAL COLUMNS", style="cyan", width=REPORT_COLUMN_WIDTH_CATEGORICAL
        )
        column_table.add_column(
            "NUMERICAL COLUMNS", style="green", width=REPORT_COLUMN_WIDTH_NUMERICAL
        )

        cat_indexed: List[Tuple[int, str]] = [
            (i, col) for i, col in enumerate(columns) if col in categorical_columns
        ]
        num_indexed: List[Tuple[int, str]] = [
            (i, col) for i, col in enumerate(columns) if col in numerical_columns
        ]

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
            column_table.add_row(cat_part, num_part)

        self.console.print(column_table)

        # Display examples
        examples = Panel(
            Text.assemble(
                ("Examples:\n", f"{self.theme['info']}"),
                ("• ", "white"),
                ("0,2,5", f"{self.theme['success']}"),
                (" - Exclude specific columns by original index\n", "white"),
                ("• ", "white"),
                ("skip", f"{self.theme['success']}"),
                (" or ", "white"),
                ("enter", f"{self.theme['success']}"),
                (" - Exclude no columns", "white"),
            ),
            title="Input Examples",
            border_style=self.theme["dim"],
        )
        self.console.print(examples)

        while True:
            try:
                # Use direct print and input for subprocess compatibility
                sys.stdout.write(
                    "Enter column indices (comma-separated) or skip/enter (): "
                )
                sys.stdout.flush()
                user_input: str = sys.stdin.readline().strip()

                if user_input == "" or user_input.lower() in ["skip", "none"]:
                    self.console.print(f"[{self.theme['info']}]No columns excluded.[/]")
                    return data_copy
                else:
                    indices: List[int] = [
                        int(idx.strip()) for idx in user_input.split(",")
                    ]

                    if all(0 <= idx < len(columns) for idx in indices):
                        break
                    else:
                        self.console.print(
                            f"[{self.theme['error']}]Invalid indices. "
                            f"Please enter numbers between 0 and {len(columns)-1}[/]"
                        )
            except ValueError:
                self.console.print(
                    f"[{self.theme['error']}]Invalid input. "
                    f"Please enter comma-separated numbers, 'skip', or just press Enter[/]"
                )

        columns_to_exclude: List[str] = [columns[idx] for idx in indices]

        self.console.print(
            f"[{self.theme['warning']}]Columns to exclude: " f"{columns_to_exclude}[/]"
        )

        data_modified = data_copy.drop(columns=columns_to_exclude)

        excluded_data = data_copy[columns_to_exclude]
        excluded_path: str = os.path.join(save_dir, "excluded_columns.csv")
        excluded_data.to_csv(excluded_path, index=False, sep=delimiter)

        # Save the modified dataset (with excluded columns removed) for other engines to use
        modified_csv_path: str = os.path.join(save_dir, "modified_dataset.csv")
        data_modified.to_csv(modified_csv_path, index=False, sep=delimiter)

        log_print_func = _import_log_print()
        log_print_func("Excluded columns data saved successfully")
        log_print_func(f"Modified dataset saved to: {modified_csv_path}")
        self.console.print(
            f"[{self.theme['success']}]Modified dataset now has "
            f"{len(data_modified.columns)} columns "
            f"(originally {len(data_copy.columns)})[/]"
        )

        return data_modified

    def tableone_column_selection_rich(self, data_copy) -> Dict[int, str]:
        """
        Rich-improved TableOne column selection
        Replaces display_columns_indexed from autocsv_profiler.analysis.statistical_analysis
        """
        all_columns: List[str] = data_copy.columns.tolist()
        categorical_columns: List[str] = data_copy.select_dtypes(
            include=DTYPE_CATEGORICAL_LIST
        ).columns.tolist()
        continuous_columns: List[str] = data_copy.select_dtypes(
            include=[DTYPE_NUMBER]
        ).columns.tolist()

        # Create Rich table for column display
        tableone_table = Table(
            title="TableOne Analysis - Select variables to group by",
            box=box.SIMPLE,
        )

        if categorical_columns:
            tableone_table.add_column("CATEGORICAL COLUMNS", style="cyan", width=35)
        if continuous_columns:
            tableone_table.add_column("NUMERICAL COLUMNS", style="green", width=35)

        categorical_with_idx: List[tuple] = []
        continuous_with_idx: List[tuple] = []
        index_to_column_map: Dict[int, str] = {}

        for i, col in enumerate(all_columns):
            index_to_column_map[i] = col

            if col in categorical_columns:
                categorical_with_idx.append((i, col))
            elif col in continuous_columns:
                continuous_with_idx.append((i, col))

        max_items = max(
            len(categorical_with_idx) if categorical_with_idx else 0,
            len(continuous_with_idx) if continuous_with_idx else 0,
        )

        for i in range(max_items):
            row_data = []

            if categorical_with_idx and i < len(categorical_with_idx):
                idx, col_name = categorical_with_idx[i]
                row_data.append(f"[{idx:{INDEX_FORMAT_WIDTH}}] {col_name}")
            elif len(tableone_table.columns) > VALIDATION_TABLE_COLUMNS_MIN:
                row_data.append("")

            if continuous_with_idx and i < len(continuous_with_idx):
                idx, col_name = continuous_with_idx[i]
                row_data.append(f"[{idx:{INDEX_FORMAT_WIDTH}}] {col_name}")
            elif len(row_data) == VALIDATION_ROW_DATA_EMPTY:
                row_data.append("")

            if (
                len(row_data) == 1
                and len(tableone_table.columns) > VALIDATION_TABLE_COLUMNS_MIN
            ):
                row_data.append("")

            tableone_table.add_row(*row_data)

        self.console.print(tableone_table)

        # Display examples
        examples = Panel(
            Text.assemble(
                ("Examples:\n", f"{self.theme['info']}"),
                ("• ", "white"),
                ("1,3", f"{self.theme['success']}"),
                (" - Group by columns 1 and 3\n", "white"),
                ("• ", "white"),
                ("skip", f"{self.theme['success']}"),
                (" or ", "white"),
                ("enter", f"{self.theme['success']}"),
                (" - Skip TableOne analysis", "white"),
            ),
            title="Input Examples",
            border_style=self.theme["dim"],
        )
        self.console.print(examples)

        return index_to_column_map

    def visualization_selection_rich(self) -> List[Dict[str, Any]]:
        """
        Rich-improved visualization selection
        Replaces display_visualizations_indexed from autocsv_profiler.visualization.plots
        """
        # Import actual visualization functions from the original module
        try:
            from autocsv_profiler.plots import (
                plot_cat_pie_charts_subplot,
                plot_categorical_summary,
                plot_num_box_plots_all,
                plot_num_kde_subplot,
                plot_num_qq_subplot,
            )

            # Use the actual function references from the original system
            visualizations = [
                {
                    "name": "KDE Plots (Numerical)",
                    "function": plot_num_kde_subplot,
                    "description": "Kernel density estimation plots in batches",
                },
                {
                    "name": "Box Plots (Numerical)",
                    "function": plot_num_box_plots_all,
                    "description": "Box plots for all numerical variables",
                },
                {
                    "name": "QQ Plots (Numerical)",
                    "function": plot_num_qq_subplot,
                    "description": "Quantile-Quantile plots in batches",
                },
                {
                    "name": "Bar Charts (Categorical)",
                    "function": plot_categorical_summary,
                    "description": "Individual analysis for categorical variables",
                },
                {
                    "name": "Pie Charts (Categorical)",
                    "function": plot_cat_pie_charts_subplot,
                    "description": "Pie charts for all categorical variables",
                },
            ]
        except ImportError as e:
            self.console.print(
                f"[{self.theme['warning']}]Warning: Could not import some visualization functions: {e}[/]"
            )
            # Fallback to the original visualization system

            self.console.print(
                f"[{self.theme['info']}]Using original visualization system...[/]"
            )
            return []  # Return empty list to trigger fallback

        # Create Rich table for visualization display
        viz_table = Table(
            title="Visualization Selection - Choose analysis plots",
            box=box.SIMPLE,
        )
        viz_table.add_column("ID", justify="right", style="cyan", width=4)
        viz_table.add_column("Visualization Name", style="cyan", width=29)
        viz_table.add_column("Description", style="green", width=50, no_wrap=True)

        for i, viz in enumerate(visualizations):
            viz["index"] = i
            viz_table.add_row(str(i), viz["name"], viz["description"])

        self.console.print(viz_table)

        # Display examples
        examples = Panel(
            Text.assemble(
                ("Examples:\n", f"{self.theme['info']}"),
                ("• ", "white"),
                ("0,2,5", f"{self.theme['success']}"),
                (" - Generate specific visualizations\n", "white"),
                ("• ", "white"),
                ("0-3", f"{self.theme['success']}"),
                (" - Generate range of visualizations\n", "white"),
                ("• ", "white"),
                ("all", f"{self.theme['success']}"),
                (" - Generate all visualizations\n", "white"),
                ("• ", "white"),
                ("skip", f"{self.theme['success']}"),
                (" or ", "white"),
                ("enter", f"{self.theme['success']}"),
                (" - Skip visualizations", "white"),
            ),
            title="Input Examples",
            border_style=self.theme["dim"],
        )
        self.console.print(examples)

        # Use direct print and input for subprocess compatibility
        sys.stdout.write(
            "Enter visualization indices, ranges, 'all', or skip/enter (): "
        )
        sys.stdout.flush()
        selection = sys.stdin.readline().strip().lower()

        selected_visualizations = []

        if selection == "" or selection in ["skip", "none"]:
            self.console.print(
                f"[{self.theme['info']}]Skipping visualizations as requested.[/]"
            )
            return []
        elif selection == "all":
            selected_visualizations = visualizations
        else:
            try:
                indices = []
                # Parse different input formats
                for part in selection.split(","):
                    part = part.strip()
                    if "-" in part and part.replace("-", "").replace(" ", "").isdigit():
                        # Handle range like "0-3"
                        start, end = map(int, part.split("-"))
                        indices.extend(range(start, end + 1))
                    elif part.isdigit():
                        # Handle single number
                        indices.append(int(part))

                # Remove duplicates and filter valid indices
                indices = list(
                    set([idx for idx in indices if 0 <= idx < len(visualizations)])
                )
                selected_visualizations = [
                    visualizations[idx] for idx in sorted(indices)
                ]

                if not selected_visualizations:
                    self.console.print(
                        f"[{self.theme['warning']}]No valid visualizations selected.[/]"
                    )
                    return []

                # Display selected visualizations for confirmation
                selected_names = [viz["name"] for viz in selected_visualizations]
                self.console.print(
                    f"[{self.theme['success']}]Selected {len(selected_visualizations)} "
                    f"visualizations: {', '.join(selected_names)}[/]"
                )

            except (ValueError, IndexError):
                self.console.print(
                    f"[{self.theme['error']}]Invalid input format. "
                    f"Please use numbers, ranges, 'all', or skip/enter.[/]"
                )
                return []

        return selected_visualizations


def exclude_columns_improved(
    data_copy,
    save_dir,
    console: Optional[Console] = None,
    delimiter: str = ",",
):
    """
    Improved version of exclude_columns function with Rich UI
    Drop-in replacement for autocsv_profiler.core.utils.exclude_columns

    Args:
        data_copy: Pandas DataFrame to modify
        save_dir: Directory to save excluded column data
        console: Rich console instance (optional)
        delimiter: CSV delimiter to use when saving data (default: ',')

    Returns:
        Modified DataFrame with excluded columns removed
    """
    rich_components = RichInteractiveComponents(console)
    return rich_components.exclude_columns_rich(data_copy, save_dir, delimiter)


def display_columns_indexed_improved(
    data_copy, console: Optional[Console] = None
) -> Dict[int, str]:
    """
    Improved version of display_columns_indexed function with Rich UI
    Drop-in replacement for autocsv_profiler.analysis.statistical_analysis.display_columns_indexed
    """
    rich_components = RichInteractiveComponents(console)
    return rich_components.tableone_column_selection_rich(data_copy)


def display_visualizations_indexed_improved(
    console: Optional[Console] = None,
) -> List[Dict[str, Any]]:
    """
    Improved version of display_visualizations_indexed function with Rich UI
    Drop-in replacement for autocsv_profiler.visualization.plots.display_visualizations_indexed
    """
    rich_components = RichInteractiveComponents(console)
    return rich_components.visualization_selection_rich()


def TableOne_groupby_column_improved(
    data_copy,
    save_dir,
    console: Optional[Console] = None,
):
    """
    Improved version of TableOne_groupby_column with Rich UI
    Drop-in replacement for autocsv_profiler.analysis.statistical_analysis.TableOne_groupby_column
    """
    rich_components = RichInteractiveComponents(console or Console())

    # Get column mapping using Rich UI
    index_to_column_map = rich_components.tableone_column_selection_rich(data_copy)

    # Get user selection with direct input for subprocess compatibility
    sys.stdout.write("Enter column indices (comma-separated) or skip/enter (): ")
    sys.stdout.flush()
    user_input = sys.stdin.readline().strip()

    if user_input == "" or user_input.lower() in ["skip", "none"]:
        rich_components.console.print(
            f"[{rich_components.theme['info']}]TableOne analysis skipped.[/]"
        )
        return data_copy

    try:
        indices = [int(idx.strip()) for idx in user_input.split(",")]

        # Validate indices
        invalid_indices = [idx for idx in indices if idx not in index_to_column_map]
        if invalid_indices:
            available_indices = list(index_to_column_map.keys())
            rich_components.console.print(
                f"[{rich_components.theme['error']}]Invalid column indices: "
                f"{invalid_indices}. Available indices: {available_indices}[/]"
            )
            return data_copy

        groupby_columns = [index_to_column_map[idx] for idx in indices]
        rich_components.console.print(
            f"[{rich_components.theme['info']}]Generating report for grouping by: {', '.join(groupby_columns)}[/]"
        )

        # Use the original TableOne functionality
        try:
            TableOne_groupby_column_original(data_copy, save_dir, groupby_columns)
            rich_components.console.print(
                f"[{rich_components.theme['success']}]TableOne analysis completed successfully[/]"
            )
        except Exception as tableone_error:
            rich_components.console.print(
                f"[{rich_components.theme['warning']}]TableOne analysis failed: {tableone_error}[/]"
            )
            rich_components.console.print(
                f"[{rich_components.theme['info']}]Continuing with remaining "
                f"analysis phases...[/]"
            )

    except ValueError as e:
        rich_components.console.print(
            f"[{rich_components.theme['error']}]Invalid input format: {e}. Please use comma-separated numbers or skip/enter.[/]"
        )
    except Exception as e:
        rich_components.console.print(
            f"[{rich_components.theme['error']}]Error during TableOne analysis: {e}[/]"
        )

    return data_copy


def TableOne_groupby_column_original(
    data_copy,
    save_dir,
    groupby_columns: List[str],
    delimiter: str = ",",
):
    """
    Original TableOne implementation - called by improved version
    Note: TableOne.to_csv() may not support custom delimiters, so this parameter is for consistency
    """
    import os

    try:
        from tableone import TableOne
    except ImportError:
        print(MSG_TABLEONE_WARNING)
        return

    os.makedirs(save_dir, exist_ok=True)

    # Create TableOne analysis - TableOne expects single column name, not list
    if len(groupby_columns) > VALIDATION_TABLE_COLUMNS_MIN:
        print(
            "WARNING: TableOne supports single groupby column only. Using first column."
        )

    groupby_column = groupby_columns[0]  # Use first column only
    # Create a copy of the DataFrame to prevent TableOne from modifying the original dtypes
    data_for_tableone = data_copy.copy()
    table1 = TableOne(data_for_tableone, groupby=groupby_column, pval=True)

    # Save results as CSV
    output_path = os.path.join(
        save_dir, f"tableone_groupby_{'_'.join(groupby_columns)}.csv"
    )
    table1.to_csv(output_path)

    print(
        f"SUCCESS: Summary table for grouping by '{', '.join(groupby_columns)}' saved successfully"
    )


def select_and_execute_visualizations_improved(
    data_copy,
    save_dir,
    console: Optional[Console] = None,
):
    """
    Improved version of select_and_execute_visualizations with Rich UI
    Drop-in replacement for autocsv_profiler.visualization.plots.select_and_execute_visualizations
    """
    rich_components = RichInteractiveComponents(console or Console())

    # Use Rich UI for selection
    selected_visualizations = rich_components.visualization_selection_rich()

    if not selected_visualizations:
        # Message already shown in visualization_selection_rich(), don't duplicate
        return

    # Execute the visualization logic with Rich feedback
    rich_components.console.print(
        f"[{rich_components.theme['info']}]Executing selected visualizations...[/]"
    )

    try:
        # Import the actual visualization execution functions
        import os
        import pickle
        import tempfile
        from multiprocessing import Pool, cpu_count

        from autocsv_profiler.plots import execute_visualization_worker

        # Create temporary file for data sharing (same as original)
        with tempfile.NamedTemporaryFile(
            mode=FILE_MODE_WRITE_BINARY, delete=False, suffix=PKL_SUFFIX
        ) as temp_file:
            pickle.dump(data_copy, temp_file)
            data_temp_file = temp_file.name

        os.makedirs(save_dir, exist_ok=True)

        # Determine number of workers
        num_workers = max(1, min(4, int(cpu_count() * 0.75)))
        rich_components.console.print(
            f"[{rich_components.theme['info']}]Using {num_workers} parallel workers for faster processing...[/]"
        )

        # Prepare arguments for parallel processing
        visualization_args = [
            (viz, data_temp_file, save_dir, None) for viz in selected_visualizations
        ]

        # Execute visualizations with progress tracking
        try:
            with Pool(processes=num_workers) as pool:

                # Create progress bar
                from rich.progress import (
                    BarColumn,
                    Progress,
                    SpinnerColumn,
                    TaskProgressColumn,
                    TextColumn,
                    TimeElapsedColumn,
                )

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(complete_style="green", finished_style="green"),
                    TaskProgressColumn(),
                    TimeElapsedColumn(),
                    console=rich_components.console,
                    transient=False,
                ) as progress:
                    task = progress.add_task(
                        "Processing visualizations...",
                        total=len(selected_visualizations),
                    )

                    results = []
                    for i, result in enumerate(
                        pool.imap(execute_visualization_worker, visualization_args)
                    ):
                        results.append(result)
                        success, viz_name, error = result

                        # Update progress with current visualization
                        if success:
                            progress.update(
                                task,
                                advance=1,
                                description=f"Completed: {viz_name}",
                            )
                        else:
                            progress.update(
                                task,
                                advance=1,
                                description=f"Failed: {viz_name}",
                            )

            # Clean up temporary file
            os.unlink(data_temp_file)

            # Report final results summary
            successful = sum(1 for success, _, _ in results if success)
            total = len(results)
            failed_count = total - successful

            rich_components.console.print()
            if successful == total:
                rich_components.console.print(
                    f"[{rich_components.theme['success']}]All {total} visualizations completed successfully![/]"
                )
            else:
                rich_components.console.print(
                    f"[{rich_components.theme['warning']}]{successful}/{total} visualizations completed successfully[/]"
                )
                if failed_count > VALIDATION_MIN_COUNT:
                    rich_components.console.print(
                        f"[{rich_components.theme['error']}]{failed_count} visualizations failed[/]"
                    )
                    # Show which ones failed
                    for success, viz_name, error in results:
                        if not success:
                            rich_components.console.print(
                                f"[{rich_components.theme['error']}]  - {viz_name}: {error}[/]"
                            )

        except Exception as e:
            # Clean up temporary file if it exists
            try:
                os.unlink(data_temp_file)
            except Exception:
                pass
            # Fallback to sequential processing
            rich_components.console.print(
                f"[{rich_components.theme['warning']}]Parallel processing failed, using sequential processing: {e}[/]"
            )

            # Sequential processing with progress bar
            from rich.progress import (
                BarColumn,
                Progress,
                SpinnerColumn,
                TaskProgressColumn,
                TextColumn,
                TimeElapsedColumn,
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(complete_style="green", finished_style="green"),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=rich_components.console,
                transient=False,
            ) as progress:
                task = progress.add_task(
                    "Processing visualizations...",
                    total=len(selected_visualizations),
                )

                results = []
                for i, viz in enumerate(selected_visualizations, 1):
                    try:
                        progress.update(task, description=f"Processing: {viz['name']}")
                        success, viz_name, error = execute_visualization_worker(
                            (viz, data_temp_file, save_dir, None)
                        )
                        results.append((success, viz_name, error))
                        if success:
                            progress.update(
                                task,
                                advance=1,
                                description=f"Completed: {viz_name}",
                            )
                        else:
                            progress.update(
                                task,
                                advance=1,
                                description=f"Failed: {viz_name}",
                            )

                    except Exception as viz_error:
                        results.append((False, viz["name"], str(viz_error)))
                        progress.update(
                            task,
                            advance=1,
                            description=f"Failed: {viz['name']}",
                        )

            # Clean up temporary file
            try:
                os.unlink(data_temp_file)
            except Exception:
                pass

            # Report final results summary for sequential processing
            successful = sum(1 for success, _, _ in results if success)
            total = len(results)
            failed_count = total - successful

            rich_components.console.print()
            if successful == total:
                rich_components.console.print(
                    f"[{rich_components.theme['success']}]All {total} visualizations completed successfully![/]"
                )
            else:
                rich_components.console.print(
                    f"[{rich_components.theme['warning']}]{successful}/{total} visualizations completed successfully[/]"
                )
                if failed_count > VALIDATION_MIN_COUNT:
                    rich_components.console.print(
                        f"[{rich_components.theme['error']}]{failed_count} visualizations failed[/]"
                    )
                    # Show which ones failed
                    for success, viz_name, error in results:
                        if not success:
                            rich_components.console.print(
                                f"[{rich_components.theme['error']}]  - {viz_name}: {error}[/]"
                            )

    except Exception as e:
        rich_components.console.print(
            f"[{rich_components.theme['error']}]Error during visualization setup: {e}[/]"
        )
        rich_components.console.print(
            f"[{rich_components.theme['info']}]Falling back to original visualization function...[/]"
        )

        # Ultimate fallback to original function
        from autocsv_profiler.plots import select_and_execute_visualizations

        select_and_execute_visualizations(data_copy, save_dir)
