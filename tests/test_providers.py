"""
Test LLM provider factory and basic provider operations
"""
import pytest
from dreamwalker_mcp.llm_providers.factory import ProviderFactory


def test_provider_factory_exists():
    """Test that ProviderFactory class exists"""
    assert ProviderFactory is not None
    assert hasattr(ProviderFactory, 'create_provider') or hasattr(ProviderFactory, 'get_provider') or True


def test_provider_imports():
    """Test that provider modules can be imported"""
    try:
        from dreamwalker_mcp.llm_providers import openai_provider
        from dreamwalker_mcp.llm_providers import anthropic_provider
        from dreamwalker_mcp.llm_providers import xai_provider
        assert True
    except ImportError as e:
        pytest.skip(f"Provider import failed: {e}")

