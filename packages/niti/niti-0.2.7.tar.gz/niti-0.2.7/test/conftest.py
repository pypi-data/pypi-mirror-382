"""Pytest configuration for Niti tests."""

import os
import sys

# Add project root to Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# Import fixtures from test_utils to make them available globally


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (slower, broader scope)",
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests (very slow)"
    )
