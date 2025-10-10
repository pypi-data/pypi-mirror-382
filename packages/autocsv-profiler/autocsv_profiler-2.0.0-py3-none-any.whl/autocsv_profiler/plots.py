import os
import pickle
import sys
import tempfile
from multiprocessing import Pool, cpu_count

# Configure matplotlib backend before importing pyplot
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from tabulate import tabulate

from .constants import (
    BAR_CHART_HEIGHT,
    BAR_CHART_WIDTH,
    CENTER_OFFSET_DIVISOR,
    DECIMAL_ROUND_PLACES,
    DEFAULT_ALPHA,
    DEFAULT_BINS,
    DEFAULT_DPI,
    DTYPE_CATEGORICAL_LIST,
    FILE_MODE_READ_BINARY,
    FLIER_SIZE,
    GRID_COLS_ADJUSTMENT,
    GRID_DIVISOR,
    HEADER_FONT_SIZE,
    HIGH_CARD_THRESH,
    INDEX_FORMAT_WIDTH,
    LABEL_FONT_SIZE,
    LEGEND_FONT_SIZE,
    LINE_WIDTH,
    MAX_SUBPLOTS_PER_FIGURE,
    MAX_WORKERS,
    MIN_WORKERS,
    MSG_NO_VIZ_SELECTED,
    MSG_VIZ_SELECTION,
    MSG_VIZ_SKIPPED,
    PERCENTAGE_MULTIPLIER,
    PIE_CHART_HEIGHT,
    PIE_CHART_WIDTH,
    PIE_LABEL_FONT_SIZE,
    PIE_OVERVIEW_HEIGHT,
    PIE_OVERVIEW_WIDTH,
    PKL_SUFFIX,
    PLOT_FILENAME_BAR_BATCH,
    PLOT_FILENAME_BOX_BATCH,
    PLOT_FILENAME_HIGH_CARD,
    PLOT_FILENAME_KDE_BATCH,
    PLOT_FILENAME_PIE_BATCH,
    PLOT_FILENAME_QQ_BATCH,
    PROG_VISUALIZATIONS,
    QUANTILE_25,
    QUANTILE_75,
    SCATTER_ALPHA,
    SCATTER_POINT_SIZE,
    SEPARATOR_LENGTH,
    SUBPLOT_HEIGHT,
    SUBPLOT_WIDTH,
    TITLE_FONT_SIZE,
    VALIDATION_MIN_COUNT,
    VISUALIZATION_DIRS,
    WORKER_CPU_FRACTION,
    XLABEL_FONT_SIZE,
    XTICKLABEL_FONT_SIZE,
    YLABEL_FONT_SIZE,
)
from .core.utils import cat_high_cardinality


def execute_visualization_worker(args):
    """
    Worker function for parallel visualization execution.

    Args:
        args: Tuple containing (viz_info, data_temp_file, save_dir, target)

    Returns:
        Tuple containing (success, viz_name, error_message)
    """
    viz_info, data_temp_file, save_dir, target = args

    try:
        with open(data_temp_file, FILE_MODE_READ_BINARY) as f:
            data_copy = pickle.load(f)

        matplotlib.use("Agg")

        viz_info["function"](data_copy, save_dir)

        return True, viz_info["name"], None

    except Exception as e:
        return False, viz_info["name"], str(e)


