# 🌊 Dreamwalker - What's Next?

**Current Status**: Phase 1 Complete ✅  
**Dreamwalker MCP v2.0.0**: Deployed and operational

---

## Immediate: Connect Cursor/Codex to Dreamwalker

### The Issue

You're SSH'd into your server where Dreamwalker is running, but Cursor can't detect it because:
- Dreamwalker runs on remote server (dr.eamer.dev:5060)
- Cursor expects local stdio MCP servers
- Need a bridge to connect them

### The Solution ✅

I've created **`mcp_http_bridge.py`** - a bridge that translates stdio ↔ HTTP

**Status**: ✅ Tested and working (returns all 26 tools)

### Setup Steps

1. **Add to Cursor settings**:

Find your Cursor settings (usually `~/.config/Cursor/User/settings.json` on Linux) and add:

```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/coolhand/shared/mcp/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ]
    }
  }
}
```

2. **Restart Cursor**

3. **Test**: Ask Cursor to "Search arXiv for papers about AI"

**Full instructions**: `CURSOR_SETUP_INSTRUCTIONS.md`

---

## Short-Term: Phase 2 Service Migrations (Week 2)

### Goal
Eliminate ~3,400 lines of duplicated orchestrator code by migrating services to use `shared/orchestration/`

### Services to Migrate

#### 1. **servers/studio/** (3 days)
**Current**: Local `core/swarm_orchestrator.py` (377 lines)  
**Target**: `from shared.orchestration import SwarmOrchestrator`

**Steps**:
- Update `blueprints/portal.py` imports
- Delete `core/swarm_orchestrator.py`
- Delete `core/tool_registry.py`
- Test swarm search functionality

#### 2. **servers/swarm/** (2 days)
**Current**: Local `core/core_registry.py` (450 lines)  
**Target**: `from shared.tools import ToolRegistry`

**Steps**:
- Update all registry imports
- Update provider usage
- Delete `core/core_registry.py`
- Test all modules load

#### 3. **servers/planner/** (3 days)
**Current**: Custom `LessonPlanOrchestrator` (2,050 lines)  
**Target**: Extend `BaseOrchestrator` + keep domain logic

**Steps**:
- Create new `lesson_orchestrator.py` extending BaseOrchestrator
- Move CEFR/WIDA logic to new class
- Update app.py imports
- Extensive testing (lesson generation workflow)

#### 4. **Update Tool Registry Usage** (1 day)
**Target**: All services use `shared.tools.ToolRegistry`

**Detailed instructions**: See `MIGRATION_ROADMAP.md` Phase 2

**Expected Savings**: ~3,400 lines eliminated

---

## Medium-Term: Phase 3 Projects Cleanup (Week 3)

### Goal
Archive duplicate projects, consolidate similar implementations

### Projects to Archive

