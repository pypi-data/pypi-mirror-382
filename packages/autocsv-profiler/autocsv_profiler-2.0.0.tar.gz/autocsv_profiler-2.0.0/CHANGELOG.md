# Changelog

All notable changes to AutoCSV Profiler will be documented in this file

## [2.0.0] - 2025-10-09

### Added
- Rich console interface with progress tracking and tables
- Interactive analysis mode with step-by-step guidance
- Memory management with configurable limits (default: 1GB)
- Automatic encoding detection and validation
- Configuration system with environment variable overrides (AUTOCSV_* prefix)
- Public API: `analyze()` function for programmatic access
- Exception hierarchy: AutoCSVProfilerError, FileProcessingError, DelimiterDetectionError, ReportGenerationError
- Settings management with runtime configuration
- Logging utilities: get_logger(), log_print()
- Version information functions and metadata
- CLI flags: --output, --delimiter, --non-interactive, --chunk-size, --memory-limit, --debug
- Modular package structure with organized codebase
- Test framework with 50% minimum coverage requirement
- Documentation: 7 comprehensive guides (API reference, user guide, developer guide, configuration, troubleshooting, architecture diagrams, index)
- GitHub templates: issue templates (bug report, feature request), pull request template
- Pre-commit hooks: Black, isort, MyPy, flake8
- Development tools: pytest with coverage, parallel testing, timeout handling
- EditorConfig for consistent code formatting across editors
- Type checking support with py.typed marker and MyPy configuration
- CLI entry point: autocsv-profiler command
- Secrets detection with detect-secrets baseline
- Statistical analysis with researchpy integration
- Data presentation with tableone and tabulate

### Changed
- Package architecture from single-file to modular structure
- Python compatibility from 3.9+ to 3.8-3.13 support
- Console interface from ANSI color codes to Rich library
- Configuration from external YAML files to embedded settings
- Dependencies: added rich==14.1.0, psutil==7.0.0, tqdm==4.67.1, charset-normalizer>=3.0.0
- Dependencies: added researchpy>=0.3.0, pyyaml==6.0.2, tabulate==0.9.0, tableone==0.9.5
- Dependencies: updated pandas==2.3.1, numpy==2.2.6, scipy>=1.10.0, statsmodels>=0.14.0
- Development status: Beta (Development Status :: 4 - Beta)
- CLI interface to include interactive mode and progress tracking

### Removed
- scikit-learn dependency
- missingno dependency
- Single-file architecture

### Security
- detect-secrets baseline configuration
- Pre-commit integration for secrets scanning

### Performance
- Memory limit configuration (default: 1GB)
- Chunked processing for large files (10,000 row default)
- Real-time memory monitoring with psutil
- Lazy imports for optional dependencies

### Documentation
- Development guidelines and project architecture documentation
- MIT license with copyright notice
- NOTICE file with third-party component attribution
- THIRD_PARTY_LICENSES.txt for license compliance

## [1.1.0] - 2025-08-04

### Added
- PyPI package distribution as `autocsv-profiler`
- CLI interface with argparse and standardized options
- Single-module architecture
- ANSI color console output for better user experience
- Python API with main analysis functions
- Automatic CSV delimiter detection (from v1.0.0)
- Statistical analysis and data summaries
- Basic visualizations (box plots, histograms, correlation matrices)

### Changed
- Installation: pip-installable package (from conda multi-environment setup)
- Interface: CLI with argparse (from Windows batch file)
- Architecture: single Python environment (from 3 conda environments)
- Python requirement: 3.9+ compatibility

### Removed
- YData profiling engine (profile_ydata_profiling_report.py)
- SweetViz profiling engine (profile_sweetviz_report.py)
- DataPrep profiling engine (profile_dataprep_report.py)
- Cerberus validation engine (cerberus_validator_specific_columns.py)
- Conda environment dependencies (ds_ml, sweetz_ydata_profiler, dataprep)
- Windows batch orchestration (run_analysis.bat)

### Dependencies
- Added: pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, statsmodels, tqdm, tableone, missingno, tabulate
- Python: 3.9+ requirement

## [1.0.0] - 2025-04-09

### Added - Initial Release
- Multi-environment conda-based architecture
- Core analysis modules:
  - auto_csv_profiler.py - Statistical analysis
  - profile_ydata_profiling_report.py - YData profiling reports
  - profile_sweetviz_report.py - SweetViz visual reports
  - profile_dataprep_report.py - DataPrep EDA reports
  - cerberus_validator_specific_columns.py - Schema validation
  - recognize_delimiter.py - Automatic delimiter detection
- Windows batch orchestration (run_analysis.bat)
- Three isolated conda environments (ds_ml, sweetz_ydata_profiler, dataprep)
- Interactive user prompts for CSV path and analysis selection
- HTML report generation with multiple profiling engines
- Cross-platform path handling
- Sample dataset and documentation

### Features
- Automated CSV analysis workflow
- Multiple profiling engines integration (YData, SweetViz, DataPrep)
- Environment isolation for dependency conflict resolution
- Batch processing with user interaction
- Statistical analysis and visualization suite

---

## Project History

The initial release **v1.0.0** is available at:
[https://github.com/dhaneshbb/autocsv-profiler-suite](https://github.com/dhaneshbb/autocsv-profiler-suite)

Starting from **v1.1.0** onward, this project focuses on a **single-environment** setup.
It was separated from the multi-environment suite to enable more focused, environment-specific development.

For the **multi-environment architecture** (with YData Profiling, SweetViz, and DataPrep integration), visit:
[https://github.com/dhaneshbb/autocsv-profiler-suite](https://github.com/dhaneshbb/autocsv-profiler-suite)

For more details about this **single-environment version**, see:
[https://github.com/dhaneshbb/autocsv-profiler](https://github.com/dhaneshbb/autocsv-profiler)

---

Version: 2.0.0 | Status: Beta | Python: 3.8-3.13

Copyright 2025 dhaneshbb | License: MIT | Homepage: https://github.com/dhaneshbb/autocsv-profiler
