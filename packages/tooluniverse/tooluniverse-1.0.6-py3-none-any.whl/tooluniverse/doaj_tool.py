import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("DOAJTool")
class DOAJTool(BaseTool):
    """
    Search DOAJ (Directory of Open Access Journals) articles and journals.

    Parameters (arguments):
        query (str): Query string (Lucene syntax supported by DOAJ)
        max_results (int): Max number of results (default 10, max 100)
        type (str): "articles" or "journals" (default: "articles")
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://doaj.org/api/search"

    def run(self, arguments=None):
        arguments = arguments or {}
        query = arguments.get("query")
        search_type = arguments.get("type", "articles")
        max_results = int(arguments.get("max_results", 10))

        if not query:
            return {"error": "`query` parameter is required."}

        if search_type not in ["articles", "journals"]:
            return {"error": "`type` must be 'articles' or 'journals'."}

        endpoint = f"{self.base_url}/{search_type}/{query}"
        params = {
            "pageSize": max(1, min(max_results, 100)),
        }
        try:
            resp = requests.get(endpoint, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            return {
                "error": "Network/API error calling DOAJ",
                "reason": str(e),
            }
        except ValueError:
            return {"error": "Failed to decode DOAJ response as JSON"}

        results = data.get("results", [])
        items = []
        if search_type == "articles":
            for r in results:
                b = r.get("bibjson", {})
                title = b.get("title")
                year = None
                try:
                    year = int((b.get("year") or 0))
                except Exception:
                    year = b.get("year")
                authors = [
                    a.get("name")
                    for a in b.get("author", [])
                    if a.get("name")
                ]
                doi = None
                for i in b.get("identifier", []):
                    if i.get("type") == "doi":
                        doi = i.get("id")
                        break
                url = None
                for link_item in b.get("link", []):
                    if (
                        link_item.get("type") == "fulltext"
                        or link_item.get("url")
                    ):
                        url = link_item.get("url")
                        break
                journal = (b.get("journal") or {}).get("title")
                items.append(
                    {
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "doi": doi,
                        "venue": journal,
                        "url": url,
                        "source": "DOAJ",
                    }
                )
        else:
            for r in results:
                b = r.get("bibjson", {})
                title = b.get("title")
                publisher = b.get("publisher")
                eissn = None
                pissn = None
                for i in b.get("identifier", []):
                    if i.get("type") == "eissn":
                        eissn = i.get("id")
                    if i.get("type") == "pissn":
                        pissn = i.get("id")
                homepage_url = None
                for link_item in b.get("link", []):
                    if link_item.get("url"):
                        homepage_url = link_item.get("url")
                        break
                subjects = [
                    s.get("term")
                    for s in b.get("subject", [])
                    if s.get("term")
                ]
                items.append(
                    {
                        "title": title,
                        "publisher": publisher,
                        "eissn": eissn,
                        "pissn": pissn,
                        "subjects": subjects,
                        "url": homepage_url,
                        "source": "DOAJ",
                    }
                )

        return items
