#!/usr/bin/env python3
"""Test runner for Niti test suite."""

import argparse
import subprocess
import sys


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests based on type."""
    cmd = ["pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(
            ["--cov=niti", "--cov-report=html", "--cov-report=term-missing"]
        )

    if test_type == "unit":
        cmd.extend(["-m", "unit", "test/unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "test/integration"])
    elif test_type == "all":
        cmd.append("test/")
    else:
        print(f"Unknown test type: {test_type}")
        return 1

    print(f"Running command: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Niti tests")
    parser.add_argument(
        "type",
        choices=["all", "unit", "integration"],
        default="all",
        nargs="?",
        help="Type of tests to run",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Generate coverage report"
    )

    args = parser.parse_args()

    return run_tests(args.type, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
