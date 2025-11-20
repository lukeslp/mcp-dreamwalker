# MCP Integration Migration Roadmap

**Version**: 1.0  
**Date**: November 18, 2025  
**Status**: Ready for Implementation

---

## Overview

This roadmap provides step-by-step instructions for migrating services from duplicated code to the centralized shared library with MCP integration.

---

## Phase 1: MCP Server Expansion (Week 1)

**Goal**: Add data_fetching, utils, and memory/cache tools to MCP server

### Task 1.1: Implement Data Fetching Server

**File**: `shared/mcp/data_server.py`

**Tools to Implement (8):**
1. `fetch_census_acs` - Fetch ACS demographic data
2. `fetch_census_saipe` - Fetch poverty estimates
3. `list_census_variables` - Search Census variable catalog
4. `search_arxiv` - Search arXiv papers
5. `search_semantic_scholar` - Search research papers
6. `get_semantic_scholar_paper` - Get paper details
7. `wayback_search` - Search Wayback Machine
8. `wayback_available_snapshots` - List available snapshots

**Resources to Implement (3):**
- `census://variables/{table}`
- `arxiv://category/{category}`
- `archive://snapshot/{url}/{timestamp}`

**Dependencies:**
- `shared.data_fetching.CensusClient`
- `shared.data_fetching.arxiv_client`
- `shared.data_fetching.semantic_scholar`
- `shared.data_fetching.archive_client`

**Testing:**
```bash
# Test Census API
curl -X POST http://localhost:5060/mcp/tools/fetch_census_acs \
  -H "Content-Type: application/json" \
  -d '{"year": 2022, "variables": {"B01003_001E": "population"}}'

# Test arXiv search
curl -X POST http://localhost:5060/mcp/tools/search_arxiv \
  -H "Content-Type: application/json" \
  -d '{"query": "transformers", "max_results": 5}'
```

**Estimated Time**: 2 days

### Task 1.2: Implement Cache Server

**File**: `shared/mcp/cache_server.py`

**Tools to Implement (7):**
1. `cache_get` - Retrieve cached value
2. `cache_set` - Store value with TTL
3. `cache_delete` - Delete key
4. `cache_increment` - Increment counter
5. `cache_list_keys` - List keys by pattern
6. `semantic_cache_lookup` - Find similar cached prompts
7. `semantic_cache_store` - Store LLM response with embedding

**Resources to Implement (2):**
- `cache://stats` - Cache statistics
- `cache://keys/{namespace}` - List namespace keys

**Dependencies:**
- `shared.memory.RedisManager`
- `shared.utils.embeddings` (for semantic cache)

**Enhancements to memory/__init__.py:**
```python
class RedisManager:
    # Add semantic caching methods
    def semantic_lookup(self, prompt, model, threshold=0.95):
        """Find semantically similar cached responses"""
        
    def semantic_store(self, prompt, model, response, metadata=None):
        """Store response with embedding for semantic search"""
```

**Testing:**
```bash
# Test basic cache
curl -X POST http://localhost:5060/mcp/tools/cache_set \
  -H "Content-Type: application/json" \
  -d '{"key": "test", "value": "hello", "ttl": 60}'

# Test semantic cache
curl -X POST http://localhost:5060/mcp/tools/semantic_cache_store \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?", "model": "grok-3", "response": "..."}'
```

**Estimated Time**: 2 days

### Task 1.3: Implement Utility Server

**File**: `shared/mcp/utility_server.py`

**Tools to Implement (10):**
1. `multi_provider_search` - Search across multiple providers
2. `extract_citations` - Extract citations from text
3. `parse_document` - Parse document (auto-detect format)
4. `extract_text_from_pdf` - PDF text extraction
5. `extract_text_from_docx` - DOCX text extraction
6. `extract_text_from_txt` - TXT text extraction
7. `generate_text_embedding` - Generate text embedding
8. `compute_similarity` - Compute text similarity
9. `analyze_image_vision` - Image analysis with vision
10. `text_to_speech` - Generate speech audio

**Dependencies:**
- `shared.utils.multi_search`
- `shared.utils.citation`
- `shared.utils.document_parsers`
- `shared.utils.embeddings`
- `shared.utils.vision`
- `shared.utils.tts`

