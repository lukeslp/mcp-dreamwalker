# 🌊 Dreamwalker MCP Server - Documentation Index

**Version**: 2.0.0  
**Status**: ✅ Operational  
**Last Updated**: November 18, 2025

---

## 🎯 Start Here

**New to Dreamwalker?** → [QUICK_START.md](QUICK_START.md)  
**Just deployed?** → [DEPLOYMENT_VERIFIED.md](DEPLOYMENT_VERIFIED.md)  
**Want the big picture?** → [DREAMWALKER_MCP_COMPLETE.md](DREAMWALKER_MCP_COMPLETE.md)

---

## 📚 Documentation Structure

### Core Documentation

1. **[README.md](README.md)** - Main MCP server documentation
   - Overview and architecture
   - Integration options (Codex, HTTP)
   - API reference
   - Configuration and deployment
   - **Start here for comprehensive overview**

2. **[QUICK_START.md](QUICK_START.md)** - Quick reference card
   - Essential commands
   - Tool categories
   - Usage examples
   - **Start here for immediate usage**

3. **[DREAMWALKER_MCP_COMPLETE.md](DREAMWALKER_MCP_COMPLETE.md)** - Master summary
   - Dreamwalker concept
   - Complete implementation status
   - Architecture overview
   - **Start here for project overview**

### Implementation Documentation

