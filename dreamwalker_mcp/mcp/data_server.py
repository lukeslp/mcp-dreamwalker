"""
Data Fetching MCP Server

Exposes shared.data_fetching capabilities through MCP protocol.

Tools provided:
- fetch_census_acs: Fetch American Community Survey data
- fetch_census_saipe: Fetch poverty estimates
- list_census_variables: Search Census variable catalog
- search_arxiv: Search arXiv papers
- search_semantic_scholar: Search research papers
- get_semantic_scholar_paper: Get paper details
- wayback_search: Search Wayback Machine
- wayback_available_snapshots: List available snapshots

Resources provided:
- census://variables/{table}: Census variable catalog
- arxiv://category/{category}: arXiv category info
- archive://snapshot/{url}/{timestamp}: Wayback snapshot metadata
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from shared library
import sys
sys.path.insert(0, '/home/coolhand/shared')
from data_fetching import CensusClient, ArxivClient, SemanticScholarClient, ArchiveClient
from config import ConfigManager

logger = logging.getLogger(__name__)


class DataServer:
    """
    MCP server for data fetching capabilities.

    Exposes Census, arXiv, Semantic Scholar, and Archive.org through MCP protocol.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize data fetching MCP server.

        Args:
            config_manager: ConfigManager instance (creates new one if None)
        """
        self.config = config_manager or ConfigManager(app_name='mcp_data')

        # Initialize clients (lazy loading)
        self._census_client = None
        self._arxiv_client = None
        self._semantic_scholar_client = None
        self._archive_client = None

    def get_census_client(self) -> CensusClient:
        """Get or create Census client."""
        if self._census_client is None:
            api_key = self.config.get('CENSUS_API_KEY')
            self._census_client = CensusClient(
                api_key=api_key,
                use_cache=True
            )
        return self._census_client

    def get_arxiv_client(self) -> ArxivClient:
        """Get or create arXiv client."""
        if self._arxiv_client is None:
            self._arxiv_client = ArxivClient()
        return self._arxiv_client

    def get_semantic_scholar_client(self) -> SemanticScholarClient:
        """Get or create Semantic Scholar client."""
        if self._semantic_scholar_client is None:
            self._semantic_scholar_client = SemanticScholarClient()
        return self._semantic_scholar_client

    def get_archive_client(self) -> ArchiveClient:
        """Get or create Archive.org client."""
        if self._archive_client is None:
            self._archive_client = ArchiveClient()
        return self._archive_client

    # -------------------------------------------------------------------------
    # MCP Tools - Census Bureau
    # -------------------------------------------------------------------------

    def tool_fetch_census_acs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: fetch_census_acs

        Fetch American Community Survey (ACS) demographic data.

        Arguments:
            year (int): Census year (e.g., 2022)
            variables (dict): Variable mapping {code: name}
            geography (str, optional): Geographic level (default: county:*)
            state (str, optional): State FIPS code filter

        Returns:
            {success: bool, records: List[Dict], metadata: Dict}
        """
        try:
            year = arguments.get('year')
            variables = arguments.get('variables')

            if not year or not variables:
                return {
                    "success": False,
                    "error": "Missing required arguments: year and variables"
                }

            client = self.get_census_client()

            df = client.fetch_acs(
                year=year,
                variables=variables,
                geography=arguments.get('geography', 'county:*'),
                state=arguments.get('state')
            )

            # Convert DataFrame to records
            records = df.to_dict('records')

            return {
                "success": True,
                "records": records,
                "metadata": {
                    "year": year,
                    "record_count": len(records),
                    "source": "Census ACS 5-year estimates",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in fetch_census_acs: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_fetch_census_saipe(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: fetch_census_saipe

        Fetch Small Area Income and Poverty Estimates (SAIPE).

        Arguments:
            year (int): Census year
            geography (str, optional): county, state, or us (default: county)
            state (str, optional): State FIPS code filter

        Returns:
            {success: bool, records: List[Dict], metadata: Dict}
        """
        try:
            year = arguments.get('year')
            if not year:
                return {
                    "success": False,
                    "error": "Missing required argument: year"
                }

            client = self.get_census_client()

            df = client.fetch_saipe(
                year=year,
                geography=arguments.get('geography', 'county'),
                state=arguments.get('state')
            )

            records = df.to_dict('records')

            return {
                "success": True,
                "records": records,
                "metadata": {
                    "year": year,
                    "record_count": len(records),
                    "source": "Census SAIPE",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in fetch_census_saipe: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_list_census_variables(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: list_census_variables

        Search Census variable catalog.

        Arguments:
            search_term (str, optional): Keyword to search
            table (str, optional): Specific table (e.g., "B17001")

        Returns:
            {success: bool, variables: List[Dict]}
        """
        try:
            # This would require implementing variable catalog search in CensusClient
            # For now, return placeholder
            return {
                "success": True,
                "variables": [],
                "message": "Variable catalog search not yet implemented"
            }

        except Exception as e:
            logger.exception(f"Error in list_census_variables: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - arXiv
    # -------------------------------------------------------------------------

    def tool_search_arxiv(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: search_arxiv

        Search arXiv for academic papers.

        Arguments:
            query (str): Search query
            max_results (int, optional): Max papers to return (default: 5)
            sort_by (str, optional): relevance or date (default: relevance)
            category (str, optional): arXiv category filter

        Returns:
            {success: bool, papers: List[Dict], metadata: Dict}
        """
        try:
            query = arguments.get('query')
            if not query:
                return {
                    "success": False,
                    "error": "Missing required argument: query"
                }

            client = self.get_arxiv_client()

            # Add category filter if provided
            search_query = query
            category = arguments.get('category')
            if category:
                search_query = f"cat:{category} AND {query}"

            papers = client.search(
                query=search_query,
                max_results=arguments.get('max_results', 5),
                sort_by=arguments.get('sort_by', 'relevance')
            )

            # Convert to dicts
            paper_dicts = [p.to_dict() for p in papers]

            return {
                "success": True,
                "papers": paper_dicts,
                "metadata": {
                    "query": query,
                    "result_count": len(paper_dicts),
                    "source": "arXiv",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in search_arxiv: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - Semantic Scholar
    # -------------------------------------------------------------------------

    def tool_search_semantic_scholar(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: search_semantic_scholar

        Search Semantic Scholar for research papers.

        Arguments:
            query (str): Search query
            limit (int, optional): Max papers to return (default: 10)
            fields (list, optional): Fields to return

        Returns:
            {success: bool, papers: List[Dict], metadata: Dict}
        """
        try:
            query = arguments.get('query')
            if not query:
                return {
                    "success": False,
                    "error": "Missing required argument: query"
                }

            client = self.get_semantic_scholar_client()

            papers = client.search_papers(
                query=query,
                limit=arguments.get('limit', 10),
                fields=arguments.get('fields')
            )

            # Convert to dicts
            paper_dicts = [p.to_dict() for p in papers]

            return {
                "success": True,
                "papers": paper_dicts,
                "metadata": {
                    "query": query,
                    "result_count": len(paper_dicts),
                    "source": "Semantic Scholar",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in search_semantic_scholar: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_get_semantic_scholar_paper(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: get_semantic_scholar_paper

        Get detailed information about a specific paper.

        Arguments:
            paper_id (str): Semantic Scholar paper ID
            fields (list, optional): Fields to return

        Returns:
            {success: bool, paper: Dict}
        """
        try:
            paper_id = arguments.get('paper_id')
            if not paper_id:
                return {
                    "success": False,
                    "error": "Missing required argument: paper_id"
                }

            client = self.get_semantic_scholar_client()

            paper = client.get_paper_details(
                paper_id=paper_id,
                fields=arguments.get('fields')
            )

            if paper:
                return {
                    "success": True,
                    "paper": paper.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Paper not found: {paper_id}"
                }

        except Exception as e:
            logger.exception(f"Error in get_semantic_scholar_paper: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - Internet Archive / Wayback Machine
    # -------------------------------------------------------------------------

    def tool_wayback_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: wayback_search

        Get the most recent archived snapshot of a URL.

        Arguments:
            url (str): URL to search for
            timestamp (str, optional): Specific timestamp (YYYYMMDDhhmmss)

        Returns:
            {success: bool, snapshot: Dict}
        """
        try:
            url = arguments.get('url')
            if not url:
                return {
                    "success": False,
                    "error": "Missing required argument: url"
                }

            client = self.get_archive_client()

            snapshot = client.get_latest_snapshot(url)

            if snapshot:
                return {
                    "success": True,
                    "snapshot": {
                        "url": snapshot.url,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "status_code": snapshot.status_code,
                        "original_url": snapshot.original_url,
                        "archive_url": snapshot.archive_url
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"No archived snapshots found for: {url}"
                }

        except Exception as e:
            logger.exception(f"Error in wayback_search: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_wayback_available_snapshots(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: wayback_available_snapshots

        List all available snapshots for a URL.

        Arguments:
            url (str): URL to search for
            year (int, optional): Filter by year

        Returns:
            {success: bool, snapshots: List[Dict]}
        """
        try:
            url = arguments.get('url')
            if not url:
                return {
                    "success": False,
                    "error": "Missing required argument: url"
                }

            client = self.get_archive_client()

            # Get all snapshots for the URL
            # This would require implementing list_snapshots in ArchiveClient
            # For now, just get latest as example
            snapshot = client.get_latest_snapshot(url)

            snapshots = []
            if snapshot:
                snapshots = [{
                    "url": snapshot.url,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "status_code": snapshot.status_code,
                    "archive_url": snapshot.archive_url
                }]

            return {
                "success": True,
                "snapshots": snapshots,
                "metadata": {
                    "url": url,
                    "snapshot_count": len(snapshots),
                    "source": "Internet Archive Wayback Machine"
                }
            }

        except Exception as e:
            logger.exception(f"Error in wayback_available_snapshots: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Resources
    # -------------------------------------------------------------------------

    def resource_census_variables(self, uri: str) -> Dict[str, Any]:
        """
        MCP Resource: census://variables/{table}

        Returns Census variable catalog for a table.

        Args:
            uri: Resource URI (e.g., "census://variables/B17001")

        Returns:
            Variable catalog
        """
        try:
            # Parse URI: census://variables/{table}
            parts = uri.replace('census://variables/', '')
            table = parts

            # This would query Census API for variable definitions
            # For now, return placeholder
            return {
                "uri": uri,
                "table": table,
                "variables": [],
                "message": "Census variable catalog not yet implemented"
            }

        except Exception as e:
            logger.exception(f"Error in resource_census_variables: {e}")
            return {
                "uri": uri,
                "error": str(e)
            }

    def resource_arxiv_category(self, uri: str) -> Dict[str, Any]:
        """
        MCP Resource: arxiv://category/{category}

        Returns arXiv category information.

        Args:
            uri: Resource URI (e.g., "arxiv://category/cs.CL")

        Returns:
            Category metadata
        """
        try:
            # Parse URI: arxiv://category/{category}
            parts = uri.replace('arxiv://category/', '')
            category = parts

            # arXiv category taxonomy
            categories = {
                'cs.CL': 'Computation and Language',
                'cs.AI': 'Artificial Intelligence',
                'cs.LG': 'Machine Learning',
                'cs.CV': 'Computer Vision and Pattern Recognition',
                'cs.NE': 'Neural and Evolutionary Computing',
                'math.ST': 'Statistics Theory',
                'stat.ML': 'Machine Learning (Statistics)',
                'physics.data-an': 'Data Analysis, Statistics and Probability',
                'q-bio.QM': 'Quantitative Methods'
            }

            category_name = categories.get(category, 'Unknown')

            return {
                "uri": uri,
                "category": category,
                "name": category_name,
                "all_categories": categories
            }

        except Exception as e:
            logger.exception(f"Error in resource_arxiv_category: {e}")
            return {
                "uri": uri,
                "error": str(e)
            }

    def resource_archive_snapshot(self, uri: str) -> Dict[str, Any]:
        """
        MCP Resource: archive://snapshot/{url}/{timestamp}

        Returns metadata about an archived snapshot.

        Args:
            uri: Resource URI (e.g., "archive://snapshot/example.com/20231201")

        Returns:
            Snapshot metadata
        """
        try:
            # Parse URI: archive://snapshot/{url}/{timestamp}
            parts = uri.replace('archive://snapshot/', '').split('/')
            url = parts[0]
            parts[1] if len(parts) > 1 else None

            client = self.get_archive_client()

            snapshot = client.get_latest_snapshot(url)

            if snapshot:
                return {
                    "uri": uri,
                    "url": url,
                    "snapshot": {
                        "archive_url": snapshot.archive_url,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "status_code": snapshot.status_code
                    }
                }
            else:
                return {
                    "uri": uri,
                    "error": f"No snapshot found for: {url}"
                }

        except Exception as e:
            logger.exception(f"Error in resource_archive_snapshot: {e}")
            return {
                "uri": uri,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Server Interface
    # -------------------------------------------------------------------------

    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        """
        Return MCP tools manifest.

        Returns:
            List of tool definitions
        """
        return [
            # Census tools
            {
                "name": "fetch_census_acs",
                "description": "Fetch American Community Survey (ACS) demographic data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Census year (e.g., 2022)"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Variable mapping {code: name}"
                        },
                        "geography": {
                            "type": "string",
                            "description": "Geographic level (default: county:*)"
                        },
                        "state": {
                            "type": "string",
                            "description": "State FIPS code filter (optional)"
                        }
                    },
                    "required": ["year", "variables"]
                }
            },
            {
                "name": "fetch_census_saipe",
                "description": "Fetch Small Area Income and Poverty Estimates",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Census year"
                        },
                        "geography": {
                            "type": "string",
                            "description": "county, state, or us (default: county)"
                        },
                        "state": {
                            "type": "string",
                            "description": "State FIPS code filter (optional)"
                        }
                    },
                    "required": ["year"]
                }
            },
            {
                "name": "list_census_variables",
                "description": "Search Census variable catalog",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Keyword to search (optional)"
                        },
                        "table": {
                            "type": "string",
                            "description": "Specific table (e.g., 'B17001') (optional)"
                        }
                    }
                }
            },
            # arXiv tools
            {
                "name": "search_arxiv",
                "description": "Search arXiv for academic papers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Max papers to return (default: 5)"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "relevance or date (default: relevance)"
                        },
                        "category": {
                            "type": "string",
                            "description": "arXiv category filter (e.g., 'cs.CL') (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            # Semantic Scholar tools
            {
                "name": "search_semantic_scholar",
                "description": "Search Semantic Scholar for research papers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max papers to return (default: 10)"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to return (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_semantic_scholar_paper",
                "description": "Get detailed information about a specific paper",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paper_id": {
                            "type": "string",
                            "description": "Semantic Scholar paper ID"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to return (optional)"
                        }
                    },
                    "required": ["paper_id"]
                }
            },
            # Wayback Machine tools
            {
                "name": "wayback_search",
                "description": "Get the most recent archived snapshot of a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to search for"
                        },
                        "timestamp": {
                            "type": "string",
                            "description": "Specific timestamp (YYYYMMDDhhmmss) (optional)"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "wayback_available_snapshots",
                "description": "List all available snapshots for a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to search for"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Filter by year (optional)"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]

    def get_resources_manifest(self) -> List[Dict[str, Any]]:
        """
        Return MCP resources manifest.

        Returns:
            List of resource templates
        """
        return [
            {
                "uri": "census://variables/{table}",
                "name": "Census Variable Catalog",
                "description": "Census variable definitions for a table",
                "mimeType": "application/json"
            },
            {
                "uri": "arxiv://category/{category}",
                "name": "arXiv Category Info",
                "description": "arXiv category taxonomy and metadata",
                "mimeType": "application/json"
            },
            {
                "uri": "archive://snapshot/{url}/{timestamp}",
                "name": "Wayback Snapshot Metadata",
                "description": "Internet Archive snapshot information",
                "mimeType": "application/json"
            }
        ]