**Testing:**
```bash
# Test document parsing
curl -X POST http://localhost:5060/mcp/tools/parse_document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/doc.pdf"}'

# Test multi-search
curl -X POST http://localhost:5060/mcp/tools/multi_provider_search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI safety", "providers": ["arxiv", "semantic_scholar"]}'
```

**Estimated Time**: 3 days

### Task 1.4: Update MCP App Integration

**File**: `shared/mcp/app.py`

**Changes:**
```python
from .data_server import DataServer
from .cache_server import CacheServer
from .utility_server import UtilityServer

# Initialize all servers
data_server = DataServer(config_manager=config)
cache_server = CacheServer(config_manager=config)
utility_server = UtilityServer(config_manager=config)

# Register all tools
@app.route('/tools', methods=['GET'])
def list_tools():
    tools = []
    tools.extend(providers_server.get_tools_manifest())
    tools.extend(unified_server.get_tools_manifest())
    tools.extend(data_server.get_tools_manifest())      # NEW
    tools.extend(cache_server.get_tools_manifest())     # NEW
    tools.extend(utility_server.get_tools_manifest())   # NEW
    return jsonify(tools)

# Register all tool endpoints
# ... add routes for each tool ...
```

**Testing:**
```bash
# Verify all tools listed
curl http://localhost:5060/mcp/tools | jq '.[] | .name'

# Should show 30+ tools
```

**Estimated Time**: 1 day

**Phase 1 Total**: 8 days

---

## Phase 2: Service Migrations (Week 2)

### Task 2.1: Migrate Studio to Shared Orchestrators

**Service**: `servers/studio/`

**Current State:**
- Local `core/swarm_orchestrator.py` (377 lines)
- Local `core/tool_registry.py` (~400 lines)
- Uses `shared.config.ConfigManager` ✅

**Migration Steps:**

1. **Update imports in `blueprints/portal.py`:**

```python
# BEFORE
from core.swarm_orchestrator import SwarmOrchestrator, SwarmResult

# AFTER
from shared.orchestration import SwarmOrchestrator, SwarmConfig
from shared.orchestration.models import OrchestratorResult
```

2. **Update orchestrator initialization:**

```python
# BEFORE
orchestrator = SwarmOrchestrator(
    main_model="grok-3",
    mini_model="grok-3-mini",
    api_key=api_key
)

# AFTER
from shared.llm_providers import ProviderFactory

provider = ProviderFactory.get_provider('xai')
config = SwarmConfig(
    num_agents=5,
    parallel_execution=True
)
orchestrator = SwarmOrchestrator(
    config=config,
    provider=provider
)
```

3. **Update tool registry imports:**

```python
# BEFORE
from core.tool_registry import ToolRegistry

# AFTER
from shared.tools import ToolRegistry
```

4. **Delete obsolete files:**

```bash
rm servers/studio/core/swarm_orchestrator.py
rm servers/studio/core/tool_registry.py
```

5. **Update requirements.txt:**

```txt
# Add if not already present
-e /home/coolhand/shared
```

6. **Test:**

```bash
cd servers/studio
python app.py
# Verify swarm search works
```

**Files Modified:**
- `blueprints/portal.py`
- `blueprints/hive.py`
- `app.py`
- `requirements.txt`

**Files Deleted:**
- `core/swarm_orchestrator.py`
- `core/tool_registry.py`

**Estimated Time**: 1 day  
**Risk**: Medium (requires testing)

### Task 2.2: Migrate Swarm to Shared Orchestrators

**Service**: `servers/swarm/`

**Current State:**
- Uses `core/core_registry.py` (~450 lines)
- Old provider adapters in `providers/swarm_adapters.py`
- Custom config in `core/core_config.py.old`

**Migration Steps:**

1. **Update registry imports throughout:**

```bash
# Find all imports
grep -r "from core.core_registry" servers/swarm/

# Replace with
from shared.tools import ToolRegistry
```

2. **Update provider usage:**

```python
# BEFORE
from providers.swarm_adapters import get_provider

# AFTER
from shared.llm_providers import ProviderFactory
provider = ProviderFactory.get_provider('xai')
```

3. **Update config:**

