import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("EuropePMCTool")
class EuropePMCTool(BaseTool):
    """
    Tool to search for articles on Europe PMC including abstracts.
    """

    def __init__(
        self,
        tool_config,
        base_url="https://www.ebi.ac.uk/europepmc/webservices/rest/search",
    ):
        super().__init__(tool_config)
        self.base_url = base_url

    def run(self, arguments):
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, limit)

    def _search(self, query, limit):
        params = {
            "query": query,
            "resultType": "core",  # 'core' includes abstractText
            "pageSize": limit,
            "format": "json",
        }
        response = requests.get(self.base_url, params=params, timeout=20)
        if response.status_code != 200:
            return {
                "error": f"Europe PMC API error {response.status_code}",
                "reason": response.reason,
            }

        results = response.json().get("resultList", {}).get("result", [])
        articles = [
            {
                "title": rec.get("title"),
                "abstract": rec.get("abstractText"),
                "journal": rec.get("journalTitle"),
                "year": rec.get("pubYear"),
                "url": f"https://europepmc.org/article/{rec.get('source')}/{rec.get('id')}",
            }
            for rec in results
        ]
        return articles
