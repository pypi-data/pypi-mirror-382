import logging
import math
import os
import sys
from io import StringIO

import numpy as np
import pandas as pd
from tabulate import tabulate

from ..constants import (
    DEFAULT_ENCODING,
    DTYPE_ALL_NUMERICAL,
    DTYPE_CATEGORICAL_LIST,
    DTYPE_NUMBER,
    DTYPE_NUMERICAL_LIST,
    FILE_MODE_WRITE,
    OUTPUT_CATEGORICAL_SUMMARY,
    OUTPUT_DATASET_ANALYSIS,
    OUTPUT_DISTINCT_VALUES,
    OUTPUT_NUMERICAL_SUMMARY,
    REPORT_SEPARATOR_80,
    SEPARATOR_LENGTH,
)
from ..summarize import cat_summary, num_summary
from .logger import log_print
from .utils import cat_high_cardinality, dataframe_memory_usage, detect_file_encoding

# Optional import for ResearchPy
try:
    import researchpy as rp
except ImportError:
    rp = None


def get_dataset_info(df):
    """Gathers complete information about the dataset.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary containing dataset information.
    """
    missing_count = df.isnull().sum().sum()
    missing_percentage = (missing_count / df.size) * 100
    duplicated_rows = df[df.duplicated(keep=False)]
    total_duplicates = duplicated_rows.shape[0]
    num_vars_count = df.select_dtypes(include=[DTYPE_NUMBER]).shape[1]
    cat_vars_count = df.select_dtypes(include=DTYPE_CATEGORICAL_LIST).shape[1]

    info = {
        "shape": df.shape,
        "memory_usage": df.memory_usage(deep=True).sum(),
        "missing_values": {
            "count": missing_count,
            "percentage": missing_percentage,
        },
        "duplicated_rows": {
            "count": total_duplicates,
            "rows": duplicated_rows,
        },
        "variable_types": {
            "numerical": num_vars_count,
            "categorical": cat_vars_count,
        },
        "data_types": df.dtypes.value_counts().to_dict(),
    }
    return info


def format_dataset_info(info):
    """Formats the dataset information for display.

    Args:
        info (dict): A dictionary containing dataset information.

    Returns:
        str: A formatted string containing the dataset information.
    """
    output_text = []
    output_text.append("\n=== Dataset Information ===\n")
    info_data = {
        "Info": [
            "Total Shape",
            "Memory Usage",
            "Total Duplicated Rows",
            "Missing Values Count",
            "Missing Values Percentage",
        ],
        "Details": [
            f"{info['shape'][0]} rows, {info['shape'][1]} columns",
            f"{info['memory_usage']} bytes",
            f"{info['duplicated_rows']['count']} duplicates",
            f"{info['missing_values']['count']} missing values",
            f"{info['missing_values']['percentage']:.2f}% missing values",
        ],
    }
    info_table = pd.DataFrame(info_data)
    info_table_md = info_table.to_markdown(index=False, tablefmt="github")
    output_text.append(info_table_md)

    output_text.append("\nData types with counts of columns:\n")
    data_types_count = pd.DataFrame(
        info["data_types"].items(), columns=["Data Type", "Count of Columns"]
    )
    data_types_md = data_types_count.to_markdown(index=False, tablefmt="github")
    output_text.append(data_types_md)

    output_text.append("\nNumerical and Categorical Variable Counts:\n")
    var_counts_data = {
        "Variable Type": ["Numerical Variables", "Categorical Variables"],
        "Count": [
            info["variable_types"]["numerical"],
            info["variable_types"]["categorical"],
        ],
    }
    var_counts_table = pd.DataFrame(var_counts_data)
    var_counts_md = var_counts_table.to_markdown(index=False, tablefmt="github")
    output_text.append(var_counts_md)

    if not info["duplicated_rows"]["rows"].empty:
        duplicated_md = info["duplicated_rows"]["rows"].to_markdown(
            index=True, tablefmt="github"
        )
        output_text.append("\nDetailed list of duplicated rows (including indices):\n")
        output_text.append(duplicated_md)
    else:
        output_text.append("\nNo duplicated rows found.\n")

    return "\n".join(output_text)


