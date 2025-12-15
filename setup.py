"""
Setup configuration for Dreamwalker MCP Plugin

Author: Luke Steuber
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dreamwalker-mcp",
    version="1.0.0",
    author="Luke Steuber",
    author_email="luke@lukesteuber.com",
    description="Multi-agent orchestration and LLM provider abstraction via MCP protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukeslp/kernel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "python-dotenv>=1.0.0",
        "requests>=2.32.5",
        "aiohttp>=3.12.14",
    ],
    extras_require={
        # LLM Providers
        "anthropic": ["anthropic>=0.18.0"],
        "openai": ["openai>=1.0.0"],
        "xai": ["openai>=1.0.0"],
        "mistral": ["requests>=2.31.0"],
        "cohere": ["cohere>=5.0.0"],
        "gemini": ["google-generativeai>=0.3.0"],
        "perplexity": ["openai>=1.0.0"],
        "groq": ["groq>=0.4.0"],
        "huggingface": ["huggingface-hub>=0.19.0"],

        # Data utilities
        "arxiv": ["arxiv>=2.0.0"],
        "wikipedia": ["wikipedia>=1.4.0"],
        "youtube": ["google-api-python-client>=2.0.0"],

        # Utilities
        "tts": ["gtts>=2.5.0"],
        "citations": ["bibtexparser>=1.4.0"],
        "redis": ["redis>=5.0.0"],

        # Document generation
        "documents": [
            "reportlab>=4.0.0",
            "python-docx>=1.0.0",
            "markdown>=3.5.0",
        ],

        # Observability
        "telemetry": [
            "opentelemetry-api>=1.20.0",
            "opentelemetry-sdk>=1.20.0",
        ],

        # All optional dependencies
        "all": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
            "cohere>=5.0.0",
            "google-generativeai>=0.3.0",
            "groq>=0.4.0",
            "huggingface-hub>=0.19.0",
            "arxiv>=2.0.0",
            "wikipedia>=1.4.0",
            "google-api-python-client>=2.0.0",
            "gtts>=2.5.0",
            "bibtexparser>=1.4.0",
            "redis>=5.0.0",
            "reportlab>=4.0.0",
            "python-docx>=1.0.0",
            "markdown>=3.5.0",
            "opentelemetry-api>=1.20.0",
            "opentelemetry-sdk>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dreamwalker-unified=dreamwalker_mcp.mcp.stdio_servers.unified_stdio:main",
            "dreamwalker-providers=dreamwalker_mcp.mcp.stdio_servers.providers_stdio:main",
            "dreamwalker-data=dreamwalker_mcp.mcp.stdio_servers.data_stdio:main",
            "dreamwalker-cache=dreamwalker_mcp.mcp.stdio_servers.cache_stdio:main",
            "dreamwalker-utility=dreamwalker_mcp.mcp.stdio_servers.utility_stdio:main",
            "dreamwalker-websearch=dreamwalker_mcp.mcp.stdio_servers.web_search_stdio:main",
        ],
    },
)
