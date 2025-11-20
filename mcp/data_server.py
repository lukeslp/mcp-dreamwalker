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
- wikipedia_search: Search Wikipedia articles
- wikipedia_get_summary: Get article summary
- wikipedia_get_full_content: Get full article content
- weather_get_current: Get current weather conditions (NOAA)
- weather_get_forecast: Get weather forecast (NOAA)
- weather_get_alerts: Get weather alerts by state (NOAA)
- youtube_search_videos: Search YouTube videos
- youtube_channel_statistics: Get channel stats
- youtube_playlist_items: List playlist videos
- news_top_headlines: Get top news headlines
- news_search: Search news articles
- news_sources: List news sources

Resources provided:
- census://variables/{table}: Census variable catalog
- arxiv://category/{category}: arXiv category info
- archive://snapshot/{url}/{timestamp}: Wayback snapshot metadata
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import from shared library
sys.path.insert(0, '/home/coolhand/shared')

from config import ConfigManager
from data_fetching import ArxivClient, ArchiveClient, CensusClient, SemanticScholarClient
from data_fetching.wikipedia_client import WikipediaClient
from data_fetching.weather_client import WeatherClient
from data_fetching.youtube_client import YouTubeClient
from data_fetching.news_client import NewsClient

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
        self._wikipedia_client = None
        self._weather_client = None
        self._youtube_client = None
        self._news_client = None

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

    def get_wikipedia_client(self) -> WikipediaClient:
        """Get or create Wikipedia client."""
        if self._wikipedia_client is None:
            self._wikipedia_client = WikipediaClient()
        return self._wikipedia_client

    def get_weather_client(self) -> WeatherClient:
        """Get or create Weather client."""
        if self._weather_client is None:
            self._weather_client = WeatherClient()
        return self._weather_client

    def get_youtube_client(self) -> YouTubeClient:
        """Get or create YouTube client."""
        if self._youtube_client is None:
            api_key = self.config.get('YOUTUBE_API_KEY')
            if not api_key:
                raise RuntimeError("YOUTUBE_API_KEY not configured")
            self._youtube_client = YouTubeClient(api_key=api_key)
        return self._youtube_client

    def get_news_client(self) -> NewsClient:
        """Get or create News client."""
        if self._news_client is None:
            api_key = self.config.get('NEWS_API_KEY')
            if not api_key:
                raise RuntimeError("NEWS_API_KEY not configured")
            self._news_client = NewsClient(api_key=api_key)
        return self._news_client

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
    # MCP Tools - Wikipedia
    # -------------------------------------------------------------------------

    def tool_wikipedia_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: wikipedia_search

        Search Wikipedia articles by keyword.

        Arguments:
            query (str): Search keywords
            limit (int, optional): Max results (default: 10, max: 25)

        Returns:
            {success: bool, results: List[Dict], metadata: Dict}
        """
        try:
            query = arguments.get('query')
            if not query:
                return {
                    "success": False,
                    "error": "Missing required argument: query"
                }

            limit = arguments.get('limit', 10)
            limit = min(limit, 25)  # Cap at 25

            client = self.get_wikipedia_client()
            result = client.search(query=query, limit=limit)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "results": result.get('results', []),
                "metadata": {
                    "query": query,
                    "result_count": result.get('count', 0),
                    "source": "Wikipedia",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in wikipedia_search: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_wikipedia_get_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: wikipedia_get_summary

        Get a concise summary of a Wikipedia article.

        Arguments:
            title (str): Wikipedia article title

        Returns:
            {success: bool, article: Dict}
        """
        try:
            title = arguments.get('title')
            if not title:
                return {
                    "success": False,
                    "error": "Missing required argument: title"
                }

            client = self.get_wikipedia_client()
            result = client.get_summary(title=title)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "article": {
                    "title": result.get('title'),
                    "summary": result.get('summary'),
                    "page_id": result.get('page_id'),
                    "image": result.get('image'),
                    "url": result.get('url')
                },
                "metadata": {
                    "source": "Wikipedia",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in wikipedia_get_summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_wikipedia_get_full_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: wikipedia_get_full_content

        Retrieve the full content of a Wikipedia article.

        Arguments:
            title (str): Wikipedia article title

        Returns:
            {success: bool, article: Dict}
        """
        try:
            title = arguments.get('title')
            if not title:
                return {
                    "success": False,
                    "error": "Missing required argument: title"
                }

            client = self.get_wikipedia_client()
            result = client.get_full_content(title=title)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "article": {
                    "title": result.get('title'),
                    "content": result.get('content'),
                    "page_id": result.get('page_id'),
                    "word_count": result.get('word_count'),
                    "url": result.get('url')
                },
                "metadata": {
                    "source": "Wikipedia",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in wikipedia_get_full_content: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - Weather (NOAA)
    # -------------------------------------------------------------------------

    def tool_weather_get_current(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: weather_get_current

        Get current weather conditions for coordinates.

        Arguments:
            latitude (float): Latitude in decimal degrees
            longitude (float): Longitude in decimal degrees

        Returns:
            {success: bool, location: Dict, current: Dict, metadata: Dict}
        """
        try:
            latitude = arguments.get('latitude')
            longitude = arguments.get('longitude')

            if latitude is None or longitude is None:
                return {
                    "success": False,
                    "error": "Missing required arguments: latitude and longitude"
                }

            client = self.get_weather_client()
            result = client.get_current_weather(latitude=latitude, longitude=longitude)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "location": result.get('location', {}),
                "current": result.get('current', {}),
                "metadata": {
                    "source": "NOAA Weather Service",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in weather_get_current: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_weather_get_forecast(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: weather_get_forecast

        Get multi-day weather forecast for coordinates.

        Arguments:
            latitude (float): Latitude in decimal degrees
            longitude (float): Longitude in decimal degrees
            periods (int, optional): Number of forecast periods (default: 7, max: 14)

        Returns:
            {success: bool, location: Dict, forecast: List[Dict], metadata: Dict}
        """
        try:
            latitude = arguments.get('latitude')
            longitude = arguments.get('longitude')

            if latitude is None or longitude is None:
                return {
                    "success": False,
                    "error": "Missing required arguments: latitude and longitude"
                }

            periods = arguments.get('periods', 7)
            periods = max(1, min(periods, 14))  # Cap between 1-14

            client = self.get_weather_client()
            result = client.get_forecast(latitude=latitude, longitude=longitude, periods=periods)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "location": result.get('location', {}),
                "forecast": result.get('forecast', []),
                "metadata": {
                    "periods": len(result.get('forecast', [])),
                    "source": "NOAA Weather Service",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in weather_get_forecast: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_weather_get_alerts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: weather_get_alerts

        Get active weather alerts for a state.

        Arguments:
            state (str): Two-letter state code (e.g., CA, NY, OR)

        Returns:
            {success: bool, state: str, alerts: List[Dict], metadata: Dict}
        """
        try:
            state = arguments.get('state')
            if not state:
                return {
                    "success": False,
                    "error": "Missing required argument: state"
                }

            # Ensure uppercase
            state = state.upper()

            client = self.get_weather_client()
            result = client.get_alerts(state=state)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "state": state,
                "alerts": result.get('alerts', []),
                "metadata": {
                    "alert_count": result.get('count', 0),
                    "source": "NOAA Weather Service",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in weather_get_alerts: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - YouTube
    # -------------------------------------------------------------------------

    def tool_youtube_search_videos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: youtube_search_videos

        Search for videos on YouTube.

        Arguments:
            query (str): Search query
            max_results (int, optional): Max results (default: 10, max: 25)
            order (str, optional): Sort order (relevance, date, rating, title, viewCount)
            safe_search (str, optional): Safety filter (none, moderate, strict)
            video_duration (str, optional): Duration filter (any, short, medium, long)

        Returns:
            {success: bool, videos: List[Dict], metadata: Dict}
        """
        try:
            query = arguments.get('query')
            if not query:
                return {
                    "success": False,
                    "error": "Missing required argument: query"
                }

            max_results = min(arguments.get('max_results', 10), 25)
            order = arguments.get('order', 'relevance')
            safe_search = arguments.get('safe_search', 'moderate')
            video_duration = arguments.get('video_duration')

            client = self.get_youtube_client()
            result = client.search_videos(
                query=query,
                max_results=max_results,
                order=order,
                safe_search=safe_search,
                video_duration=video_duration
            )

            return {
                "success": True,
                "videos": result.get('videos', []),
                "metadata": {
                    "query": query,
                    "result_count": result.get('total_results', 0),
                    "next_page_token": result.get('next_page_token'),
                    "source": "YouTube Data API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in youtube_search_videos: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_youtube_channel_statistics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: youtube_channel_statistics

        Fetch statistics and metadata for a YouTube channel.

        Arguments:
            channel_id (str): YouTube channel ID

        Returns:
            {success: bool, channel: Dict, metadata: Dict}
        """
        try:
            channel_id = arguments.get('channel_id')
            if not channel_id:
                return {
                    "success": False,
                    "error": "Missing required argument: channel_id"
                }

            client = self.get_youtube_client()
            result = client.get_channel_statistics(channel_id=channel_id)

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "channel": result,
                "metadata": {
                    "source": "YouTube Data API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in youtube_channel_statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_youtube_playlist_items(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: youtube_playlist_items

        List items from a YouTube playlist.

        Arguments:
            playlist_id (str): YouTube playlist ID
            max_results (int, optional): Max items (default: 25, max: 25)

        Returns:
            {success: bool, items: List[Dict], metadata: Dict}
        """
        try:
            playlist_id = arguments.get('playlist_id')
            if not playlist_id:
                return {
                    "success": False,
                    "error": "Missing required argument: playlist_id"
                }

            max_results = min(arguments.get('max_results', 25), 25)

            client = self.get_youtube_client()
            result = client.get_playlist_items(
                playlist_id=playlist_id,
                max_results=max_results
            )

            return {
                "success": True,
                "items": result.get('items', []),
                "metadata": {
                    "playlist_id": playlist_id,
                    "result_count": result.get('total_results', 0),
                    "next_page_token": result.get('next_page_token'),
                    "source": "YouTube Data API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in youtube_playlist_items: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # MCP Tools - News
    # -------------------------------------------------------------------------

    def tool_news_top_headlines(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: news_top_headlines

        Get top news headlines for a country or category.

        Arguments:
            country (str, optional): ISO country code (default: us)
            category (str, optional): Category (business, technology, etc.)
            query (str, optional): Search keywords
            page_size (int, optional): Max results (default: 20, max: 50)

        Returns:
            {success: bool, articles: List[Dict], metadata: Dict}
        """
        try:
            country = arguments.get('country', 'us')
            category = arguments.get('category')
            query = arguments.get('query')
            page_size = min(arguments.get('page_size', 20), 50)

            client = self.get_news_client()
            result = client.get_top_headlines(
                country=country,
                category=category,
                query=query,
                page_size=page_size
            )

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "articles": result.get('articles', []),
                "metadata": {
                    "total_results": result.get('total_results', 0),
                    "country": country,
                    "category": category,
                    "source": "News API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in news_top_headlines: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_news_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: news_search

        Search news articles across sources.

        Arguments:
            query (str): Search keywords
            language (str, optional): Language code (default: en)
            page_size (int, optional): Max results (default: 20, max: 50)
            from_date (str, optional): Start date (YYYY-MM-DD)
            to_date (str, optional): End date (YYYY-MM-DD)

        Returns:
            {success: bool, articles: List[Dict], metadata: Dict}
        """
        try:
            query = arguments.get('query')
            if not query:
                return {
                    "success": False,
                    "error": "Missing required argument: query"
                }

            language = arguments.get('language', 'en')
            page_size = min(arguments.get('page_size', 20), 50)
            from_date = arguments.get('from_date')
            to_date = arguments.get('to_date')

            client = self.get_news_client()
            result = client.search_everything(
                query=query,
                language=language,
                page_size=page_size,
                from_date=from_date,
                to_date=to_date
            )

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "articles": result.get('articles', []),
                "metadata": {
                    "query": query,
                    "total_results": result.get('total_results', 0),
                    "language": language,
                    "source": "News API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in news_search: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tool_news_sources(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: news_sources

        List available news sources and metadata.

        Arguments:
            category (str, optional): Filter by category
            language (str, optional): Filter by language code
            country (str, optional): Filter by country code

        Returns:
            {success: bool, sources: List[Dict], metadata: Dict}
        """
        try:
            category = arguments.get('category')
            language = arguments.get('language')
            country = arguments.get('country')

            client = self.get_news_client()
            result = client.get_sources(
                category=category,
                language=language,
                country=country
            )

            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            return {
                "success": True,
                "sources": result.get('sources', []),
                "metadata": {
                    "count": result.get('count', 0),
                    "filters": {
                        "category": category,
                        "language": language,
                        "country": country
                    },
                    "source": "News API",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.exception(f"Error in news_sources: {e}")
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
            timestamp = parts[1] if len(parts) > 1 else None

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
            },
            # Wikipedia tools
            {
                "name": "wikipedia_search",
                "description": "Search Wikipedia articles by keyword",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keywords"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results (default: 10, max: 25)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "wikipedia_get_summary",
                "description": "Get a concise summary of a Wikipedia article",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Wikipedia article title"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "wikipedia_get_full_content",
                "description": "Retrieve the full content of a Wikipedia article",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Wikipedia article title"
                        }
                    },
                    "required": ["title"]
                }
            },
            # Weather tools
            {
                "name": "weather_get_current",
                "description": "Get current weather conditions for coordinates (NOAA)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude in decimal degrees"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude in decimal degrees"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "weather_get_forecast",
                "description": "Get multi-day weather forecast for coordinates (NOAA)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude in decimal degrees"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude in decimal degrees"
                        },
                        "periods": {
                            "type": "integer",
                            "description": "Number of forecast periods (default: 7, max: 14)"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "weather_get_alerts",
                "description": "Get active weather alerts for a state (NOAA)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "description": "Two-letter state code (e.g., CA, NY, OR)"
                        }
                    },
                    "required": ["state"]
                }
            },
            # YouTube tools
            {
                "name": "youtube_search_videos",
                "description": "Search for videos on YouTube",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Max results (default: 10, max: 25)"
                        },
                        "order": {
                            "type": "string",
                            "description": "Sort order: relevance, date, rating, title, viewCount (default: relevance)"
                        },
                        "safe_search": {
                            "type": "string",
                            "description": "Safety filter: none, moderate, strict (default: moderate)"
                        },
                        "video_duration": {
                            "type": "string",
                            "description": "Duration filter: any, short, medium, long (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "youtube_channel_statistics",
                "description": "Fetch statistics and metadata for a YouTube channel",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "YouTube channel ID"
                        }
                    },
                    "required": ["channel_id"]
                }
            },
            {
                "name": "youtube_playlist_items",
                "description": "List items from a YouTube playlist",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "playlist_id": {
                            "type": "string",
                            "description": "YouTube playlist ID"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Max items (default: 25, max: 25)"
                        }
                    },
                    "required": ["playlist_id"]
                }
            },
            # News tools
            {
                "name": "news_top_headlines",
                "description": "Get top news headlines for a country or category",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "country": {
                            "type": "string",
                            "description": "ISO country code (default: us)"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category (business, technology, health, etc.)"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search keywords (optional)"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Max results (default: 20, max: 50)"
                        }
                    }
                }
            },
            {
                "name": "news_search",
                "description": "Search news articles across sources",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keywords"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code (default: en)"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Max results (default: 20, max: 50)"
                        },
                        "from_date": {
                            "type": "string",
                            "description": "Start date (YYYY-MM-DD format)"
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date (YYYY-MM-DD format)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "news_sources",
                "description": "List available news sources and metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category (optional)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Filter by language code (optional)"
                        },
                        "country": {
                            "type": "string",
                            "description": "Filter by country code (optional)"
                        }
                    }
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

