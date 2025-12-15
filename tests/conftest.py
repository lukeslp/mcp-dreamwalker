"""
Pytest configuration and fixtures for Dreamwalker MCP tests
"""
import os
import pytest
from pathlib import Path

# Set test environment variables
os.environ['TESTING'] = '1'

@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture
def mock_api_key():
    """Provide mock API key for testing"""
    return "test-api-key-12345"