def data_table_range_min_max_distinct(data_copy, save_dir, delimiter=","):
    """
    Prints a concise table with data type, range, distinct count, and index,
    organized by data type.
    Saves the results directly in save_dir.
    """
    result_lines = []
    result_lines.append("\n== Column Summary: ==\n")
    header = (
        f"{'Index'.ljust(5)} {'Attribute'.ljust(30)} "
        f"{'Data Type'.ljust(15)} {'Range'.ljust(30)} {'Distinct Count'}"
    )
    separator = (
        f"{''.ljust(5)} {''.ljust(30)} {''.ljust(15)} " f"{''.ljust(30)} {''.ljust(15)}"
    )
    result_lines.append(header)
    result_lines.append(separator)

    index = 1
    for dtype in data_copy.dtypes.unique():
        dtype_columns = data_copy.select_dtypes(include=[dtype]).columns
        for col in dtype_columns:
            col_type = str(data_copy[col].dtype)
            distinct_count = data_copy[col].nunique()
            range_display = (
                f"{data_copy[col].min()} - {data_copy[col].max()}"
                if col_type in DTYPE_NUMERICAL_LIST
                else "N/A"
            )
            result_lines.append(
                f"{str(index).ljust(5)} {col.ljust(30)} {col_type.ljust(15)} "
                f"{range_display.ljust(30)} {distinct_count}"
            )
            index += 1


def columns_info(title, data):
    # Log to file only - no console output
    print(f"\n======== {title}: ===========\n")
    print(
        f"{'Index':<5} {'Col Index':<10} {'Attribute':<30} {'Data Type':<15} {'Range':<30} {'Distinct Count'}"
    )
    print(f"{'-'*5} {'-'*10} {'-'*30} {'-'*15} {'-'*30} {'-'*15}")
    sorted_cols = sorted(data.columns, key=lambda col: str(data[col].dtype))
    for i, col in enumerate(sorted_cols, 1):
        col_index = data.columns.get_loc(col)
        dtype, distinct = str(data[col].dtype), data[col].nunique()
        rng = (
            f"{data[col].min()} - {data[col].max()}"
            if dtype in DTYPE_ALL_NUMERICAL
            else "N/A"
        )
        print(f"{i:<5} {col_index:<10} {col:<30} {dtype:<15} {rng:<30} {distinct}")


def missing_inf_values(df, missing=False, inf=False, df_table=False):
    total_entries = df.shape[0]

    if not missing and not inf:
        missing = inf = True

    results = []

    if missing:
        missing_summary = pd.DataFrame(
            {
                "Data Type": df.dtypes,
                "Missing Count": df.isna().sum(),
                "Missing Percentage": (df.isna().sum() / total_entries) * 100,
            }
        ).sort_values(by="Missing Percentage", ascending=False)
        missing_summary = missing_summary[missing_summary["Missing Count"] > 0]

        if df_table:
            results.append(missing_summary)
        else:
            logging.info("Missing Values Summary:")
            logging.info(
                missing_summary
                if not missing_summary.empty
                else "No missing values found."
            )

    if inf:
        infinite_summary = pd.DataFrame(
            {
                "Data Type": df.dtypes,
                "Positive Infinite Count": (df == np.inf).sum(),
                "Positive Infinite Percentage": ((df == np.inf).sum() / total_entries)
                * 100,
                "Negative Infinite Count": (df == -np.inf).sum(),
                "Negative Infinite Percentage": ((df == -np.inf).sum() / total_entries)
                * 100,
            }
        ).sort_values(by="Positive Infinite Percentage", ascending=False)
        infinite_summary = infinite_summary[
            (infinite_summary["Positive Infinite Count"] > 0)
            | (infinite_summary["Negative Infinite Count"] > 0)
        ]

        if df_table:
            results.append(infinite_summary)
        else:
            logging.info("\nInfinite Values Summary:")
            logging.info(
                infinite_summary
                if not infinite_summary.empty
                else "No infinite values found."
            )

    if df_table:
        return pd.concat(results) if results else None


