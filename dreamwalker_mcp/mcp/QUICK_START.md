# 🌊 Dreamwalker MCP Server - Quick Start

**Version**: 2.0.0 | **Status**: ✅ Operational | **Port**: 5060

---

## What is Dreamwalker?

**Dreamwalker** is the master MCP orchestrator providing:
- **26 Tools** across orchestration, data, cache, utilities
- **9 Resources** for metadata and catalogs
- **Real-time SSE streaming** for long-running workflows
- **Production deployment** at https://dr.eamer.dev/mcp/

---

## Quick Commands

### Service Control
```bash
sm start mcp-server      # Start Dreamwalker
sm restart mcp-server    # Restart
sm status mcp-server     # Check status
sm logs mcp-server       # View logs
```

### Health Check
```bash
curl localhost:5060/              # Server info
curl localhost:5060/health        # Health status
curl localhost:5060/tools         # List all 26 tools
curl localhost:5060/resources     # List all 9 resources
```

---

## Tool Categories

### Orchestration (7 tools)
- `orchestrate_research` - Beltalowda hierarchical research
- `orchestrate_search` - Swarm multi-agent search
- `get_orchestration_status` - Check workflow status
- `cancel_orchestration` - Cancel workflow
- `list_orchestrator_patterns` - List patterns
- `list_registered_tools` - Query tool registry
- `execute_registered_tool` - Execute registered tool

### Data Fetching (8 tools) 🆕
- `fetch_census_acs` - Census demographics
- `fetch_census_saipe` - Poverty estimates
- `list_census_variables` - Variable search
- `search_arxiv` - arXiv papers
- `search_semantic_scholar` - Research papers
- `get_semantic_scholar_paper` - Paper details
- `wayback_search` - Archive snapshots
- `wayback_available_snapshots` - List snapshots

### Caching (7 tools) 🆕
- `cache_get` - Retrieve value
- `cache_set` - Store value with TTL
- `cache_delete` - Delete key
- `cache_increment` - Increment counter
- `cache_exists` - Check existence
- `cache_expire` - Set TTL
- `cache_list_keys` - List by pattern

### Utilities (4 tools) 🆕
- `parse_document` - Parse 50+ file formats
- `multi_provider_search` - Multi-query research
- `extract_citations` - Extract citations
- `format_citation_bibtex` - BibTeX formatting

---

## Usage Examples

### Orchestrate Research
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research quantum computing applications",
    "num_agents": 9,
    "generate_documents": true
  }'
```

### Search arXiv
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/search_arxiv \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformers NLP",
    "max_results": 5,
    "category": "cs.CL"
  }'
```

### Cache Data
```bash
# Set
curl -X POST https://dr.eamer.dev/mcp/tools/cache_set \
  -H "Content-Type: application/json" \
  -d '{"key": "config", "value": {"theme": "dark"}, "ttl": 3600}'

# Get
curl -X POST https://dr.eamer.dev/mcp/tools/cache_get \
  -H "Content-Type: application/json" \
  -d '{"key": "config"}'
```

### Parse Document
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/parse_document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'
```

---

## Documentation

| File | Purpose |
|------|---------|
| **DREAMWALKER_MCP_COMPLETE.md** | Master summary (this overview) |
| **README.md** | Full MCP documentation |
| **MCP_EVALUATION_REPORT.md** | Analysis and findings |
| **MIGRATION_ROADMAP.md** | 4-phase migration plan |
| **DEPLOYMENT_VERIFIED.md** | Deployment confirmation |
| **IMPLEMENTATION_SUMMARY.md** | Implementation details |

---

## Next Steps

### Immediate
- ✅ Phase 1 deployed
- ⏸️ Monitor for issues
- ⏸️ Test additional tools

### Phase 2 (Next 2 Weeks)
- Migrate studio to shared orchestrators
- Migrate swarm to shared orchestrators
- Refactor planner orchestrator
- **Expected**: ~3,400 lines eliminated

### Phase 3-4 (Weeks 3-4)
- Archive duplicate projects
- Update documentation
- Add integration tests

---

## Support

**Logs**: `~/.service_manager/logs/mcp-server.log`  
**Docs**: `/home/coolhand/shared/mcp/`  
**Service**: `sm status mcp-server`

---

**🌊 Dreamwalker - Master Orchestrator**  
**Ready for service migrations and further expansion**

