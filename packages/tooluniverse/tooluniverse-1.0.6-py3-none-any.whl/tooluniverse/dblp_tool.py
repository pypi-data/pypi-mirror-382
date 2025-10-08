import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("DBLPTool")
class DBLPTool(BaseTool):
    """
    Search DBLP Computer Science Bibliography for publications.
    """

    def __init__(
        self,
        tool_config,
        base_url="https://dblp.org/search/publ/api",
    ):
        super().__init__(tool_config)
        self.base_url = base_url

    def run(self, arguments):
        query = arguments.get("query")
        limit = int(arguments.get("limit", 10))
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, limit)

    def _search(self, query, limit):
        params = {
            "q": query,
            "h": max(1, min(limit, 100)),
            "format": "json",
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=20)
        except requests.RequestException as e:
            return {
                "error": "Network error calling DBLP API",
                "reason": str(e),
            }

        if response.status_code != 200:
            return {
                "error": f"DBLP API error {response.status_code}",
                "reason": response.reason,
            }

        hits = response.json().get("result", {}).get("hits", {}).get("hit", [])
        results = []
        for hit in hits:
            info = hit.get("info", {})
            results.append(
                {
                    "title": info.get("title"),
                    "authors": info.get("authors", {}).get("author"),
                    "year": info.get("year"),
                    "venue": info.get("venue"),
                    "url": info.get("url"),
                    "ee": info.get("ee"),
                }
            )

        return results