def generate_complete_report(df, save_dir, file_path, delimiter=","):
    """Generates a complete dataset analysis report.

    Args:
        df (pd.DataFrame): The input DataFrame.
        save_dir (str): The directory to save the report to.
        file_path (str): Path to the original CSV file.
        delimiter (str): CSV delimiter to use when saving results (default: ',').
    """
    os.makedirs(save_dir, exist_ok=True)

    complete_output = []

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("COMPLETE DATASET ANALYSIS REPORT")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("FILE ENCODING DETECTION")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    encoding_result = detect_file_encoding(file_path)
    # Log to file only - no console output
    log_print("=== File Encoding Detection ===")
    if "error" in encoding_result:
        encoding_info = f"Encoding: {encoding_result['encoding']} (Error: {encoding_result['error']})"
    elif "note" in encoding_result:
        encoding_info = (
            f"Encoding: {encoding_result['encoding']} ({encoding_result['note']})"
        )
    else:
        encoding_info = f"Encoding: {encoding_result['encoding']} (Confidence: {encoding_result['confidence']:.2%})"

    log_print(encoding_info)
    complete_output.append(encoding_info)
    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("MEMORY USAGE ANALYSIS")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    df_mem_usage = dataframe_memory_usage(df)
    complete_output.append(f"DataFrame Memory Usage: {df_mem_usage:.2f} MB")
    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("PANDAS DATAFRAME INFO")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    from io import StringIO

    info_buffer = StringIO()
    df.info(buf=info_buffer)
    info_text = info_buffer.getvalue()

    # Log to file only - no console output
    print("=== Pandas DataFrame Info ===")
    print(info_text)
    complete_output.append("=== Pandas DataFrame Info ===")
    complete_output.append(info_text)
    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("DETAILED DATASET INFORMATION")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    missing_count = df.isnull().sum().sum()
    missing_percentage = (missing_count / df.size) * 100
    duplicated_rows = df[df.duplicated(keep=False)]
    total_duplicates = duplicated_rows.shape[0]
    num_vars_count = df.select_dtypes(include=[DTYPE_NUMBER]).shape[1]
    cat_vars_count = df.select_dtypes(include=DTYPE_CATEGORICAL_LIST).shape[1]

    info_data = {
        "Info": [
            "Total Shape",
            "Range Index",
            "Columns",
            "Memory Usage",
            "Total Duplicated Rows",
            "Missing Values Count",
            "Missing Values Percentage",
        ],
        "Details": [
            f"{df.shape[0]} rows, {df.shape[1]} columns",
            f"{df.index.min()} to {df.index.max()}, {len(df)} entries",
            f"{df.shape[1]} columns",
            f"{df.memory_usage(deep=True).sum()} bytes",
            f"{total_duplicates} duplicates",
            f"{missing_count} missing values",
            f"{missing_percentage:.2f}% missing values",
        ],
    }
    info_table = pd.DataFrame(info_data)
    info_table_md = info_table.to_markdown(index=False, tablefmt="github")

    # Log to file only - no console output
    print("=== Dataset Information ===")
    print(info_table_md)
    complete_output.append("=== Dataset Information ===")
    complete_output.append(info_table_md)
    complete_output.append("")

    data_types_count = df.dtypes.value_counts().reset_index()
    data_types_count.columns = ["Data Type", "Count of Columns"]
    data_types_md = data_types_count.to_markdown(index=False, tablefmt="github")

    # Log to file only - no console output
    print("=== Data Types with Counts of Columns ===")
    print(data_types_md)
    complete_output.append("=== Data Types with Counts of Columns ===")
    complete_output.append(data_types_md)
    complete_output.append("")

    var_counts_data = {
        "Variable Type": ["Numerical Variables", "Categorical Variables"],
        "Count": [num_vars_count, cat_vars_count],
    }
    var_counts_table = pd.DataFrame(var_counts_data)
    var_counts_md = var_counts_table.to_markdown(index=False, tablefmt="github")

    # Log to file only - no console output
    print("=== Numerical and Categorical Variable Counts ===")
    print(var_counts_md)
    complete_output.append("=== Numerical and Categorical Variable Counts ===")
    complete_output.append(var_counts_md)
    complete_output.append("")

    if not duplicated_rows.empty:
        # Log to file only - no console output
        print("=== Detailed List of Duplicated Rows ===")
        duplicated_md = duplicated_rows.to_markdown(index=True, tablefmt="github")
        print(duplicated_md)
        complete_output.append("=== Detailed List of Duplicated Rows ===")
        complete_output.append(duplicated_md)
    else:
        # Log to file only - no console output
        print("=== No Duplicated Rows Found ===")
        complete_output.append("=== No Duplicated Rows Found ===")

    complete_output.append("")

    shape_info = f"Dataset Shape: {df.shape}"
    # Log to file only - no console output
    print(shape_info)
    complete_output.append(shape_info)
    complete_output.append("")
    complete_output.append("Column Indices:")

    for idx, col in enumerate(df.columns):
        col_info = f"{idx}: {col}"
        # Log to file only - no console output
        print(col_info)
        complete_output.append(col_info)

    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("DATASET OVERVIEW - COLUMN DETAILS")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    complete_output.append(
        f"{'Index':<5} {'Col Index':<10} {'Attribute':<30} {'Data Type':<15} {'Range':<30} {'Distinct Count'}"
    )
    complete_output.append(f"{'-'*5} {'-'*10} {'-'*30} {'-'*15} {'-'*30} {'-'*15}")

    sorted_cols = sorted(df.columns, key=lambda col: str(df[col].dtype))
    for i, col in enumerate(sorted_cols, 1):
        col_index = df.columns.get_loc(col)
        dtype, distinct = str(df[col].dtype), df[col].nunique()
        rng = (
            f"{df[col].min()} - {df[col].max()}"
            if dtype in DTYPE_ALL_NUMERICAL
            else "N/A"
        )
        line = f"{i:<5} {col_index:<10} {col:<30} {dtype:<15} {rng:<30} {distinct}"
        # Log to file only - no console output
        print(line)
        complete_output.append(line)

    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("STATISTICAL ANALYSIS (RESEARCHPY)")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    num_res, cat_res = [], []
    num_cols = df.select_dtypes(
        include=[
            "int64",
            "float64",
            "int8",
            "int16",
            "int32",
            "float16",
            "float32",
        ]
    ).columns
    cat_cols = df.select_dtypes(include=DTYPE_CATEGORICAL_LIST).columns

    # Only use ResearchPy if available
    if rp is not None:
        for col in num_cols:
            stats = rp.summary_cont(df[col].dropna())
            stats["Variable"] = col
            num_res.append(stats)
        for col in cat_cols:
            stats = rp.summary_cat(df[col])
            stats["Variable"] = col
            cat_res.append(stats)
    else:
        complete_output.append(
            "ResearchPy not available - skipping ResearchPy analysis"
        )

    if num_res:
        numerical_analysis = "=== Numerical Analysis ==="
        # Log to file only - no console output
        print(numerical_analysis)
        complete_output.append(numerical_analysis)

        numerical_table = pd.concat(num_res, ignore_index=True).to_markdown(
            tablefmt="pipe"
        )
        # Log to file only - no console output
        print(numerical_table)
        complete_output.append(numerical_table)
        complete_output.append("")

    if cat_res:
        categorical_analysis = "=== Categorical Analysis ==="
        # Log to file only - no console output
        print(categorical_analysis)
        complete_output.append(categorical_analysis)

        categorical_table = pd.concat(cat_res, ignore_index=True).to_markdown(
            tablefmt="pipe"
        )
        # Log to file only - no console output
        print(categorical_table)
        complete_output.append(categorical_table)
        complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("DETAILED STATISTICAL SUMMARIES")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    num_summary_df = num_summary(df)
    if not num_summary_df.empty:
        num_stats_header = "=== Numerical Summary Statistics ==="
        # Log to file only - no console output
        print(num_stats_header)
        complete_output.append(num_stats_header)

        num_stats_table = num_summary_df.to_markdown(tablefmt="pipe")
        # Log to file only - no console output
        print(num_stats_table)
        complete_output.append(num_stats_table)
        complete_output.append("")

    cat_summary_df = cat_summary(df)
    if not cat_summary_df.empty:
        cat_stats_header = "=== Categorical Summary Statistics ==="
        # Log to file only - no console output
        print(cat_stats_header)
        complete_output.append(cat_stats_header)

        cat_stats_table = cat_summary_df.to_markdown(tablefmt="pipe")
        # Log to file only - no console output
        print(cat_stats_table)
        complete_output.append(cat_stats_table)
        complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("MISSING AND INFINITE VALUES ANALYSIS")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    missing_header = "=== Missing and Infinite Values Analysis ==="
    complete_output.append(missing_header)
    complete_output.append("")

    total_entries = df.shape[0]
    missing_summary = pd.DataFrame(
        {
            "Data Type": df.dtypes,
            "Missing Count": df.isna().sum(),
            "Missing Percentage": (df.isna().sum() / total_entries) * 100,
        }
    ).sort_values(by="Missing Percentage", ascending=False)
    missing_summary = missing_summary[missing_summary["Missing Count"] > 0]

    if not missing_summary.empty:
        missing_text = "Missing Values Summary:"
        complete_output.append(missing_text)
        missing_table = missing_summary.to_markdown(tablefmt="pipe")
        complete_output.append(missing_table)
    else:
        no_missing_text = "No missing values found."
        complete_output.append(no_missing_text)

    complete_output.append("")

    infinite_summary = pd.DataFrame(
        {
            "Data Type": df.dtypes,
            "Positive Infinite Count": (df == np.inf).sum(),
            "Positive Infinite Percentage": ((df == np.inf).sum() / total_entries)
            * 100,
            "Negative Infinite Count": (df == -np.inf).sum(),
            "Negative Infinite Percentage": ((df == -np.inf).sum() / total_entries)
            * 100,
        }
    ).sort_values(by="Positive Infinite Percentage", ascending=False)
    infinite_summary = infinite_summary[
        (infinite_summary["Positive Infinite Count"] > 0)
        | (infinite_summary["Negative Infinite Count"] > 0)
    ]

    if not infinite_summary.empty:
        inf_text = "Infinite Values Summary:"
        complete_output.append(inf_text)
        inf_table = infinite_summary.to_markdown(tablefmt="pipe")
        complete_output.append(inf_table)
    else:
        no_inf_text = "No infinite values found."
        complete_output.append(no_inf_text)

    complete_output.append("")

    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("ADDITIONAL ANALYSIS")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("")

    complete_output.append("=== High Cardinality Categorical Columns ===")
    high_card_cols = cat_high_cardinality(df, threshold=20)
    if high_card_cols:
        high_card_info = (
            f"High cardinality columns (>20 unique values): {', '.join(high_card_cols)}"
        )
        complete_output.append(high_card_info)
    else:
        no_high_card = "No high cardinality categorical columns found."
        complete_output.append(no_high_card)
    complete_output.append("")

    complete_output.append("=== Mixed Data Types Detection ===")
    mixed_columns = []
    for col in df.columns:
        unique_types = {type(val).__name__ for val in df[col].dropna().values}
        if len(unique_types) > 1:
            mixed_columns.append([col, ", ".join(sorted(unique_types))])

    if not mixed_columns:
        no_mixed_msg = "No mixed data types detected!"
        complete_output.append(no_mixed_msg)
    else:
        mixed_table = tabulate(
            mixed_columns,
            headers=["Column Name", "Detected Data Types"],
            tablefmt="pipe",
        )
        complete_output.append(mixed_table)

    complete_output.append("")
    complete_output.append("=" * REPORT_SEPARATOR_80)
    complete_output.append("END OF COMPLETE ANALYSIS REPORT")
    complete_output.append("=" * REPORT_SEPARATOR_80)

    os.makedirs(save_dir, exist_ok=True)
    combined_analysis_path = os.path.join(save_dir, OUTPUT_DATASET_ANALYSIS)
    with open(combined_analysis_path, FILE_MODE_WRITE, encoding=DEFAULT_ENCODING) as f:
        f.write("\n".join(complete_output))

    if not num_summary_df.empty:
        num_summary_path = os.path.join(save_dir, OUTPUT_NUMERICAL_SUMMARY)
        num_summary_df.to_csv(num_summary_path, sep=delimiter)

    if not cat_summary_df.empty:
        cat_summary_path = os.path.join(save_dir, OUTPUT_CATEGORICAL_SUMMARY)
        cat_summary_df.to_csv(cat_summary_path, sep=delimiter)

    if not missing_summary.empty or not infinite_summary.empty:
        missing_inf_combined = (
            pd.concat([missing_summary, infinite_summary])
            if not missing_summary.empty and not infinite_summary.empty
            else (missing_summary if not missing_summary.empty else infinite_summary)
        )
        missing_inf_path = os.path.join(save_dir, "missing_infinite_values.csv")
        missing_inf_combined.to_csv(missing_inf_path, sep=delimiter)

    return combined_analysis_path


