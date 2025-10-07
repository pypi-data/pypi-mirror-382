"""
File path validation utilities for secure file operations.

This module provides utilities for validating file paths to prevent
path traversal attacks and ensure secure file operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Standard library imports
import os
import re
from pathlib import Path

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvPathValidationError,
)

# Module-level constants for path validation
_MAX_PATH_LENGTH = 4096  # Maximum path length for most filesystems
_DEFAULT_FILENAME = "unnamed_file"  # Default filename when sanitization results in empty string


class PathValidator:
    """
    Utility class for validating file paths securely.

    This class provides methods to validate file paths and prevent
    path traversal attacks and other security vulnerabilities.
    """

    # Private constants for path validation
    _PATH_TRAVERSAL_PATTERNS = [
        r"\.\.",  # Directory traversal
        r"//+",  # Multiple forward slashes (including //)
        r"\\{2,}",  # Two or more consecutive backslashes (not normal Windows paths)
        r"~",  # Home directory expansion
    ]

    _DANGEROUS_CHARS = [
        "<",
        ">",
        '"',
        "|",
        "?",
        "*",  # Windows reserved characters (excluding ':' for drive letters)
        "\x00",
        "\x01",
        "\x02",
        "\x03",
        "\x04",
        "\x05",
        "\x06",
        "\x07",  # Control characters
        "\x08",
        "\x09",
        "\x0a",
        "\x0b",
        "\x0c",
        "\x0d",
        "\x0e",
        "\x0f",
        "\x10",
        "\x11",
        "\x12",
        "\x13",
        "\x14",
        "\x15",
        "\x16",
        "\x17",
        "\x18",
        "\x19",
        "\x1a",
        "\x1b",
        "\x1c",
        "\x1d",
        "\x1e",
        "\x1f",
    ]

    MAX_PATH_LENGTH = _MAX_PATH_LENGTH

    @classmethod
    def validate_path(
        cls,
        file_path: str | Path,
        *,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_readable: bool = False,
        allow_relative: bool = True,
        base_directory: str | Path | None = None,
    ) -> Path:
        """Validate a filesystem path for security and correctness.

        This is the central path validation routine used across the package.

        Args:
            file_path: Path or string to validate.
            must_exist: If True, require the path to exist.
            must_be_file: If True, require the path to be a regular file.
            must_be_readable: If True, check read permission via os.access().
            allow_relative: If False, disallow relative paths.
            base_directory: Optional directory to resolve relative paths
                against and to restrict the resolved path to.

        Returns:
            pathlib.Path: Resolved and normalized path.

        Raises:
            SplurgeDsvPathValidationError: If any validation rule fails.
            SplurgeDsvFileNotFoundError: If must_exist is True and file is missing.
            SplurgeDsvFilePermissionError: If must_be_readable is True and the
                file is not readable.
        """
        # Convert to Path object
        path = Path(file_path) if isinstance(file_path, str) else file_path

        # Get the original string for validation (before Path normalization)
        path_str = str(file_path) if isinstance(file_path, str) else str(path)

        # Check for dangerous characters
        cls._check_dangerous_characters(path_str)

        # Check for path traversal patterns
        cls._check_path_traversal(path_str)

        # Check path length
        cls._check_path_length(path_str)

        # Handle relative paths
        if not path.is_absolute() and not allow_relative:
            raise SplurgeDsvPathValidationError(
                f"Relative paths are not allowed: {path}", details="Set allow_relative=True to allow relative paths"
            )

        # Resolve path (handles symlinks and normalizes)
        try:
            if base_directory:
                base_path = Path(base_directory).resolve()
                if not path.is_absolute():
                    resolved_path = (base_path / path).resolve()
                else:
                    resolved_path = path.resolve()

                # Ensure resolved path is within base directory
                try:
                    resolved_path.relative_to(base_path)
                except ValueError:
                    raise SplurgeDsvPathValidationError(
                        f"Path {path} resolves outside base directory {base_directory}",
                        details="Path traversal detected",
                    ) from None
            else:
                resolved_path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise SplurgeDsvPathValidationError(
                f"Failed to resolve path {path}: {e}", details="Check if path contains invalid characters or symlinks"
            ) from e

        # Check if file exists
        if must_exist and not resolved_path.exists():
            raise SplurgeDsvFileNotFoundError(
                f"File does not exist: {resolved_path}", details="Set must_exist=False to allow non-existent files"
            )

        # Check if it's a file (not directory)
        if must_be_file and resolved_path.exists() and not resolved_path.is_file():
            raise SplurgeDsvPathValidationError(
                f"Path is not a file: {resolved_path}", details="Path exists but is not a regular file"
            )

        # Check if file is readable
        if must_be_readable:
            if not resolved_path.exists():
                raise SplurgeDsvFileNotFoundError(
                    f"Cannot check readability of non-existent file: {resolved_path}",
                    details="File must exist to check readability",
                )

            if not os.access(resolved_path, os.R_OK):
                raise SplurgeDsvFilePermissionError(
                    f"File is not readable: {resolved_path}", details="Check file permissions"
                )

        return resolved_path

    @classmethod
    def _is_valid_windows_drive_pattern(cls, path_str: str) -> bool:
        """Return True if ``path_str`` looks like a valid Windows drive pattern.

        Accepts both ``C:`` and ``C:\\...`` or ``C:/...`` forms.
        """
        # Must be C: at the end of the string, or C:\ (or C:/) followed by path
        return bool(re.match(r"^[A-Za-z]:$", path_str)) or bool(re.match(r"^[A-Za-z]:[\\/]", path_str))

    @classmethod
    def _check_dangerous_characters(cls, path_str: str) -> None:
        """Raise if ``path_str`` contains characters disallowed by policy.

        This guards against NULs, control characters, and reserved filesystem
        characters which may be used in injection or traversal attacks.
        """
        # Check for dangerous characters, but allow colons in Windows drive letters
        for char in cls._DANGEROUS_CHARS:
            if char in path_str:
                raise SplurgeDsvPathValidationError(
                    f"Path contains dangerous character: {repr(char)}",
                    details=f"Character at position {path_str.find(char)}",
                )

        # Special handling for colons - only allow them in Windows drive letters (e.g., C:)
        if ":" in path_str:
            if not cls._is_valid_windows_drive_pattern(path_str):
                raise SplurgeDsvPathValidationError(
                    "Path contains colon in invalid position",
                    details="Colons are only allowed in Windows drive letters (e.g., C: or C:\\)",
                )

    @classmethod
    def _check_path_traversal(cls, path_str: str) -> None:
        """Raise if ``path_str`` contains obvious traversal patterns.

        This is a best-effort check that catches sequences such as ``..``
        and unusual repeated separators that are likely malicious.
        """
        for pattern in cls._PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, path_str):
                raise SplurgeDsvPathValidationError(
                    f"Path contains traversal pattern: {pattern}", details="Path traversal attacks are not allowed"
                )

    @classmethod
    def _check_path_length(cls, path_str: str) -> None:
        """Raise if the path exceeds the configured maximum length.

        Long paths can indicate malformed input or attempt to overflow
        downstream APIs; this check enforces a sane upper bound.
        """
        if len(path_str) > cls.MAX_PATH_LENGTH:
            raise SplurgeDsvPathValidationError(
                f"Path is too long: {len(path_str)} characters",
                details=f"Maximum allowed length is {cls.MAX_PATH_LENGTH} characters",
            )

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize a filename by removing dangerous characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace dangerous characters
        sanitized = filename

        # Replace Windows reserved characters
        for char in ["<", ">", ":", '"', "|", "?", "*"]:
            sanitized = sanitized.replace(char, "_")

        # Remove control characters
        sanitized = "".join(char for char in sanitized if ord(char) >= 32)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Ensure filename is not empty
        if not sanitized:
            sanitized = _DEFAULT_FILENAME

        return sanitized

    @classmethod
    def is_safe_path(cls, file_path: str | Path) -> bool:
        """
        Check if a path is safe without raising exceptions.

        Args:
            file_path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            cls.validate_path(file_path)
            return True
        except (SplurgeDsvPathValidationError, SplurgeDsvFileNotFoundError, SplurgeDsvFilePermissionError):
            return False
