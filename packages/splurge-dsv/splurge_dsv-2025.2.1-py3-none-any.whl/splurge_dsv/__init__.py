"""Top-level package for Splurge DSV.

This package provides utilities for parsing, processing and manipulating
delimited string value (DSV) files. It exposes the high-level API objects
such as :class:`~splurge_dsv.dsv.Dsv` and :class:`~splurge_dsv.dsv.DsvConfig`,
convenience helpers, and the package's exception types.

License: MIT
Copyright (c) 2025 Jim Schilling
"""

# Ensure current working directory exists. Some test environments or earlier
# test cases may remove the process working directory which causes calls to
# os.getcwd() to raise FileNotFoundError later during test execution. Guard
# against that here by switching to this package directory when cwd is missing.
import os
from pathlib import Path as _Path

try:
    try:
        # os.getcwd() can raise FileNotFoundError in CI/runner environments
        # if the original working directory was removed. Check existence via
        # Path.cwd(); if it doesn't exist, switch to the package directory.
        if not _Path.cwd().exists():
            os.chdir(_Path(__file__).resolve().parent)
    except FileNotFoundError:
        # Fall back to package directory when cwd is gone
        os.chdir(_Path(__file__).resolve().parent)
except Exception:
    # Be conservative: if this fails, don't break import - tests will report
    # the original failure. Swallowing ensures import-time is resilient.
    pass

# Local imports
from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import (
    SplurgeDsvConfigurationError,
    SplurgeDsvDataProcessingError,
    # canonical SplurgeDsv* exception names
    SplurgeDsvError,
    SplurgeDsvFileEncodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFileOperationError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvFormatError,
    SplurgeDsvParameterError,
    SplurgeDsvParsingError,
    SplurgeDsvPathValidationError,
    SplurgeDsvPerformanceWarning,
    SplurgeDsvRangeError,
    SplurgeDsvResourceAcquisitionError,
    SplurgeDsvResourceError,
    SplurgeDsvResourceReleaseError,
    SplurgeDsvStreamingError,
    SplurgeDsvTypeConversionError,
    SplurgeDsvValidationError,
)
from splurge_dsv.path_validator import PathValidator
from splurge_dsv.string_tokenizer import StringTokenizer
from splurge_dsv.text_file_helper import TextFileHelper

__version__ = "2025.2.1"
__author__ = "Jim Schilling"
__license__ = "MIT"

__all__ = [
    # Main classes
    "Dsv",
    "DsvConfig",
    "DsvHelper",
    # Exceptions
    "SplurgeDsvError",
    "SplurgeDsvValidationError",
    "SplurgeDsvFileOperationError",
    "SplurgeDsvFileNotFoundError",
    "SplurgeDsvFilePermissionError",
    "SplurgeDsvFileEncodingError",
    "SplurgeDsvPathValidationError",
    "SplurgeDsvDataProcessingError",
    "SplurgeDsvParsingError",
    "SplurgeDsvTypeConversionError",
    "SplurgeDsvStreamingError",
    "SplurgeDsvConfigurationError",
    "SplurgeDsvResourceError",
    "SplurgeDsvResourceAcquisitionError",
    "SplurgeDsvResourceReleaseError",
    "SplurgeDsvPerformanceWarning",
    "SplurgeDsvParameterError",
    "SplurgeDsvRangeError",
    "SplurgeDsvFormatError",
    # Utility classes
    "StringTokenizer",
    "TextFileHelper",
    "PathValidator",
]
