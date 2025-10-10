"""Custom exceptions for the AutoCSV Profiler."""


class AutoCSVProfilerError(Exception):
    """Base class for exceptions in this module."""


class FileProcessingError(AutoCSVProfilerError):
    """Exception raised for errors in file processing."""

    def __init__(self, message: str = "Error processing file") -> None:
        self.message = message
        super().__init__(self.message)


class DelimiterDetectionError(AutoCSVProfilerError):
    """Exception raised for errors in delimiter detection."""

    def __init__(self, message: str = "Could not determine delimiter") -> None:
        self.message = message
        super().__init__(self.message)


class ReportGenerationError(AutoCSVProfilerError):
    """Exception raised for errors in report generation."""

    def __init__(self, report_name: str, original_exception: Exception) -> None:
        self.report_name = report_name
        self.original_exception = original_exception
        message = f"Failed to generate {report_name} report: {original_exception}"
        super().__init__(message)