```python
# BEFORE
from core.core_config import Config

# AFTER
from shared.config import ConfigManager
config = ConfigManager(app_name='swarm')
```

4. **Delete obsolete files:**

```bash
rm servers/swarm/core/core_registry.py
rm servers/swarm/providers/swarm_adapters.py
rm servers/swarm/core/core_config.py.old
```

5. **Test:**

```bash
cd servers/swarm
python app.py
# Verify all modules load
```

**Files Modified:**
- `app.py`
- `core/core_web.py`
- `core/core_agent.py`
- `core/core_cli.py`
- All `hive/*.py` modules
- `requirements.txt`

**Files Deleted:**
- `core/core_registry.py`
- `providers/swarm_adapters.py`
- `core/core_config.py.old`

**Estimated Time**: 2 days  
**Risk**: Medium (many files to update)

### Task 2.3: Migrate Planner Orchestrator

**Service**: `servers/planner/`

**Current State:**
- Custom `LessonPlanOrchestrator` (2,050 lines)
- Domain-specific logic (CEFR, WIDA frameworks)
- Tightly coupled to XAI client

**Migration Strategy**: ⚠️ **Refactor to Extend BaseOrchestrator**

**Steps:**

1. **Keep domain logic, extract orchestration pattern:**

```python
# NEW: servers/planner/core/lesson_orchestrator.py
from shared.orchestration import BaseOrchestrator, SubTask, AgentResult
from shared.llm_providers import ProviderFactory

class LessonPlanOrchestrator(BaseOrchestrator):
    """
    Lesson planning orchestrator.
    
    Extends BaseOrchestrator with lesson-specific decomposition,
    execution, and synthesis logic.
    """
    
    def __init__(self, cefr_level=None, topic_area=None, **kwargs):
        super().__init__(**kwargs)
        self.cefr_level = cefr_level
        self.topic_area = topic_area
    
    async def decompose_task(self, task, context):
        """
        Break lesson idea into subtasks.
        
        Uses CEFR/WIDA frameworks for objective alignment.
        """
        # Keep existing decomposition logic
        # Returns List[SubTask]
    
    async def execute_subtask(self, subtask, context):
        """
        Generate individual lesson artifacts.
        
        Artifacts: outline, handout, video script, assessments
        """
        # Keep existing artifact generation
        # Returns AgentResult
    
    async def synthesize_results(self, agent_results, context):
        """
        Synthesize final lesson plan from artifacts.
        """
        # Keep existing synthesis logic
        # Returns final lesson plan
```

2. **Benefits of refactoring:**
- Inherits workflow orchestration from BaseOrchestrator
- Gets document generation for free
- Automatically gets MCP integration
- Reduces code from 2,050 → ~800 lines

3. **Update imports in `app.py`:**

```python
from core.lesson_orchestrator import LessonPlanOrchestrator
from shared.llm_providers import ProviderFactory

provider = ProviderFactory.get_provider('xai')
orchestrator = LessonPlanOrchestrator(
    cefr_level=cefr_level,
    topic_area=topic_area,
    provider=provider
)
```

**Files Modified:**
- `core/orchestrator.py` → `core/lesson_orchestrator.py` (refactored)
- `app.py`
- `requirements.txt`

**Estimated Time**: 3 days  
**Risk**: High (significant refactoring, extensive testing needed)

### Task 2.4: Update Tool Registry Usage Across All Services

**Services**: studio, swarm, planner, io

**Standard Pattern:**

```python
# In app.py or main module
from shared.tools import ToolRegistry

# Get singleton instance
registry = ToolRegistry.get_instance()

# Register tools
registry.register_tool(
    name='my_tool',
    schema={...},
    handler=my_function,
    module_name='my_module'
)

# Get enabled tools
tools = registry.get_enabled_tools()
```

**Find & Replace:**

```bash
# Studio
sed -i 's/from core.tool_registry/from shared.tools/g' servers/studio/**/*.py

# Swarm
sed -i 's/from core.core_registry/from shared.tools/g' servers/swarm/**/*.py
sed -i 's/CoreRegistry/ToolRegistry/g' servers/swarm/**/*.py

# IO
sed -i 's/from core.core_registry/from shared.tools/g' projects/io/**/*.py
```

**Estimated Time**: 1 day (all services)  
**Risk**: Low (well-defined API)

