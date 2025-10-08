import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("SemanticScholarTool")
class SemanticScholarTool(BaseTool):
    """
    Tool to search for papers on Semantic Scholar including abstracts.
    """

    def __init__(
        self,
        tool_config,
        base_url="https://api.semanticscholar.org/graph/v1/paper/search",
    ):
        super().__init__(tool_config)
        self.base_url = base_url

    def run(self, arguments):
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        api_key = arguments.get("api_key")
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, limit, api_key)

    def _search(self, query, limit, api_key):
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,year,venue,url",
        }
        headers = {"x-api-key": api_key} if api_key else {}
        response = requests.get(
            self.base_url, params=params, headers=headers, timeout=20
        )
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "2"))
            import time

            time.sleep(retry_after)
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=20
            )
        if response.status_code != 200:
            return {
                "error": f"Semantic Scholar API error {response.status_code}",
                "reason": response.reason,
            }
        results = response.json().get("data", [])
        papers = [
            {
                "title": p.get("title"),
                "abstract": p.get("abstract"),
                "journal": p.get("venue"),
                "year": p.get("year"),
                "url": p.get("url"),
            }
            for p in results
        ]
        return papers
