#!/usr/bin/env python3
"""
AutoCSV Profiler - Command Line Interface

Simplified CLI for the single-environment CSV analysis toolkit.
"""

import argparse
import os
import sys
from typing import Optional

# Import only lightweight modules at module level for fast --help
try:
    from autocsv_profiler.constants import (
        CLI_CHUNK_SIZE_HELP_DEFAULT,
        DEBUG_ENV_VAR,
        DEFAULT_CHUNK_SIZE,
        DEFAULT_MEMORY_LIMIT_GB,
        MSG_DEBUG_FLAG,
    )
    from autocsv_profiler.version import __version__
except ImportError as e:
    print(f"Error: Could not import AutoCSV Profiler: {e}")
    print("Please install the package: pip install autocsv-profiler")
    sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="autocsv-profiler",
        description="AutoCSV Profiler - CSV data analysis toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  autocsv-profiler                           # Interactive mode
  autocsv-profiler data.csv                  # Direct analysis
  autocsv-profiler data.csv --delimiter ";"  # Custom delimiter
  autocsv-profiler data.csv --output ./results  # Custom output directory
  autocsv-profiler --version                 # Show version information

For more information, visit: https://github.com/dhaneshbb/autocsv-profiler
        """,
    )

    parser.add_argument("csv_file", nargs="?", help="Path to the CSV file to analyze")

    parser.add_argument(
        "--output", "-o", type=str, help="Output directory for analysis results"
    )

    parser.add_argument(
        "--delimiter",
        "-d",
        type=str,
        help="CSV delimiter (auto-detected if not specified)",
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (skip interactive analysis phases)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Chunk size for processing large files (default: {CLI_CHUNK_SIZE_HELP_DEFAULT})",
    )

    parser.add_argument(
        "--memory-limit",
        type=float,
        default=DEFAULT_MEMORY_LIMIT_GB,
        help="Memory limit in GB (default: 1.0)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed error information",
    )

    parser.add_argument(
        "--version", "-v", action="version", version=f"AutoCSV Profiler {__version__}"
    )

    return parser


def run_direct_analysis(
    csv_file: str,
    output: Optional[str] = None,
    delimiter: Optional[str] = None,
    interactive: bool = True,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    memory_limit: float = DEFAULT_MEMORY_LIMIT_GB,
) -> bool:
    """Run direct analysis on a CSV file."""
    # Lazy import heavy modules only when needed
    from autocsv_profiler import analyze

    try:
        print(f"Starting analysis of: {csv_file}")

        result_dir = analyze(
            csv_file_path=csv_file,
            output_dir=output,
            delimiter=delimiter,
            interactive=interactive,
            chunk_size=chunk_size,
            memory_limit_gb=int(memory_limit),
        )

        print("\nAnalysis completed successfully!")
        print(f"Results saved to: {result_dir}")
        return True

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Analysis failed: {e}")
        return False


def run_interactive_analysis() -> bool:
    """Run interactive analysis mode."""
    # Lazy import heavy modules only when needed
    from autocsv_profiler.ui.interactive import CleanInteractiveMethods
    from autocsv_profiler.ui.interface import CleanCSVInterface

    try:
        # Initialize clean interface
        interface = CleanCSVInterface()
        interactive_methods = CleanInteractiveMethods(interface)

        # Run interactive analysis
        success = interactive_methods.run_analysis()
        return success

    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        return False
    except Exception as e:
        print(f"Interactive analysis failed: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Enable debug mode if requested
    if args.debug:
        os.environ[DEBUG_ENV_VAR] = "1"
        # Set debug logging level and enable file logging
        from autocsv_profiler.config import settings

        settings.set("logging.level", "DEBUG")
        settings.set("logging.console.level", "DEBUG")
        settings.set("logging.file.enabled", True)
        settings.set("logging.file.level", "DEBUG")

    try:
        if args.csv_file:
            # Direct analysis mode
            if not os.path.exists(args.csv_file):
                print(f"Error: CSV file not found: {args.csv_file}")
                sys.exit(1)

            success = run_direct_analysis(
                csv_file=args.csv_file,
                output=args.output,
                delimiter=args.delimiter,
                interactive=not args.non_interactive,
                chunk_size=args.chunk_size,
                memory_limit=args.memory_limit,
            )
        else:
            # Interactive mode
            success = run_interactive_analysis()

        if not success:
            print("\nAnalysis failed or was cancelled")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] CLI failed: {e}")

        # Debug information
        if args.debug or os.getenv(DEBUG_ENV_VAR):
            import traceback

            traceback.print_exc()
        else:
            print(MSG_DEBUG_FLAG)

        sys.exit(1)


if __name__ == "__main__":
    main()