**Phase 2 Total**: 7 days

---

## Phase 3: Projects Cleanup (Week 3)

### Task 3.1: Archive Duplicate Beltalowda Projects

**Projects to Archive:**

1. `projects/beltalowda/task-swarm/`
2. `projects/swarm/belta_back/`

**Steps:**

```bash
# Create archive directory
mkdir -p projects/.archive/beltalowda-duplicates/

# Move projects
mv projects/beltalowda/task-swarm/ projects/.archive/beltalowda-duplicates/task-swarm-1/
mv projects/swarm/belta_back/ projects/.archive/beltalowda-duplicates/belta-back/

# Create archive README
cat > projects/.archive/beltalowda-duplicates/README.md << 'EOF'
# Archived Beltalowda Duplicates

**Archived**: November 2025  
**Reason**: Replaced by shared/orchestration/beltalowda_orchestrator.py

These projects were early implementations of the Beltalowda orchestrator
pattern. All functionality has been consolidated into the shared library.

**To use Beltalowda orchestration:**
```python
from shared.orchestration import BeltalowdaOrchestrator, BeltalowdaConfig

config = BeltalowdaConfig(num_agents=9, enable_drummer=True)
orchestrator = BeltalowdaOrchestrator(config=config, provider=provider)
result = await orchestrator.execute_workflow(task="...")
```

**Original Reports:**
Generated reports from these projects are preserved in the `reports/` subdirectories.
EOF

# Commit
git add projects/.archive/beltalowda-duplicates/
git commit -m "chore: archive duplicate Beltalowda implementations"
```

**Estimated Time**: 0.5 days

### Task 3.2: Migrate IO/XAI Swarm

**Project**: `projects/io/xai_swarm/`

**Strategy**: Keep UI, delete duplicate orchestrator

**Steps:**

1. **Delete duplicate orchestrator:**

```bash
rm projects/io/xai_swarm/core/swarm_orchestrator.py
```

2. **Update imports in `app.py`:**

```python
# BEFORE
from core.swarm_orchestrator import SwarmOrchestrator

# AFTER
from shared.orchestration import SwarmOrchestrator, SwarmConfig
```

3. **Update initialization:**

```python
from shared.llm_providers import ProviderFactory

provider = ProviderFactory.get_provider('xai')
config = SwarmConfig(num_agents=5, parallel_execution=True)
orchestrator = SwarmOrchestrator(config=config, provider=provider)
```

4. **Test:**

```bash
cd projects/io/xai_swarm
python app.py
# Verify swarm search works
```

**Estimated Time**: 0.5 days

### Task 3.3: Consolidate servers/swarm and projects/io

**Analysis:**
- Both provide Swarm UI
- Near-identical functionality
- Causing namespace confusion

**Decision Options:**

**Option A: Keep servers/swarm as canonical**
- Archive projects/io/
- Redirect users to servers/swarm

**Option B: Merge best features**
- Take best UI elements from each
- Consolidate into servers/swarm
- Archive projects/io

**Option C: Repurpose projects/io**
- Keep as experimental/development version
- Use for testing new features
- servers/swarm remains production

**Recommendation**: Option A (simplest, lowest risk)

**Steps (Option A):**

```bash
# Archive projects/io
mkdir -p projects/.archive/io-swarm/
mv projects/io/ projects/.archive/io-swarm/

# Create redirect README
cat > projects/io-redirect.md << 'EOF'
# IO Swarm → Migrated

This project has been consolidated into `servers/swarm/`.

**To use Swarm:**
- Service: `sm start swarm`
- URL: https://dr.eamer.dev/swarm/
- MCP: `shared/orchestration/SwarmOrchestrator`

See `projects/.archive/io-swarm/` for historical code.
EOF
```

**Estimated Time**: 1 day (review + decision)

### Task 3.4: Remove Duplicated Files

**Checklist:**

- [ ] `servers/studio/core/swarm_orchestrator.py`
- [ ] `servers/studio/core/tool_registry.py`
- [ ] `servers/swarm/core/core_registry.py`
- [ ] `servers/swarm/providers/swarm_adapters.py`
- [ ] `servers/swarm/core/core_config.py.old`
- [ ] `projects/io/core/core_registry.py`
- [ ] `projects/io/xai_swarm/core/swarm_orchestrator.py`

