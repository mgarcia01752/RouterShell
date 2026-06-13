#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""RouterShell unittest discovery runner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TestResult:
    """Container for individual test file results."""

    file_path: str
    tests_run: int
    failures: int
    errors: int
    skipped: int
    success: bool
    duration: float


@dataclass
class TestSummary:
    """Container for overall test execution summary."""

    total_files: int
    successful_files: int
    failed_files: int
    total_tests: int
    total_failures: int
    total_errors: int
    total_skipped: int
    total_duration: float
    results: list[TestResult]


class RouterShellTestRunner:
    """Discover and run unittest-compatible tests."""

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser."""
        parser = argparse.ArgumentParser(description="Run RouterShell unittest tests.")
        parser.add_argument("--tests-dir", default="tests", help="Directory containing tests.")
        parser.add_argument("--pattern", default="test_*.py", help="Test file pattern.")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
        parser.add_argument("--failfast", action="store_true", help="Stop on first failure.")
        parser.add_argument("--json-report", action="store_true", help="Write a JSON report.")
        parser.add_argument("--output-dir", default="test_reports", help="Report output directory.")
        return parser

    @staticmethod
    def _discover(tests_dir: Path, pattern: str) -> list[Path]:
        """Discover test files."""
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")
        return sorted(tests_dir.rglob(pattern))

    @staticmethod
    def _run_file(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run tests from one file."""
        start = time.time()
        loader = unittest.TestLoader()
        suite = loader.discover(str(path.parent), pattern=path.name)
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1, failfast=failfast)
        result = runner.run(suite)
        tests_run = result.testsRun
        errors = len(result.errors)
        failures = len(result.failures)

        if tests_run == 0:
            function_result = RouterShellTestRunner._run_function_tests(path, verbose, failfast)
            tests_run = function_result.tests_run
            errors = errors + function_result.errors
            failures = failures + function_result.failures

        return TestResult(
            file_path=str(path),
            tests_run=tests_run,
            failures=failures,
            errors=errors,
            skipped=len(result.skipped),
            success=failures == 0 and errors == 0,
            duration=time.time() - start,
        )

    @staticmethod
    def _run_function_tests(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run pytest-style module-level test functions without pytest."""
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            return TestResult(str(path), 0, 0, 1, 0, False, 0.0)

        module = importlib.util.module_from_spec(spec)
        project_root = Path.cwd()
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path = original_path

        functions = [
            value
            for name, value in vars(module).items()
            if name.startswith("test_") and callable(value)
        ]
        failures = 0
        errors = 0
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        for function in functions:
            try:
                function()
                if verbose:
                    print(f"PASS {function.__name__}")
            except AssertionError:
                failures = failures + 1
                traceback.print_exc()
                if failfast:
                    break
            except Exception:
                errors = errors + 1
                traceback.print_exc()
                if failfast:
                    break
        sys.path = original_path

        return TestResult(
            file_path=str(path),
            tests_run=len(functions),
            failures=failures,
            errors=errors,
            skipped=0,
            success=failures == 0 and errors == 0,
            duration=0.0,
        )

    @staticmethod
    def _write_json(summary: TestSummary, output_dir: Path) -> None:
        """Write a JSON test report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "total_files": summary.total_files,
                "successful_files": summary.successful_files,
                "failed_files": summary.failed_files,
                "total_tests": summary.total_tests,
                "total_failures": summary.total_failures,
                "total_errors": summary.total_errors,
                "total_skipped": summary.total_skipped,
                "total_duration": summary.total_duration,
            },
            "results": [result.__dict__ for result in summary.results],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report generated: {output_path}")

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Run discovered tests and return a process status."""
        tests_dir = Path(options.tests_dir)
        start = time.time()
        test_files = RouterShellTestRunner._discover(tests_dir, options.pattern)
        if not test_files:
            print(f"No test files found matching {options.pattern!r} in {tests_dir}.")
            return 1

        results: list[TestResult] = []
        for path in test_files:
            print(f"Running {path}...")
            result = RouterShellTestRunner._run_file(path, options.verbose, options.failfast)
            results.append(result)
            if options.failfast and not result.success:
                break

        summary = TestSummary(
            total_files=len(results),
            successful_files=sum(1 for result in results if result.success),
            failed_files=sum(1 for result in results if not result.success),
            total_tests=sum(result.tests_run for result in results),
            total_failures=sum(result.failures for result in results),
            total_errors=sum(result.errors for result in results),
            total_skipped=sum(result.skipped for result in results),
            total_duration=time.time() - start,
            results=results,
        )

        print("\nTest summary")
        print(f"Files: {summary.successful_files}/{summary.total_files} passed")
        print(f"Tests: {summary.total_tests - summary.total_failures - summary.total_errors}/{summary.total_tests} passed")
        print(f"Failures: {summary.total_failures}")
        print(f"Errors: {summary.total_errors}")
        print(f"Skipped: {summary.total_skipped}")
        print(f"Duration: {summary.total_duration:.3f}s")

        if options.json_report:
            RouterShellTestRunner._write_json(summary, Path(options.output_dir))

        return 0 if summary.failed_files == 0 else 1


def main() -> int:
    """Run the RouterShell unittest runner."""
    parser = RouterShellTestRunner._build_parser()
    try:
        return RouterShellTestRunner.run(parser.parse_args())
    except KeyboardInterrupt:
        print("Test execution interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
