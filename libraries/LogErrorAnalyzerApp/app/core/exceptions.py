"""Application-specific exceptions."""


class LogAnalyzerError(Exception):
    """Base exception for expected application failures."""


class InvalidPathError(LogAnalyzerError):
    """Raised when the provided path is invalid."""


class UnsupportedFileTypeError(LogAnalyzerError):
    """Raised when no supported log files can be processed."""


class LogReadError(LogAnalyzerError):
    """Raised when a log file cannot be read."""


class LLMServiceError(LogAnalyzerError):
    """Raised when LLM solution generation fails."""


class TicketServiceError(LogAnalyzerError):
    """Raised when ticket creation fails."""