**Verification:**

```bash
# Ensure no imports reference deleted files
grep -r "from core.swarm_orchestrator" servers/ projects/
grep -r "from core.tool_registry" servers/ projects/
grep -r "from core.core_registry" servers/ projects/

# Should return no results
```

**Estimated Time**: 0.5 days

**Phase 3 Total**: 2.5 days

---

## Phase 4: Documentation & Testing (Week 4)

### Task 4.1: Update Service READMEs

**Services to Update:**
- servers/studio/README.md
- servers/swarm/README.md
- servers/planner/README.md

**Add Section:**

```markdown
## Shared Library Integration

This service uses the centralized shared library for:

- **LLM Providers**: `shared.llm_providers.ProviderFactory`
- **Orchestration**: `shared.orchestration.SwarmOrchestrator`
- **Tool Registry**: `shared.tools.ToolRegistry`
- **Configuration**: `shared.config.ConfigManager`

### Setup

1. Install shared library:
```bash
pip install -e /home/coolhand/shared
```

2. Configure API keys in `.env`:
```bash
XAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
```

3. Start service:
```bash
python app.py
```

### Migration from Local Implementation

This service previously maintained local copies of orchestrators, registries,
and providers. These have been replaced by shared library imports for:
- Consistency across services
- Centralized bug fixes
- Feature parity
- Reduced maintenance

See `/home/coolhand/shared/README.md` for shared library documentation.
```

**Estimated Time**: 1 day

### Task 4.2: Create MCP Integration Examples

**File**: `shared/mcp/EXAMPLES.md` (expand existing)

**Add Sections:**

```markdown
## Data Fetching Examples

### Census Data

```python
# Via MCP HTTP
import requests

response = requests.post('http://localhost:5060/mcp/tools/fetch_census_acs', json={
    'year': 2022,
    'variables': {
        'B01003_001E': 'population',
        'B17001_002E': 'poverty_count'
    },
    'geography': 'county:*',
    'state': '06'  # California
})

data = response.json()
print(f"Fetched {len(data['records'])} counties")
```

### arXiv Search

```python
response = requests.post('http://localhost:5060/mcp/tools/search_arxiv', json={
    'query': 'large language models',
    'max_results': 10,
    'category': 'cs.CL'
})

papers = response.json()['papers']
for paper in papers:
    print(f"{paper['title']} - {paper['authors']}")
```

## Utility Examples

### Document Parsing

```python
response = requests.post('http://localhost:5060/mcp/tools/parse_document', json={
    'file_path': '/path/to/document.pdf',
    'format': 'pdf'
})

text = response.json()['text']
print(f"Extracted {len(text)} characters")
```

### Multi-Provider Search

```python
response = requests.post('http://localhost:5060/mcp/tools/multi_provider_search', json={
    'query': 'climate change impacts',
    'providers': ['arxiv', 'semantic_scholar'],
    'max_results_per_provider': 5
})

results = response.json()['aggregated_results']
print(f"Found {results['total_count']} results across providers")
```

## Cache Examples

### Basic Caching

```python
# Store
requests.post('http://localhost:5060/mcp/tools/cache_set', json={
    'key': 'user:123:preferences',
    'value': {'theme': 'dark', 'lang': 'en'},
    'ttl': 3600,
    'namespace': 'user_prefs'
})

# Retrieve
response = requests.post('http://localhost:5060/mcp/tools/cache_get', json={
    'key': 'user:123:preferences',
    'namespace': 'user_prefs'
})

prefs = response.json()['value']
```

### Semantic Caching (LLM Responses)

```python
# Store LLM response
requests.post('http://localhost:5060/mcp/tools/semantic_cache_store', json={
    'prompt': 'Explain quantum entanglement',
    'model': 'grok-3',
    'response': 'Quantum entanglement is...',
    'metadata': {'tokens': 150, 'cost': 0.001}
})

# Lookup similar prompt
response = requests.post('http://localhost:5060/mcp/tools/semantic_cache_lookup', json={
    'prompt': 'What is quantum entanglement?',
    'model': 'grok-3',
    'similarity_threshold': 0.90
})

