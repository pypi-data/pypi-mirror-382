# AutoCSV Profiler

A Python toolkit for automated CSV data analysis with statistical profiling and visualization.

[![PyPI version](https://badge.fury.io/py/autocsv-profiler.svg)](https://pypi.org/project/autocsv-profiler/)
[![Python Version](https://img.shields.io/badge/python-3.8--3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/dhaneshbb/autocsv-profiler)

## Overview

AutoCSV Profiler provides automated analysis of CSV files with statistical summaries, data quality assessment, and visualization generation. It features memory-efficient processing, automatic delimiter detection, and a rich console interface.

**Key Features:**
- Interactive analysis mode with step-by-step guidance
- Automatic delimiter detection and encoding validation
- Memory-efficient chunked processing for large files
- Statistical analysis with descriptive statistics and data quality metrics
- Visualization generation (KDE plots, box plots, Q-Q plots, bar charts, pie charts)
- Rich console interface with progress tracking
- Configurable via CLI flags or environment variables

## Installation

**Requirements:** Python 3.8 - 3.13

```bash
pip install autocsv-profiler
```

## Quick Start

**Interactive Mode:**
```bash
autocsv-profiler
```

Step-by-step guidance for first-time users.

**Direct Analysis:**
```bash
autocsv-profiler data.csv
```

Quick analysis with sensible defaults.

## Usage

```bash
# Show help
autocsv-profiler --help
```

### Command Line Interface

```bash
# Show help
autocsv-profiler --help

# Basic analysis
autocsv-profiler data.csv

# Custom output directory
autocsv-profiler data.csv --output results/

# Custom delimiter
autocsv-profiler data.csv --delimiter ";"

# Large file processing
autocsv-profiler data.csv --memory-limit 4.0 --chunk-size 20000

# Non-interactive mode
autocsv-profiler data.csv --non-interactive

# Debug mode
autocsv-profiler data.csv --debug
```

### Python API

```python
import autocsv_profiler

# Basic analysis
result_dir = autocsv_profiler.analyze('data.csv')
print(f"Analysis saved to: {result_dir}")

# Custom configuration
result_dir = autocsv_profiler.analyze(
    csv_file_path='data.csv',
    output_dir='results/',
    delimiter=',',
    chunk_size=10000,
    memory_limit_gb=1
)

# Interactive mode
result_dir = autocsv_profiler.analyze(
    csv_file_path='data.csv',
    interactive=True
)
```

### Configuration

Environment variables with `AUTOCSV_` prefix:

```bash
# Performance settings
export AUTOCSV_PERFORMANCE_MEMORY_LIMIT_GB=2
export AUTOCSV_PERFORMANCE_CHUNK_SIZE=20000

# Logging settings
export AUTOCSV_LOGGING_LEVEL=DEBUG
export AUTOCSV_LOGGING_CONSOLE_LEVEL=INFO
```

## Output Files

Analysis generates the following files in the output directory:

**Data Summaries:**
- `dataset_analysis.txt` - Dataset overview and basic statistics
- `numerical_summary.csv` - Summary statistics for numeric columns
- `categorical_summary.csv` - Summary for categorical columns
- `numerical_stats.csv` - Descriptive statistics using researchpy
- `categorical_stats.csv` - Categorical frequency analysis
- `distinct_values.txt` - Unique value counts per column

**Visualizations:**
- `kde_plots/` - Kernel density estimation plots
- `box_plots/` - Box plots for numerical variables
- `qq_plots/` - Q-Q plots for normality testing
- `bar_charts/` - Bar charts for categorical variables
- `pie_charts/` - Categorical distribution pie charts

**Process Logs:**
- `autocsv_profiler.log` - Processing log file

## Documentation

**User Documentation:**
- [User Guide](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/user-guide.md) - Installation, CLI usage, and examples
- [Configuration](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/configuration.md) - Settings and environment variables
- [Troubleshooting](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/troubleshooting.md) - Problem-solving guide

**Developer Documentation:**
- [API Reference](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/api-reference.md) - Python API documentation
- [Developer Guide](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/developer-guide.md) - Development workflow and architecture
- [Architecture Diagrams](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/diagrams.md) - Visual system architecture

**Complete Index:**
- [Documentation Index](https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/index.md) - Complete documentation overview

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://github.com/dhaneshbb/autocsv-profiler/blob/master/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](https://github.com/dhaneshbb/autocsv-profiler/blob/master/LICENSE) for details.

This software includes third-party components. See [NOTICE](https://github.com/dhaneshbb/autocsv-profiler/blob/master/NOTICE) for complete license information.

## Links

- **PyPI:** https://pypi.org/project/autocsv-profiler/
- **Repository:** https://github.com/dhaneshbb/autocsv-profiler
- **Documentation:** https://github.com/dhaneshbb/autocsv-profiler/blob/master/docs/index.md
- **Issues:** https://github.com/dhaneshbb/autocsv-profiler/issues
- **Changelog:** https://github.com/dhaneshbb/autocsv-profiler/blob/master/CHANGELOG.md

---

Version: 2.0.0 | Status: Beta | Python: 3.8-3.13

Copyright 2025 dhaneshbb | License: MIT | Homepage: https://github.com/dhaneshbb/autocsv-profiler
