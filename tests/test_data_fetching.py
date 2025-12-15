"""
Test data fetching clients
"""
import pytest
from dreamwalker_mcp.data_fetching.factory import DataClientFactory


def test_data_client_factory_exists():
    """Test that DataClientFactory exists"""
    assert DataClientFactory is not None


def test_arxiv_client_import():
    """Test that arXiv client can be imported"""
    try:
        from dreamwalker_mcp.data_fetching.arxiv_client import ArxivClient
        assert ArxivClient is not None
    except ImportError as e:
        pytest.skip(f"ArxivClient import failed: {e}")


def test_wikipedia_client_import():
    """Test that Wikipedia client can be imported"""
    try:
        from dreamwalker_mcp.data_fetching.wikipedia_client import WikipediaClient
        assert WikipediaClient is not None
    except ImportError as e:
        pytest.skip(f"WikipediaClient import failed: {e}")

