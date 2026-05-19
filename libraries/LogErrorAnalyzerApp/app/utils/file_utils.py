"""File discovery helpers."""

from __future__ import annotations

from pathlib import Path

from libraries.LogErrorAnalyzerApp.app.core.exceptions import InvalidPathError, UnsupportedFileTypeError


def discover_log_files(
    path_value: str,
    extensions: set[str],
    recursive: bool,
) -> list[Path]:
    """Discover supported log files from a file or folder path."""

    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        raise InvalidPathError(f"Path does not exist: {path}")

    if path.is_file():
        if path.suffix.lower() not in extensions:
            raise UnsupportedFileTypeError(f"Unsupported file type: {path.suffix}")
        return [path]

    pattern = "**/*" if recursive else "*"
    files = [
        file_path
        for file_path in path.glob(pattern)
        if file_path.is_file() and file_path.suffix.lower() in extensions
    ]
    if not files:
        raise UnsupportedFileTypeError("No supported log files found.")
    return sorted(files)