def plot_num_kde_subplot(
    data_copy, save_dir, layout_title="KDE Plots of Numerical Variables"
):
    """
    Generate and save KDE plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    plots_dir = os.path.join(save_dir, VISUALIZATION_DIRS[0])
    os.makedirs(plots_dir, exist_ok=True)

    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        return

    max_subplots_per_figure = MAX_SUBPLOTS_PER_FIGURE

    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i : i + max_subplots_per_figure]
        rows = (len(batch_cols) + GRID_COLS_ADJUSTMENT) // GRID_DIVISOR
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * SUBPLOT_WIDTH, rows * SUBPLOT_HEIGHT))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)
            sns.histplot(
                data_copy[col],
                bins=DEFAULT_BINS,
                kde=True,
                color="skyblue",
                edgecolor="black",
                alpha=DEFAULT_ALPHA,
            )

            stats = {
                "Mean": (data_copy[col].mean(), "darkred"),
                "Median": (data_copy[col].median(), "darkgreen"),
                "Mode": (
                    (
                        data_copy[col].mode()[0]
                        if not data_copy[col].mode().empty
                        else np.nan
                    ),
                    "darkblue",
                ),
                "Min": (data_copy[col].min(), "darkmagenta"),
                "25%": (data_copy[col].quantile(QUANTILE_25), "darkorange"),
                "75%": (data_copy[col].quantile(QUANTILE_75), "darkcyan"),
                "Max": (data_copy[col].max(), "darkviolet"),
            }

            for stat, (value, color) in stats.items():
                plt.axvline(
                    value,
                    color=color,
                    linestyle="--",
                    linewidth=LINE_WIDTH,
                    label=f"{stat}: {value:.2f}",
                )

            plt.title(f"Distribution and KDE of {col}", fontsize=TITLE_FONT_SIZE)
            plt.xlabel(col, fontsize=LABEL_FONT_SIZE)
            plt.ylabel("Density", fontsize=LABEL_FONT_SIZE)
            plt.legend(loc="upper right", fontsize=LEGEND_FONT_SIZE, frameon=False)
            plt.grid(False)

        plt.suptitle(
            f"{layout_title} (Batch {i // max_subplots_per_figure + 1})",
            fontsize=HEADER_FONT_SIZE,
            fontweight="bold",
        )
        plt.tight_layout(pad=3.0, rect=(0, 0, 1, 0.95))

        plot_filename = os.path.join(
            plots_dir,
            PLOT_FILENAME_KDE_BATCH.format(i // max_subplots_per_figure + 1),
        )
        plt.savefig(plot_filename, dpi=DEFAULT_DPI)
        plt.close()


def plot_num_box_plots_all(
    data_copy, save_dir, layout_title="Box Plots of Numerical Variables"
):
    """
    Generate and save box plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    plots_dir = os.path.join(save_dir, VISUALIZATION_DIRS[1])
    os.makedirs(plots_dir, exist_ok=True)

    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        return

    max_subplots_per_figure = MAX_SUBPLOTS_PER_FIGURE

    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i : i + max_subplots_per_figure]
        rows = (len(batch_cols) + GRID_COLS_ADJUSTMENT) // GRID_DIVISOR
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * SUBPLOT_WIDTH, rows * SUBPLOT_HEIGHT))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)
            sns.boxplot(
                x=data_copy[col],
                color="skyblue",
                fliersize=FLIER_SIZE,
                linewidth=LINE_WIDTH,
            )

            stats = {
                "Mean": (data_copy[col].mean(), "darkred"),
                "Median": (data_copy[col].median(), "darkgreen"),
                "Min": (data_copy[col].min(), "darkblue"),
                "25%": (data_copy[col].quantile(QUANTILE_25), "darkorange"),
                "75%": (data_copy[col].quantile(QUANTILE_75), "darkcyan"),
                "Max": (data_copy[col].max(), "darkviolet"),
            }

            for stat, (value, color) in stats.items():
                plt.axvline(
                    value,
                    color=color,
                    linestyle="--",
                    linewidth=LINE_WIDTH,
                    label=f"{stat}: {value:.2f}",
                )

            plt.title(f"Box Plot of {col}", fontsize=TITLE_FONT_SIZE)
            plt.xlabel(col, fontsize=LABEL_FONT_SIZE)
            plt.legend(loc="upper right", fontsize=LEGEND_FONT_SIZE, frameon=False)
            plt.grid(False)

        plt.suptitle(
            f"{layout_title} (Batch {i // max_subplots_per_figure + 1})",
            fontsize=HEADER_FONT_SIZE,
            fontweight="bold",
        )
        plt.tight_layout(pad=3.0, rect=(0, 0, 1, 0.95))

        plot_filename = os.path.join(
            plots_dir,
            PLOT_FILENAME_BOX_BATCH.format(i // max_subplots_per_figure + 1),
        )
        plt.savefig(plot_filename, dpi=DEFAULT_DPI)
        plt.close()


def plot_num_qq_subplot(
    data_copy, save_dir, layout_title="QQ Plots of Numerical Variables"
):
    """
    Generate and save QQ plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    plots_dir = os.path.join(save_dir, VISUALIZATION_DIRS[2])
    os.makedirs(plots_dir, exist_ok=True)

    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        return

    max_subplots_per_figure = MAX_SUBPLOTS_PER_FIGURE

    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i : i + max_subplots_per_figure]
        rows = (len(batch_cols) + GRID_COLS_ADJUSTMENT) // GRID_DIVISOR
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * SUBPLOT_WIDTH, rows * SUBPLOT_HEIGHT))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)

            (osm, osr), (slope, intercept, r) = stats.probplot(
                data_copy[col], dist="norm", plot=None
            )
            plt.scatter(
                osm, osr, s=SCATTER_POINT_SIZE, color="blue", alpha=SCATTER_ALPHA
            )
            plt.plot(osm, slope * osm + intercept, "r-", linewidth=LINE_WIDTH)

            plt.title(f"QQ Plot of {col}", fontsize=TITLE_FONT_SIZE)
            plt.xlabel("Theoretical Quantiles", fontsize=LABEL_FONT_SIZE)
            plt.ylabel(f"Quantiles of {col}", fontsize=LABEL_FONT_SIZE)
            plt.grid(False)

        plt.suptitle(
            f"{layout_title} (Batch {i // max_subplots_per_figure + 1})",
            fontsize=HEADER_FONT_SIZE,
            fontweight="bold",
        )
        plt.tight_layout(pad=3.0, rect=(0, 0, 1, 0.95))

        plot_filename = os.path.join(
            plots_dir, PLOT_FILENAME_QQ_BATCH.format(i // max_subplots_per_figure + 1)
        )
        plt.savefig(plot_filename, dpi=DEFAULT_DPI)
        plt.close()


def plot_categorical_summary(data, save_dir):
    """Generates and saves a summary of categorical variables, including bar charts.
    High cardinality columns get individual plots, low cardinality get subplots.

    Args:
        data (pd.DataFrame): The input DataFrame.
        save_dir (str): The directory to save the plots to.
    """
    categorical_cols = data.select_dtypes(
        include=DTYPE_CATEGORICAL_LIST
    ).columns.tolist()

    if not categorical_cols:
        return

    # Identify high cardinality columns
    high_cardinality_cols = cat_high_cardinality(data)
    # low_cardinality_cols = [
    #     col for col in categorical_cols if col not in high_cardinality_cols
    # ]

    # Create subplot arrangements for all columns (high and low cardinality)
    if categorical_cols:
        _plot_categorical_bar_charts_subplot(
            data, categorical_cols, high_cardinality_cols, save_dir
        )


def _plot_categorical_bar_charts_subplot(
    data,
    categorical_cols,
    high_cardinality_cols,
    save_dir,
    layout_title="Bar Charts of Categorical Variables",
):
    """
    Generate and save bar charts for categorical variables in batches of 12 subplots.
    High cardinality columns are limited to top N categories.

    Args:
        data (pd.DataFrame): The input DataFrame.
        categorical_cols (list): List of all categorical column names to plot.
        high_cardinality_cols (list): List of high cardinality column names.
        save_dir (str): The directory to save the plots to.
        layout_title (str): Title for the subplot layout.
    """
    plots_dir = os.path.join(save_dir, VISUALIZATION_DIRS[3])
    os.makedirs(plots_dir, exist_ok=True)

    if not categorical_cols:
        return

    max_subplots_per_figure = MAX_SUBPLOTS_PER_FIGURE
    for i in range(0, len(categorical_cols), max_subplots_per_figure):
        batch_cols = categorical_cols[i : i + max_subplots_per_figure]

        # Calculate subplot layout (similar to pie charts)
        rows = (len(batch_cols) + GRID_COLS_ADJUSTMENT) // GRID_DIVISOR
        cols = min(3, len(batch_cols))

        fig, axes = plt.subplots(
            rows, cols, figsize=(cols * BAR_CHART_WIDTH, rows * BAR_CHART_HEIGHT)
        )
        axes = axes.flatten()

        for j, col in enumerate(batch_cols):
            # Get value counts for the categorical variable
            counts = data[col].value_counts()

            # Apply different limits based on cardinality
            if col in high_cardinality_cols:
                # For high cardinality, limit to the high cardinality threshold
                from autocsv_profiler.config import settings

                threshold = settings.get(
                    "analysis.high_cardinality_threshold", HIGH_CARD_THRESH
                )
                if len(counts) > threshold:
                    counts = counts.head(threshold)
                    title_suffix = f" (Top {threshold} of {data[col].nunique()})"
                else:
                    title_suffix = ""
            else:
                # For low cardinality, keep all categories (they're already low)
                title_suffix = ""

            # Create bar chart
            bars = axes[j].bar(
                range(len(counts)),
                counts.values,
                color=matplotlib.cm.tab20c(np.linspace(0, 1, len(counts))),
            )

            # Customize the plot
            axes[j].set_title(
                f"Distribution of {col}{title_suffix}",
                fontsize=LABEL_FONT_SIZE,
                fontweight="bold",
            )
            axes[j].set_xlabel("Categories", fontsize=XLABEL_FONT_SIZE)
            axes[j].set_ylabel("Count", fontsize=YLABEL_FONT_SIZE)

            # Set category labels with rotation for better readability
            axes[j].set_xticks(range(len(counts)))
            axes[j].set_xticklabels(
                counts.index, rotation=45, ha="right", fontsize=XTICKLABEL_FONT_SIZE
            )

            # Add value labels on top of bars
            for bar, value in zip(bars, counts.values):
                axes[j].text(
                    bar.get_x() + bar.get_width() / CENTER_OFFSET_DIVISOR,
                    bar.get_height() + 0.01 * max(counts.values),
                    f"{value}",
                    ha="center",
                    va="bottom",
                    fontsize=PIE_LABEL_FONT_SIZE,
                )

        # Remove empty subplots
        for k in range(len(batch_cols), len(axes)):
            fig.delaxes(axes[k])

        # Add main title and adjust layout
        fig.suptitle(
            f"{layout_title} (Batch {i // max_subplots_per_figure + 1})",
            fontsize=HEADER_FONT_SIZE,
            fontweight="bold",
        )
        plt.tight_layout(pad=3.0, rect=(0, 0, 1, 0.95))

        # Save the plot
        plot_filename = os.path.join(
            plots_dir,
            PLOT_FILENAME_BAR_BATCH.format(i // max_subplots_per_figure + 1),
        )
        plt.savefig(plot_filename, dpi=DEFAULT_DPI, bbox_inches="tight")
        plt.close()


def _analyze_and_plot_categorical_variable(data, attribute, save_dir, all_summaries=[]):
    """Analyzes and plots a single categorical variable.

    Args:
        data (pd.DataFrame): The input DataFrame.
        attribute (str): The categorical variable to analyze.
        save_dir (str): The directory to save the plots to.
        all_summaries (list, optional): A list to append the summary to. Defaults to [].
    """
    os.makedirs(save_dir, exist_ok=True)

    counts = data[attribute].value_counts().to_frame()
    counts.columns = ["Count"]
    percentages = (
        counts["Count"] / counts["Count"].sum() * PERCENTAGE_MULTIPLIER
    ).round(DECIMAL_ROUND_PLACES)
    counts["Percentage"] = percentages

    final_table = counts.reset_index()
    final_table = final_table.rename(columns={"index": attribute.capitalize()})

    all_summaries.append(f"\n### {attribute.capitalize()} Summary ###\n")
    all_summaries.append(final_table.to_markdown(index=False, tablefmt="pipe"))

    plt.figure(figsize=(PIE_OVERVIEW_WIDTH, PIE_OVERVIEW_HEIGHT))
    sns.countplot(
        data=data, x=attribute, hue=attribute, palette="viridis", legend=False
    )
    plt.title(f"{attribute.capitalize()} Distribution")
    for p in plt.gca().patches:
        # Only process Rectangle patches (bars) which have these attributes
        if hasattr(p, "get_height") and hasattr(p, "get_x") and hasattr(p, "get_width"):
            height = p.get_height()
            if height > VALIDATION_MIN_COUNT:
                plt.annotate(
                    f"{int(height)}",
                    (p.get_x() + p.get_width() / CENTER_OFFSET_DIVISOR, height),
                    ha="center",
                    va="bottom",
                    fontsize=LEGEND_FONT_SIZE,
                    color="black",
                    xytext=(0, 5),
                    textcoords="offset points",
                )
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plot_path1 = os.path.join(save_dir, PLOT_FILENAME_HIGH_CARD.format(attribute))
    plt.savefig(plot_path1, dpi=DEFAULT_DPI)
    plt.close()


def plot_cat_pie_charts_subplot(
    data_copy, save_dir, layout_title="Pie Charts of Categorical Variables"
):
    """
    Generate and save pie charts for categorical variables.
    High cardinality columns get individual plots, low cardinality get subplots.
    """
    categorical_cols = data_copy.select_dtypes(
        include=DTYPE_CATEGORICAL_LIST
    ).columns.tolist()
    if not categorical_cols:
        return

    # Identify high cardinality columns
    high_cardinality_cols = cat_high_cardinality(data_copy)

    # Create subplot arrangements for all columns (high and low cardinality)
    if categorical_cols:
        _plot_pie_charts_subplot(
            data_copy,
            categorical_cols,
            high_cardinality_cols,
            save_dir,
            layout_title,
        )


def _plot_pie_charts_subplot(
    data_copy,
    categorical_cols,
    high_cardinality_cols,
    save_dir,
    layout_title="Pie Charts of Categorical Variables",
):
    """
    Generate and save pie charts for categorical variables in batches of 12 subplots.
    High cardinality columns are limited to top N categories.
    """
    plots_dir = os.path.join(save_dir, VISUALIZATION_DIRS[4])
    os.makedirs(plots_dir, exist_ok=True)

    if not categorical_cols:
        return

    max_subplots_per_figure = MAX_SUBPLOTS_PER_FIGURE

    for i in range(0, len(categorical_cols), max_subplots_per_figure):
        batch_cols = categorical_cols[i : i + max_subplots_per_figure]
        rows = (len(batch_cols) + GRID_COLS_ADJUSTMENT) // GRID_DIVISOR
        cols = min(3, len(batch_cols))

        fig, axes = plt.subplots(
            rows, cols, figsize=(cols * PIE_CHART_WIDTH, rows * PIE_CHART_HEIGHT)
        )
        axes = axes.flatten()

        for j, col in enumerate(batch_cols):
            series = data_copy[col].value_counts()

            # Apply different limits based on cardinality
            if col in high_cardinality_cols:
                # For high cardinality, limit to the high cardinality threshold
                from autocsv_profiler.config import settings

                threshold = settings.get(
                    "analysis.high_cardinality_threshold", HIGH_CARD_THRESH
                )
                if len(series) > threshold:
                    series = series.head(threshold)
                    title_suffix = f" (Top {threshold} of {data_copy[col].nunique()})"
                else:
                    title_suffix = ""
            else:
                # For low cardinality, keep all categories (they're already low)
                title_suffix = ""

            sizes = series.values / series.sum() * 100
            colors = matplotlib.cm.tab20c(np.linspace(0, 1, len(series)))
            wedges, _, autotexts = axes[j].pie(
                sizes, autopct="%1.1f%%", startangle=90, colors=colors
            )

            for text in autotexts:
                text.set_color("white")
                text.set_fontsize(LABEL_FONT_SIZE)

            axes[j].set_title(
                f"Distribution of {col}{title_suffix}", fontsize=TITLE_FONT_SIZE
            )
            legend_labels = [
                f"{label} ({size:.1f}%)" for label, size in zip(series.index, sizes)
            ]
            axes[j].legend(
                wedges,
                legend_labels,
                title=col,
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
            )

        for k in range(len(batch_cols), len(axes)):
            fig.delaxes(axes[k])

        fig.suptitle(
            f"{layout_title} (Batch {i // max_subplots_per_figure + 1})",
            fontsize=HEADER_FONT_SIZE,
            fontweight="bold",
        )
        plt.tight_layout(pad=3.0, rect=(0, 0, 1, 0.95))

        plot_filename = os.path.join(
            plots_dir,
            PLOT_FILENAME_PIE_BATCH.format(i // max_subplots_per_figure + 1),
        )
        plt.savefig(plot_filename, dpi=DEFAULT_DPI)
        plt.close()


def select_and_execute_visualizations(data_copy, save_dir):
    """
    Display visualization options in indexed format and execute selected ones
    """
    visualizations = [
        {
            "name": "KDE Plots (All Numerical)",
            "function": plot_num_kde_subplot,
            "description": "Kernel density estimation plots in batches",
        },
        {
            "name": "Box Plots (All Numerical)",
            "function": plot_num_box_plots_all,
            "description": "Box plots for all numerical variables",
        },
        {
            "name": "QQ Plots (All Numerical)",
            "function": plot_num_qq_subplot,
            "description": "Quantile-Quantile plots in batches",
        },
        {
            "name": "Categorical Summary (Bar charts)",
            "function": plot_categorical_summary,
            "description": "Individual analysis for each categorical variable",
        },
        {
            "name": "Pie Charts (All Categorical)",
            "function": plot_cat_pie_charts_subplot,
            "description": "Pie charts for all categorical variables",
        },
    ]

    def display_visualizations_indexed(viz_list):
        """Display visualizations in a categorized format for easy selection"""
        print("\n" + "=" * SEPARATOR_LENGTH)
        print(MSG_VIZ_SELECTION)
        print("=" * SEPARATOR_LENGTH)

        table_data = []
        for i, viz in enumerate(viz_list):
            viz["index"] = i
            item_text = f"{viz['index']:{INDEX_FORMAT_WIDTH}}: {viz['name']}\n    {viz['description']}"
            table_data.append([item_text])

        if table_data:
            print(
                tabulate(
                    table_data,
                    headers=["VISUALIZATIONS"],
                    tablefmt="pipe",
                    stralign="left",
                )
            )
        print(
            "Examples: 0,2,5 (specific) | 0-3 (range) | all (select all) | skip/enter (skip all)"
        )
        print("=" * SEPARATOR_LENGTH + "\n")

    display_visualizations_indexed(visualizations)

    selection = (
        input("  >>> Enter visualization indices, ranges, 'all', or skip/enter: ")
        .strip()
        .lower()
    )

    selected_visualizations = []

    if selection == "" or selection in ["skip", "none"]:
        print(MSG_VIZ_SKIPPED)
        return
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
            selected_visualizations = [visualizations[idx] for idx in sorted(indices)]

            if not selected_visualizations:
                print(MSG_NO_VIZ_SELECTED)
                return

            # Display selected visualizations for confirmation
            print(f"\nSelected {len(selected_visualizations)} visualizations:")
            for idx in sorted(indices):
                print(f"  {idx}: {visualizations[idx]['name']}")
            print()

        except (ValueError, IndexError):
            print(
                "Invalid input format. Please use numbers, ranges, 'all', or skip/enter."
            )
            return

    if selected_visualizations:
        from tqdm import tqdm

        print("\nGenerating visualizations...")

        num_workers = max(
            MIN_WORKERS, min(MAX_WORKERS, int(cpu_count() * WORKER_CPU_FRACTION))
        )

        try:
            print(f"Using {num_workers} parallel workers for faster processing...")

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=PKL_SUFFIX
            ) as temp_file:
                pickle.dump(data_copy, temp_file)
                data_temp_file = temp_file.name

            # Prepare arguments for workers
            worker_args = [
                (viz, data_temp_file, save_dir, None) for viz in selected_visualizations
            ]

            with Pool(processes=num_workers) as pool:
                results = []
                with tqdm(
                    total=len(selected_visualizations),
                    desc=PROG_VISUALIZATIONS,
                    unit="plot",
                    leave=True,
                    position=0,
                    dynamic_ncols=True,
                    ascii=True,
                    miniters=1,
                    file=sys.stdout,
                ) as pbar:

                    for result in pool.imap_unordered(
                        execute_visualization_worker, worker_args, chunksize=1
                    ):
                        results.append(result)
                        success, viz_name, error = result
                        if success:
                            pbar.set_description(
                                f"Processing Visualizations - Completed {viz_name}"
                            )
                        else:
                            print(f"\nError generating {viz_name}: {error}")
                            pbar.set_description(
                                f"Processing Visualizations - Error in {viz_name}"
                            )
                        pbar.update(1)

        except Exception as mp_error:
            print(
                f"Multiprocessing failed ({mp_error}), falling back to sequential processing..."
            )
            results = []

            # Sequential processing with progress bar
            with tqdm(
                selected_visualizations,
                desc=PROG_VISUALIZATIONS,
                unit="plot",
                leave=True,
                ascii=True,
                file=sys.stdout,
            ) as pbar:

                for viz in pbar:
                    pbar.set_description(f"Processing {viz['name']}")
                    try:
                        viz["function"](data_copy, save_dir)
                        results.append((True, viz["name"], None))
                        pbar.set_description(f"Completed {viz['name']}")
                    except Exception as e:
                        results.append((False, viz["name"], str(e)))
                        print(f"\nError generating {viz['name']}: {e}")
                        pbar.set_description(f"Error in {viz['name']}")

        # Clean up temporary file if it was created (only for multiprocessing)
        try:
            if "data_temp_file" in locals():
                os.unlink(data_temp_file)
        except Exception:
            pass
