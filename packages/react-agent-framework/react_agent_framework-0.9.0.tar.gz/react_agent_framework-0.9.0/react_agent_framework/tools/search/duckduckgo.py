"""
DuckDuckGo search tool (free, no API key required)
"""

from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class DuckDuckGoSearch(BaseTool):
    """
    Search the web using DuckDuckGo

    Free search tool that doesn't require an API key
    """

    name = "duckduckgo"
    description = "Search the web using DuckDuckGo. Input: search query"
    category = "search"

    def __init__(self, max_results: int = 5, **kwargs):
        """
        Initialize DuckDuckGo search

        Args:
            max_results: Maximum number of results to return
        """
        super().__init__(**kwargs)
        self.max_results = max_results

    def execute(self, input_text: str) -> str:
        """
        Execute DuckDuckGo search

        Args:
            input_text: Search query

        Returns:
            Formatted search results
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "Error: duckduckgo-search package not installed. Install with: pip install duckduckgo-search"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(input_text, max_results=self.max_results))

            if not results:
                return "No results found."

            # Format results
            formatted = []
            for i, result in enumerate(results, 1):
                formatted.append(
                    f"{i}. {result['title']}\n" f"   {result['body']}\n" f"   URL: {result['href']}"
                )

            return "\n\n".join(formatted)

        except Exception as e:
            return f"Search error: {str(e)}"