def distinct_val_tabular_txt(
    data,
    output_file=OUTPUT_DISTINCT_VALUES,
    max_rows_per_column=20,
    max_columns=3,
):
    """
    Displays the distinct value counts of all variables in a tabular format grouped by data type,
    with columns_info output at the top, saved as a TXT file in tabulate pipe format.
    Long tables are split into side-by-side columns for better readability.

    Parameters:
    - data: DataFrame to analyze
    - output_file: Output filename
    - max_rows_per_column: Maximum rows per column before splitting (default: 20)
    - max_columns: Maximum number of side-by-side columns (default: 3)
    """

    def capture_columns_info(data):
        """Capture the output of columns_info function as string"""
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()

        # Call the actual columns_info function
        columns_info("Dataset Overview", data)

        sys.stdout = old_stdout
        return buffer.getvalue()

    def create_side_by_side_table(
        table_data, headers, max_rows_per_column, max_columns
    ):
        """Create a side-by-side table layout for long tables"""
        from tabulate import tabulate

        total_rows = len(table_data)

        if total_rows <= max_rows_per_column:
            return tabulate(
                table_data, headers=headers, tablefmt="pipe", stralign="left"
            )

        num_columns = min(max_columns, math.ceil(total_rows / max_rows_per_column))
        rows_per_column = math.ceil(total_rows / num_columns)

        chunks = []
        for i in range(num_columns):
            start_idx = i * rows_per_column
            end_idx = min(start_idx + rows_per_column, total_rows)
            chunk = table_data[start_idx:end_idx] if start_idx < total_rows else []
            chunks.append(chunk)

        side_by_side_data = []
        max_chunk_length = max(len(chunk) for chunk in chunks) if chunks else 0

        side_headers = []
        for i in range(num_columns):
            side_headers.extend([f"{headers[0]} ({i+1})", f"{headers[1]} ({i+1})"])

        for row_idx in range(max_chunk_length):
            row = []
            for chunk_idx, chunk in enumerate(chunks):
                if row_idx < len(chunk):
                    row.extend([chunk[row_idx][0], chunk[row_idx][1]])
                else:
                    row.extend(["", ""])

            side_by_side_data.append(row)

        return tabulate(
            side_by_side_data,
            headers=side_headers,
            tablefmt="pipe",
            stralign="left",
        )

    grouped_columns = data.columns.to_series().groupby(data.dtypes).groups

    report_parts = []

    columns_info_output = capture_columns_info(data)
    report_parts.append(columns_info_output)

    report_parts.append("DISTINCT VALUES COUNT BY DATA TYPE")
    report_parts.append("=" * REPORT_SEPARATOR_80)
    report_parts.append("")

    for dtype, variable_columns in grouped_columns.items():
        dtype_str = str(dtype).upper()
        report_parts.append(
            f"\n{dtype_str} COLUMNS ({len(variable_columns)} variables)"
        )
        report_parts.append("-" * SEPARATOR_LENGTH)

        for variable in variable_columns:
            value_counts = data[variable].value_counts(dropna=False).sort_index()
            distinct_count = value_counts.shape[0]

            report_parts.append(
                f"\nVariable: {variable} (Distinct Count: {distinct_count})"
            )

            if distinct_count > max_rows_per_column:
                num_cols = min(
                    max_columns,
                    math.ceil(distinct_count / max_rows_per_column),
                )
                report_parts.append(
                    f"(Table split into {num_cols} side-by-side columns for better readability)"
                )

            report_parts.append("-" * 40)

            if len(value_counts) > 0:
                table_data = []
                for value, count in value_counts.items():
                    if pd.isna(value):
                        display_value = "NaN"
                    else:
                        display_value = str(value)
                    table_data.append([display_value, count])

                table_str = create_side_by_side_table(
                    table_data,
                    ["Value", "Count"],
                    max_rows_per_column,
                    max_columns,
                )
                report_parts.append(table_str)
            else:
                report_parts.append("No data available")

            report_parts.append("")

    with open(output_file, FILE_MODE_WRITE, encoding=DEFAULT_ENCODING) as file:
        file.write("\n".join(report_parts))
