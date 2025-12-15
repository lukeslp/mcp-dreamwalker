# Changelog

All notable changes to Dreamwalker MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20

### Added
- Initial release of Dreamwalker MCP server
- 31+ MCP tools across 5 categories:
  - LLM Provider Tools (5): create_provider, list_provider_models, chat_completion, generate_image, analyze_image
  - Data Fetching Tools (8): dream_of_census_acs, dream_of_census_saipe, dream_of_arxiv, dream_of_semantic_scholar, dream_of_wayback, and more
  - Caching Tools (7): cache_get, cache_set, cache_delete, cache_increment, cache_exists, cache_clear_namespace, cache_list_keys
  - Utility Tools (4): parse_document, multi_provider_search, format_citation_bibtex, format_citation_apa
  - Orchestration Tools (7+): dream_research, dream_search, dreamwalker_status, dreamwalker_cancel, dreamwalker_patterns, and more
- Support for 14 LLM providers:
  - Anthropic (Claude Sonnet 4.5, Haiku)
  - OpenAI (GPT-4o, GPT-4o-mini, DALL-E-3)
  - xAI (Grok-3, Grok-4-fast, Aurora)
  - Mistral, Cohere, Gemini, Perplexity, Groq, HuggingFace, Manus, ElevenLabs
- Integration with 12 data sources:
  - Census Bureau (ACS demographics, SAIPE poverty estimates)
  - arXiv (academic paper search)
  - Semantic Scholar (research papers)
  - Wayback Machine (web archive snapshots)
  - 8 additional sources available but not yet exposed (GitHub, YouTube, Wikipedia, News, Weather, NASA, Finance, OpenLibrary)
- Redis caching infrastructure:
  - Key-value storage with TTL support
  - Namespace isolation for multi-tenancy
  - Atomic operations (increment, etc.)
- Document parsing support:
  - 50+ file formats including PDF, DOCX, Excel, PPT, code files, Jupyter notebooks
  - Text extraction and optional metadata
- Orchestration workflows:
  - Dream Cascade (Beltalowda pattern): Hierarchical 3-tier research with 8-15 agents
  - Dream Swarm: Multi-agent domain-specific search with 5-20 agents
  - Real-time streaming via SSE
  - Webhook notifications with HMAC signatures
- stdio server for local MCP integration with Cursor and Claude Code
- HTTP server with Gunicorn for production deployment
- Comprehensive cost tracking and observability
- Configuration templates for Cursor and Claude Code
- User guide and documentation

### Technical Features
- Async/await support throughout
- Type hints for better IDE integration
- Comprehensive error handling
- Logging infrastructure
- Prometheus-compatible metrics export
- Import error fixes for better module loading
- Hybrid import patterns (relative and absolute)

### Documentation
- USER_GUIDE.md with complete tool documentation
- README.md with quick start instructions
- CURSOR_INTEGRATION.md for Cursor IDE setup
- CLAUDE_CODE_SETUP.md for Claude Code setup
- MCP_USAGE_GUIDE.md with usage examples
- This CHANGELOG.md

### Known Limitations
- Only 8 of 12 data sources currently exposed via MCP tools (remaining 4 implemented but not tooled yet)
- Chat completion doesn't support streaming responses (returns full response only)
- TTS tools (ElevenLabs) not yet exposed
- Embeddings generation not yet available as tool
- Vision utilities (image manipulation) not yet exposed
- No distributed tracing yet (OpenTelemetry integration planned)

### Dependencies
- Python 3.8+
- Flask for HTTP server
- Gunicorn for production WSGI
- Redis for caching
- Multiple LLM provider SDKs (anthropic, openai, mistralai, cohere, google-generativeai, etc.)
- Document parsing libraries (PyPDF2, python-docx, openpyxl, etc.)
- Various data fetching dependencies (requests, arxiv, etc.)

### Configuration
- Environment-based API key management
- Support for .env files
- Configurable via JSON for Cursor/Claude Code
- Service manager integration for systemd/process management

### Security
- API keys via environment variables only
- No secrets in code or logs
- HMAC webhook signatures
- Input validation on all tools

## [Unreleased]

### Planned for 1.1.0
- Streaming chat completion support
- TTS tool exposure (ElevenLabs)
- Embeddings generation tool
- Additional data source tools (GitHub, YouTube, Wikipedia, News, Weather, NASA, Finance, OpenLibrary)
- Vision utility tools (image manipulation, format conversion)
- Enhanced metadata for all tools (cost estimates, execution time)
- MCP Resources expansion (tool catalog, provider status, config endpoints)
- Integration test suite
- Performance benchmarks

### Planned for 1.2.0
- Content Generation Orchestrator (iterative document creation)
- OSINT Orchestrator (intelligence gathering with ethical constraints)
- Meta-orchestrator (tools that create tools)
- Advanced monitoring (distributed tracing, performance profiling)
- Plugin marketplace infrastructure

### Planned for 2.0.0
- Plugin marketplace with discovery service
- Plugin verification and sandboxing
- Tool composition/chaining engine
- Pattern templates library
- Smart tool recommendations
- Cost optimization engine
- Multi-tenant support with quotas
- Role-based access control

---

**Maintained by:** Luke Steuber  
**Repository:** https://github.com/yourusername/dreamwalker-mcp  
**License:** MIT

