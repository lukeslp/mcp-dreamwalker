"""
Dreamwalker MCP Plugin

Multi-agent orchestration and LLM provider abstraction via MCP protocol.

Features:
- Beltalowda hierarchical research orchestration
- Swarm multi-agent search orchestration
- 9 LLM providers (Anthropic, OpenAI, xAI, Mistral, Cohere, Gemini, Perplexity, Groq, HuggingFace)
- 29+ tool modules for data fetching and processing
- Redis-based caching and state management
- ArXiv, Semantic Scholar, Wikipedia, YouTube, and more

Author: Luke Steuber
License: MIT
"""

__version__ = "1.0.0"

from .config import ConfigManager

__all__ = ["ConfigManager"]