4. **[MCP_EVALUATION_REPORT.md](MCP_EVALUATION_REPORT.md)** - Comprehensive analysis
   - Current MCP implementation review
   - Gap analysis (what's not in MCP)
   - Code duplication audit (~5,000 lines identified)
   - Consolidation recommendations
   - **Read for understanding the before/after state**

5. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details
   - Files created/modified
   - Tool coverage breakdown
   - Migration opportunities
   - Success metrics
   - **Read for technical implementation details**

6. **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - Phase 1 completion
   - Deployment instructions
   - Verification checklist
   - Dependencies list
   - **Read before/after deployment**

7. **[DEPLOYMENT_VERIFIED.md](DEPLOYMENT_VERIFIED.md)** - Deployment confirmation
   - Verification test results
   - Functional testing
   - Access points
   - Troubleshooting
   - **Read to confirm successful deployment**

### Migration Documentation

8. **[MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md)** - Complete migration plan
   - Phase 1: MCP Expansion ✅ (complete)
   - Phase 2: Service Migrations (studio, swarm, planner)
   - Phase 3: Projects Cleanup (archives, consolidation)
   - Phase 4: Documentation & Testing
   - Step-by-step instructions for each phase
   - **Essential for implementing Phases 2-4**

9. **[APP_INTEGRATION_GUIDE.md](APP_INTEGRATION_GUIDE.md)** - App.py integration
   - Step-by-step integration of new servers
   - Route definitions
   - Testing procedures
   - **Used during Phase 1 implementation**

### Historical/Conceptual Documentation

10. **[MCP_SERVER_CONCEPT.md](../MCP_SERVER_CONCEPT.md)** - Original concept
    - Initial vision for MCP server
    - Tool categories planned
    - Architecture concepts
    - **Historical reference**

11. **[MCP_IMPLEMENTATION.md](../MCP_IMPLEMENTATION.md)** - Original implementation guide
    - providers_server.py documentation
    - Usage examples
    - Integration patterns
    - **Historical reference**

### Technical Documentation

12. **[API.md](API.md)** - Complete API reference
    - All endpoints documented
    - Request/response formats
    - Error codes

13. **[EXAMPLES.md](EXAMPLES.md)** - Usage examples
    - Academic research example
    - Multi-platform search
    - Python client with SSE

14. **[CODEX_INTEGRATION.md](CODEX_INTEGRATION.md)** - Codex/Claude Code setup
    - stdio bridge configuration
    - Usage examples

---

## 📖 Reading Paths

### For Quick Usage
```
QUICK_START.md
→ Use the server immediately
```

### For Understanding the Project
```
DREAMWALKER_MCP_COMPLETE.md
→ MCP_EVALUATION_REPORT.md
→ README.md
→ Comprehensive understanding
```

### For Implementing Migrations
```
MIGRATION_ROADMAP.md (Phase 2)
→ Follow step-by-step for each service
```

### For Troubleshooting Deployment
```
DEPLOYMENT_VERIFIED.md
→ PHASE1_COMPLETE.md
→ APP_INTEGRATION_GUIDE.md
→ Resolve deployment issues
```

---

## 🗂️ File Organization

### Production Code
```
mcp/
├── app.py                    # Main Flask application
├── unified_server.py         # Orchestration tools
├── data_server.py           # Data fetching tools 🆕
├── cache_server.py          # Caching tools 🆕
├── utility_server.py        # Utility tools 🆕
├── providers_server.py      # Provider tools (separate)
├── streaming.py             # SSE support
├── tool_registry.py         # Tool registration
└── background_loop.py       # Async tasks
```

### Documentation
```
mcp/
├── INDEX.md                           # This file
├── README.md                          # Main documentation
├── QUICK_START.md                     # Quick reference
├── DREAMWALKER_MCP_COMPLETE.md       # Master summary
├── MCP_EVALUATION_REPORT.md          # Analysis
├── MIGRATION_ROADMAP.md              # Migration plan
├── IMPLEMENTATION_SUMMARY.md         # Implementation
├── PHASE1_COMPLETE.md                # Phase 1 completion
├── DEPLOYMENT_VERIFIED.md            # Deployment verification
├── APP_INTEGRATION_GUIDE.md          # Integration guide
├── API.md                            # API reference
├── EXAMPLES.md                       # Usage examples
└── CODEX_INTEGRATION.md              # Codex setup
```

---

## 🔍 Quick Lookup

### "How do I..."

**Start the server?**  
→ [QUICK_START.md](QUICK_START.md) - Service Control section

**Use a specific tool?**  
→ [QUICK_START.md](QUICK_START.md) - Usage Examples section  
→ [README.md](README.md) - API Reference section

**Migrate my service to shared orchestrators?**  
→ [MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md) - Phase 2

**Understand what tools are available?**  
→ [DREAMWALKER_MCP_COMPLETE.md](DREAMWALKER_MCP_COMPLETE.md) - Tools Implemented section  
→ [API.md](API.md) - Complete reference

**Troubleshoot deployment issues?**  
→ [DEPLOYMENT_VERIFIED.md](DEPLOYMENT_VERIFIED.md) - Troubleshooting section  
→ [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Testing Checklist

**See what changed?**  
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Changes section  
→ [DEPLOYMENT_VERIFIED.md](DEPLOYMENT_VERIFIED.md) - Changelog

---

## 📊 Key Statistics

- **Tools**: 26 (7 orchestration + 8 data + 7 cache + 4 utility)
- **Resources**: 9 (2 orchestrator + 3 data + 2 cache + 2 utility)
- **Servers**: 4 (orchestration, data, cache, utility)
- **Documentation**: 13 files
- **Code**: 1,770 lines (new servers)
- **Docs**: 3,408 lines (new documentation)

---

## 🚀 Common Tasks

### Test arXiv Search
```bash
curl -X POST http://localhost:5060/tools/search_arxiv \
  -H "Content-Type: application/json" \
  -d '{"query": "AI safety", "max_results": 5}'
```

### Use Cache
```bash
# Set
curl -X POST http://localhost:5060/tools/cache_set \
  -d '{"key": "test", "value": "hello", "ttl": 60}'

# Get
curl -X POST http://localhost:5060/tools/cache_get \
  -d '{"key": "test"}'
```

### Parse Document
```bash
curl -X POST http://localhost:5060/tools/parse_document \
  -d '{"file_path": "/path/to/doc.pdf"}'
```

### Orchestrate Research
```bash
curl -X POST http://localhost:5060/tools/orchestrate_research \
  -d '{"task": "AI alignment", "num_agents": 9}'
```

---

## 🔗 External Links

- **Production**: https://dr.eamer.dev/mcp/
- **Health**: https://dr.eamer.dev/mcp/health
- **Tools**: https://dr.eamer.dev/mcp/tools
- **Logs**: ~/.service_manager/logs/mcp-server.log

---

## 📞 Support

**Questions?** See [README.md](README.md) or [DEPLOYMENT_VERIFIED.md](DEPLOYMENT_VERIFIED.md)  
**Issues?** Check `sm logs mcp-server`  
**Migrations?** See [MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md)

---

**🌊 Dreamwalker v2.0.0 - Master Orchestrator**

