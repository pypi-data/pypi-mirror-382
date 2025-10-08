# -*- coding: utf-8 -*-

"""
This module provides a group of commands related to tests, this way we
avoid defining them in each project that requires them.

Test File Discovery:
Automatically discovers test files matching these patterns:
  * test_*.py (standard pytest/unittest pattern)
  * *_test.py (standard pytest pattern)
  * tests_*.py (legacy pattern support)

Available Commands:
  * python manager.py run-tests --test-type unit
  * python manager.py run-tests --test-type integration
  * python manager.py run-tests --test-type functional
  * python manager.py run-tests --engine pytest
  * python manager.py run-tests --pattern "test_specific"
  * python manager.py run-coverage
  * python manager.py run-coverage --engine pytest
"""

from __future__ import annotations

import glob
import logging
import os
import sys
import typing
from unittest import TestCase
from unittest import TestLoader
from unittest import TestSuite
from unittest import TextTestRunner

import pytest
from click import echo, option
from click.decorators import group
from coverage import coverage, CoverageException

patterns = [
    "test_*.py",
    "*_test.py",
    "tests_*.py",
]


@group()
def cli_tests():
    """
    Group of commands related to tests.
    """


@cli_tests.command("run-tests")
@option("-t", "--test-type", "test_type", default="unit")
@option("-p", "--pattern", "pattern", default="tests*.py")
@option("-e", "--engine", "engine", default="unittest")
def run_tests(test_type: str, pattern: str, engine: str) -> None:
    """
    Runs tests in a specific directory using the specified engine.

    Args:
        test_type: Directory name under ./tests/ (e.g., 'unit', 'integration').
        pattern: File pattern for discovery or test name pattern for filtering.
        engine: Test engine to use ('unittest' or 'pytest').

    File Discovery:
        Automatically finds files matching: `test_*.py`, `*_test.py`, `tests_*.py`.

    Pattern Usage:
        - File patterns (*.py): Used for file discovery (pytest only).
        - Test names: Used with -k option for test filtering (pytest only).
        - Default: 'tests*.py' (backward compatibility).
    """

    validate_engines(engine)
    if not os.path.exists(f"./tests/{test_type}"):
        echo(f"The directory: {test_type} does not exist under ./tests!", err=True)
        sys.exit(1)

    if test_type == "unit":
        # Just removing verbosity from unit tests...
        level = os.getenv("LOGGER_LEVEL_FOR_TEST", str(logging.ERROR))
        os.environ["LOGGER_LEVEL"] = level

    if engine == "pytest":
        test_path = f"./tests/{test_type}"

        # Determine if pattern is for file discovery or test filtering
        is_file_pattern = "*" in pattern and pattern.endswith(".py")

        # Find all test files using appropriate patterns
        test_files = []
        if is_file_pattern and pattern != "tests_*.py":
            # Use custom file pattern for discovery
            test_files.extend(glob.glob(f"{test_path}/{pattern}"))

        else:
            # Use default patterns for file discovery
            for pattern_glob in patterns:
                test_files.extend(glob.glob(f"{test_path}/{pattern_glob}"))

        if not test_files:
            echo(f"No test files found in {test_path}", err=True)
            sys.exit(1)

        # Use specific test files instead of directory discovery
        args = test_files + ["-v"]

        # If pattern is for test name filtering (not file pattern), use -k
        if not is_file_pattern and pattern != "tests_*.py":
            args.extend(["-k", pattern])

        exit_code = pytest.main(args)
        if exit_code != 0:
            sys.exit(exit_code)

    else:
        # Determine if pattern is for file discovery or test filtering
        is_file_pattern = "*" in pattern and pattern.endswith(".py")

        # Use the same patterns as pytest for consistency
        all_tests: typing.List[TestCase | TestSuite] = []
        if is_file_pattern and pattern != "tests_*.py":
            # Use custom file pattern for discovery
            tests = TestLoader().discover(f"./tests/{test_type}", pattern=pattern)
            all_tests.extend(tests)
        else:
            # Use default patterns for file discovery
            for pattern_glob in patterns:
                tests = TestLoader().discover(f"./tests/{test_type}", pattern=pattern_glob)
                all_tests.extend(tests)

        # Combine all discovered tests into a single suite
        combined_suite = TestSuite(all_tests)
        result = TextTestRunner(verbosity=2).run(combined_suite)
        if not result.wasSuccessful():
            sys.exit(1)


@cli_tests.command("run-coverage")
@option("-s", "--save-report", "save_report", default=True)
@option("-e", "--engine", "engine", default="unittest")
def run_coverage(save_report: bool, engine: str) -> None:
    """
    Runs all tests across all test directories and generates a coverage report.

    Args:
        save_report: Whether to save HTML and data coverage reports to disk.
        engine: Test engine to use ('unittest' or 'pytest').

    Coverage Analysis:
        - Runs tests with branch coverage enabled.
        - Analyzes all source files in current directory.
        - Generates console report summary.
        - Optionally saves HTML report (default: True).

    File Discovery:
        Automatically finds files matching: `test_*.py`, `*_test.py`, `tests_*.py`.
        across all subdirectories under `./tests/`.
    """

    validate_engines(engine)
    os.environ["LOGGER_LEVEL"] = os.getenv("LOGGER_LEVEL_FOR_TEST", str(logging.ERROR))
    coverage_ = coverage(branch=True, source=["."])
    coverage_.start()

    if engine == "pytest":
        # Finding all test files using multiple patterns
        # across all test directories...
        test_files = []
        for pattern_glob in patterns:
            test_files.extend(glob.glob(f"./tests/**/{pattern_glob}", recursive=True))

        if test_files:
            exit_code = pytest.main(test_files + ["-v"])
        else:
            exit_code = pytest.main(["./tests", "-v"])

        if exit_code != 0:
            sys.exit(exit_code)

    else:
        all_tests: typing.List[TestCase | TestSuite] = []
        for pattern_glob in patterns:
            tests = TestLoader().discover("./tests", pattern=pattern_glob)
            all_tests.extend(tests)

        result = TextTestRunner(verbosity=3).run(TestSuite(all_tests))
        if not result.wasSuccessful():
            sys.exit(1)

    coverage_.stop()

    try:
        echo("Coverage Summary:")
        coverage_.report()

        if save_report:
            coverage_.save()
            coverage_.html_report()

        coverage_.erase()

    except CoverageException as error:
        echo(error)
        sys.exit(1)


def validate_engines(engine: str) -> None:
    """
    Validates that the specified test engine is supported.

    Args:
        engine: The test engine name to validate.

    Raises:
        SystemExit: If the engine is not in the list of valid engines.

    Supported Engines:
        - 'unittest': Python's built-in unittest framework
        - 'pytest': Third-party pytest framework
    """

    _engines = ["unittest", "pytest"]
    if engine not in _engines:
        echo(f"Valid engines: {_engines}", err=True)
        sys.exit(1)
