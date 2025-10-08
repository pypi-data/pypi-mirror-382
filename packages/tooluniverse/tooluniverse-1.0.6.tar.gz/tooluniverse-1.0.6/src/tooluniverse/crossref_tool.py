import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("CrossrefTool")
class CrossrefTool(BaseTool):
    """
    Search Crossref Works API for articles by keyword.
    """

    def __init__(
        self,
        tool_config,
        base_url="https://api.crossref.org/works",
    ):
        super().__init__(tool_config)
        self.base_url = base_url

    def run(self, arguments):
        query = arguments.get("query")
        rows = int(arguments.get("limit", 10))
        # e.g., 'type:journal-article,from-pub-date:2020-01-01'
        filter_str = arguments.get("filter")
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, rows, filter_str)

    def _search(self, query, rows, filter_str):
        params = {"query": query, "rows": max(1, min(rows, 100))}
        if filter_str:
            params["filter"] = filter_str

        try:
            response = requests.get(self.base_url, params=params, timeout=20)
        except requests.RequestException as e:
            return {
                "error": "Network error calling Crossref API",
                "reason": str(e),
            }

        if response.status_code != 200:
            return {
                "error": f"Crossref API error {response.status_code}",
                "reason": response.reason,
            }

        data = response.json().get("message", {}).get("items", [])
        results = []
        for item in data:
            title_list = item.get("title") or []
            title = title_list[0] if title_list else None
            abstract = item.get("abstract")
            year = None
            issued = item.get("issued", {}).get("date-parts") or []
            if issued and issued[0]:
                year = issued[0][0]
            url = item.get("URL")
            doi = item.get("DOI")
            container_title = item.get("container-title") or []
            journal = container_title[0] if container_title else None
            results.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "doi": doi,
                    "url": url,
                }
            )

        return results