if response.json()['found']:
    cached_response = response.json()['response']
    print(f"Cache hit! Saved ${response.json()['metadata']['cost']}")
```
```

**Estimated Time**: 1 day

### Task 4.3: Integration Testing

**Test Suites:**

1. **MCP Server Tests** (`shared/mcp/tests/test_integration.py`):

```python
import pytest
import requests

BASE_URL = 'http://localhost:5060/mcp'

def test_list_all_tools():
    """Verify all 30+ tools are exposed"""
    response = requests.get(f'{BASE_URL}/tools')
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 30
    
def test_census_integration():
    """Test Census API integration"""
    response = requests.post(f'{BASE_URL}/tools/fetch_census_acs', json={
        'year': 2022,
        'variables': {'B01003_001E': 'population'},
        'geography': 'state:*'
    })
    assert response.status_code == 200
    assert 'records' in response.json()

def test_semantic_cache():
    """Test semantic cache store and lookup"""
    # Store
    store_resp = requests.post(f'{BASE_URL}/tools/semantic_cache_store', json={
        'prompt': 'Test prompt',
        'model': 'test-model',
        'response': 'Test response'
    })
    assert store_resp.status_code == 200
    
    # Lookup
    lookup_resp = requests.post(f'{BASE_URL}/tools/semantic_cache_lookup', json={
        'prompt': 'Test prompt',
        'model': 'test-model',
        'similarity_threshold': 0.95
    })
    assert lookup_resp.status_code == 200
    assert lookup_resp.json()['found'] == True

# Add more tests...
```

2. **Service Migration Tests**:

```bash
# Studio
cd servers/studio
pytest tests/ -v

# Swarm  
cd servers/swarm
pytest tests/ -v

# Planner
cd servers/planner
pytest tests/ -v
```

3. **Smoke Tests**:

```bash
# Start all migrated services
sm start studio
sm start swarm
sm start planner
sm start mcp-server

# Verify health
curl http://localhost:5060/mcp/health
curl http://localhost:<studio-port>/health
curl http://localhost:<swarm-port>/health
```

**Estimated Time**: 2 days

### Task 4.4: Update Shared Library Usage Patterns

**File**: `shared/USAGE_PATTERNS.md` (new)

**Content:**

```markdown
# Shared Library Usage Patterns

Standard patterns for consuming shared library in services.

## 1. LLM Provider Usage

```python
from shared.llm_providers import ProviderFactory

# Get provider instance
provider = ProviderFactory.get_provider('xai')

# Generate completion
from shared.llm_providers import Message
messages = [Message(role='user', content='Hello')]
response = provider.complete(messages, max_tokens=100)
print(response.content)
```

## 2. Orchestrator Usage

```python
from shared.orchestration import SwarmOrchestrator, SwarmConfig
from shared.llm_providers import ProviderFactory

# Configure
provider = ProviderFactory.get_provider('xai')
config = SwarmConfig(
    num_agents=5,
    parallel_execution=True,
    generate_documents=True
)

# Execute
orchestrator = SwarmOrchestrator(config=config, provider=provider)
result = await orchestrator.execute_workflow(
    task='Research AI safety',
    title='AI Safety Research',
    stream_callback=my_callback  # Optional
)

# Access results
print(result.final_synthesis)
for agent in result.agent_results:
    print(f"{agent.agent_id}: {agent.content[:100]}...")
```

## 3. Tool Registry Usage

```python
from shared.tools import ToolRegistry

# Get singleton
registry = ToolRegistry.get_instance()

# Register tool
registry.register_tool(
    name='my_search',
    schema={
        'type': 'function',
        'function': {
            'name': 'my_search',
            'description': 'Search for documents',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string'}
                },
                'required': ['query']
            }
        }
    },
    handler=my_search_function,
    module_name='search_module'
)

# Get tools for LLM
tools = registry.get_enabled_tools()
```

## 4. Data Fetching Usage

```python
from shared.data_fetching import CensusClient, ArxivClient

# Census
census = CensusClient(use_cache=True)
df = census.fetch_acs(
    year=2022,
    variables={'B01003_001E': 'population'}
)

# arXiv
arxiv = ArxivClient()
papers = arxiv.search('transformers', max_results=10)
```

## 5. Configuration Usage

```python
from shared.config import ConfigManager