1. **projects/beltalowda/task-swarm/** → Archive (duplicate)
2. **projects/swarm/belta_back/** → Delete (duplicate)
3. **projects/io/xai_swarm/** → Migrate to shared SwarmOrchestrator

### Consolidation Decision Needed

**servers/swarm/** vs **projects/io/** - Near-identical codebases

**Options**:
- A) Keep `servers/swarm` as canonical, archive `projects/io`
- B) Merge best features, consolidate into `servers/swarm`
- C) Repurpose `projects/io` for experimental features

**Recommendation**: Option A (simplest)

**Expected Savings**: ~1,600 lines eliminated

---

## Long-Term: Phase 4 Documentation & Testing (Week 4)

### Goal
Complete migration with comprehensive docs and tests

### Tasks

1. **Update Service READMEs** (1 day)
   - Add "Shared Library Integration" sections
   - Document migration from local to shared
   - Update setup instructions

2. **MCP Integration Examples** (1 day)
   - Expand `EXAMPLES.md` with new tools
   - Add Census, caching, utility examples
   - Python client patterns

3. **Integration Testing** (2 days)
   - Test suite for MCP tools
   - Service migration verification
   - End-to-end workflow tests

4. **Usage Patterns Documentation** (1 day)
   - Standard import patterns
   - Best practices
   - Common pitfalls

---

## Timeline Overview

### ✅ Phase 1: Complete (November 18)
- MCP server expansion
- 19 new tools added
- Dreamwalker branding
- **Status**: Deployed and operational

### ⏸️ Phase 2: Service Migrations (Week 2)
- **Estimate**: 7 days
- **Impact**: ~3,400 lines eliminated
- **Status**: Ready to begin

### ⏸️ Phase 3: Projects Cleanup (Week 3)
- **Estimate**: 2.5 days
- **Impact**: ~1,600 lines eliminated
- **Status**: Ready after Phase 2

### ⏸️ Phase 4: Docs & Testing (Week 4)
- **Estimate**: 5 days
- **Impact**: Complete documentation
- **Status**: Ready after Phase 3

**Total Project**: 22.5 days (~4.5 weeks)  
**Completed**: 8 days (Phase 1)  
**Remaining**: 14.5 days (Phases 2-4)

---

## Enhanced Features (Future Phases)

### Potential Additions

1. **Semantic Caching** (Phase 2+)
   - Vector similarity for LLM responses
   - Reduce API costs 30-50%
   - Requires sentence-transformers

2. **Census Variable Catalog** (Phase 2+)
   - Full variable search implementation
   - Autocomplete for variable codes
   - Better UX for Census tools

3. **Advanced Citation Extraction** (Phase 3+)
   - NLP-based citation detection
   - Multiple format support
   - Citation validation

4. **Rate Limiting** (Phase 3+)
   - Per-tool rate limits
   - User/session tracking
   - Prevent abuse

5. **Authentication** (Phase 4+)
   - API key authentication
   - Role-based access
   - Usage tracking

6. **Monitoring Dashboard** (Phase 4+)
   - Grafana dashboards
   - Tool usage metrics
   - Cost tracking

---

## Quick Wins After Cursor Connection

Once Cursor is connected to Dreamwalker, try these:

### 1. Research Workflow
```
"Use orchestrate_research to analyze the evolution of transformer 
architectures from 2017-2025 with 9 agents"
```

### 2. Academic Search
```
"Search arXiv for the 10 most recent papers about multimodal learning"
```

### 3. Data Analysis
```
"Fetch Census poverty data for all California counties in 2022"
```

### 4. Document Processing
```
"Parse the PDF at /path/to/document.pdf and extract the text"
```

### 5. Multi-Source Research
```
"Use multi_provider_search to research climate change impacts 
with 5 diverse queries"
```

---

## Decision Points

### Phase 2: Which Service to Migrate First?

**Recommendation**: Start with **studio** (lowest risk, medium impact)

**Rationale**:
- Clean codebase
- Already uses `shared.config`
- Clear orchestrator replacement
- Good test case for others

### Phase 3: servers/swarm vs projects/io?

**Recommendation**: Keep **servers/swarm**, archive **projects/io**

**Rationale**:
- servers/swarm is registered in service manager
- Has production deployment path
- Better documented
- Cleaner structure

---

## Success Criteria

### Phase 2 Success
- ✅ All services use shared orchestrators
- ✅ Zero local orchestrator files remain
- ✅ All services pass smoke tests
- ✅ ~3,400 lines eliminated

### Phase 3 Success
- ✅ Duplicate projects archived
- ✅ No orphaned references
- ✅ Archive documentation complete
- ✅ ~1,600 lines eliminated

### Phase 4 Success
- ✅ All service READMEs updated
- ✅ Integration tests comprehensive
- ✅ Usage patterns documented
- ✅ Project fully documented

---

## Your Next Action

### Immediate (Today)

**1. Connect Cursor to Dreamwalker**
- Follow `CURSOR_SETUP_INSTRUCTIONS.md`
- Add MCP config to Cursor
- Test connection

**2. Test Dreamwalker Tools**
- Try `search_arxiv` in Cursor
- Try `cache_set` / `cache_get`
- Try `orchestrate_research`

### This Week

**3. Plan Phase 2 Kickoff**
- Review `MIGRATION_ROADMAP.md` Phase 2
- Choose first service to migrate (studio recommended)
- Schedule migration time

### Next 2 Weeks

**4. Execute Phase 2 Migrations**
- Migrate studio (3 days)
- Migrate swarm (2 days)
- Migrate planner (3 days)
- Update tool registries (1 day)

---

## Resources

**Cursor Setup**: `CURSOR_SETUP_INSTRUCTIONS.md` ⭐ Start here  
**What to Migrate**: `MIGRATION_ROADMAP.md`  
**Tool Reference**: `QUICK_START.md`  
**Complete Status**: `DREAMWALKER_MCP_COMPLETE.md`  
**All Docs**: `INDEX.md`

---

## Questions to Consider

1. **Which service to migrate first?** (Recommend: studio)
2. **Keep servers/swarm or projects/io?** (Recommend: servers/swarm)
3. **Add semantic caching now or later?** (Recommend: Phase 3+)
4. **Need authentication on MCP?** (Recommend: Phase 4+)

---

**🌊 Dreamwalker is Ready**

**Immediate**: Connect Cursor (see `CURSOR_SETUP_INSTRUCTIONS.md`)  
**Short-term**: Begin Phase 2 migrations  
**Long-term**: Complete Phases 3-4

_The Dreamwalker awaits your command._ 🌊

