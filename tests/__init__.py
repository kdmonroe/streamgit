"""StreamGit Test Suite

Contains test fixtures and configuration for pytest.
Includes tests for both CLI and web interface components.
"""

import pytest
from pathlib import Path

# Define test data directory
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / 'fixtures'

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "cli: mark test as a CLI test"
    )
    config.addinivalue_line(
        "markers",
        "web: mark test as a web interface test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as requiring GitHub API access"
    )

# Common fixtures
@pytest.fixture
def mock_token():
    """Provide a mock GitHub token for testing"""
    return "mock_github_token_for_testing"

@pytest.fixture
def sample_repo_data():
    """Provide sample repository data for testing"""
    return {
        "name": "test-repo",
        "description": "Test repository",
        "private": False
    }