# Initialize
config = ConfigManager(
    app_name='myapp',
    defaults={'DEBUG': False}
)

# Get values
debug = config.get('DEBUG')
api_key = config.get_api_key('anthropic')

# List providers
providers = config.list_available_providers()
```

## 6. MCP Integration (HTTP)

```python
import requests

# Call MCP tool
response = requests.post('http://localhost:5060/mcp/tools/orchestrate_research', json={
    'task': 'Research quantum computing',
    'num_agents': 8
})

task_id = response.json()['task_id']

# Stream progress
import sseclient
stream = requests.get(f'http://localhost:5060/mcp/stream/{task_id}', stream=True)
client = sseclient.SSEClient(stream)

for event in client.events():
    print(f"{event.event}: {event.data}")
```
```

**Estimated Time**: 1 day

**Phase 4 Total**: 5 days

---

## Timeline Summary

| Phase | Tasks | Duration | Risk |
|-------|-------|----------|------|
| **Phase 1**: MCP Expansion | 4 tasks | 8 days | Low-Medium |
| **Phase 2**: Service Migrations | 4 tasks | 7 days | Medium-High |
| **Phase 3**: Projects Cleanup | 4 tasks | 2.5 days | Low |
| **Phase 4**: Documentation & Testing | 4 tasks | 5 days | Low |
| **Total** | 16 tasks | **22.5 days** (~4.5 weeks) | Medium |

---

## Success Criteria

### Phase 1
- ✅ 30+ MCP tools exposed
- ✅ All tools return valid JSON
- ✅ All resources accessible
- ✅ Integration tests pass

### Phase 2
- ✅ All services use shared orchestrators
- ✅ All services use shared tool registry
- ✅ All services use shared providers
- ✅ No duplicate orchestrator files remain
- ✅ All service smoke tests pass

### Phase 3
- ✅ Duplicate projects archived
- ✅ No orphaned references remain
- ✅ Archive documentation complete

### Phase 4
- ✅ All READMEs updated
- ✅ Integration tests comprehensive
- ✅ Usage patterns documented
- ✅ MCP examples complete

---

## Rollback Plan

### If Phase 1 Fails
- New MCP tools are additive, old tools unaffected
- Can deploy incrementally (one server at a time)
- Rollback: Remove new tool endpoints from app.py

### If Phase 2 Fails (Service Migration)
- Keep local orchestrator files temporarily
- Conditional import pattern:

```python
try:
    from shared.orchestration import SwarmOrchestrator
except ImportError:
    from core.swarm_orchestrator import SwarmOrchestrator
```

- Rollback: `git revert` migration commits

### If Phase 3 Fails (Cleanup)
- Archive is just `mv`, easily reversible
- Rollback: `mv projects/.archive/X/ projects/X/`

---

## Risk Mitigation

**High-Risk Items:**
1. Planner orchestrator refactoring (Phase 2.3)
   - **Mitigation**: Extensive testing, feature flags, gradual rollout

2. Multiple file imports (Phase 2.2, 2.4)
   - **Mitigation**: Automated find/replace, comprehensive grep verification

3. Breaking changes to service APIs
   - **Mitigation**: Maintain backward compatibility, deprecation warnings

**Medium-Risk Items:**
1. MCP tool schema changes
   - **Mitigation**: Versioning, schema validation tests

2. Cache semantic similarity accuracy
   - **Mitigation**: Adjustable thresholds, opt-in feature

---

## Post-Migration Monitoring

**Week 1 After Completion:**
- Monitor error rates in migrated services
- Check MCP tool usage patterns
- Verify cache hit rates
- Review semantic cache accuracy

**Week 2-4:**
- Collect developer feedback
- Identify missing MCP tools
- Optimize slow tools
- Plan Phase 2 features

---

## Contacts

**Questions/Issues:**
- Luke Steuber (project lead)
- See `shared/README.md` for library documentation
- See `shared/mcp/README.md` for MCP documentation

**Status Updates:**
- Track in `mcp-integration.plan.md`
- Update daily during active implementation

---

**Document Version**: 1.0  
**Last Updated**: November 18, 2025  
**Next Review**: After Phase 1 completion

