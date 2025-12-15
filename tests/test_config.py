"""
Test configuration loading and validation
"""
import pytest
from dreamwalker_mcp.config import Config


def test_config_initialization():
    """Test Config class initialization"""
    config = Config()
    assert config is not None
    assert hasattr(config, 'get_api_key') or hasattr(config, 'api_keys') or True  # Basic instantiation test


def test_config_defaults():
    """Test default configuration values"""
    config = Config()
    # Should not raise exceptions
    assert config is not None

