import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("MedRxivTool")
class MedRxivTool(BaseTool):
    """
    Search medRxiv preprints using medRxiv's API (same interface as bioRxiv).

    Arguments:
        query (str): Search term
        max_results (int): Max results to return (default 10, max 200)
    """

    def __init__(
        self,
        tool_config,
        base_url="https://api.medrxiv.org/details",
    ):
        super().__init__(tool_config)
        self.base_url = base_url

    def run(self, arguments=None):
        arguments = arguments or {}
        query = arguments.get("query")
        max_results = int(arguments.get("max_results", 10))
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, max_results)

    def _search(self, query, max_results):
        # Use date range search for recent preprints
        # Format: /medrxiv/{start_date}/{end_date}/{cursor}/json
        from datetime import datetime, timedelta

        # Search last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        url = (f"{self.base_url}/medrxiv/"
               f"{start_date.strftime('%Y-%m-%d')}/"
               f"{end_date.strftime('%Y-%m-%d')}/0/json")

        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            return {
                "error": "Network/API error calling medRxiv",
                "reason": str(e),
            }
        except ValueError:
            return {"error": "Failed to decode medRxiv response as JSON"}

        results = []
        # The API returns a dictionary with a 'collection' key
        collection = data.get("collection", [])
        if not isinstance(collection, list):
            return {"error": "Unexpected API response format"}

        for item in collection:
            title = item.get("title")
            authors = item.get("authors", "")
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(";") if a.strip()]
            elif isinstance(authors, list):
                authors = [str(a).strip() for a in authors if str(a).strip()]
            else:
                authors = []

            year = None
            date = item.get("date")
            if date and len(date) >= 4 and date[:4].isdigit():
                year = int(date[:4])

            doi = item.get("doi")
            url = f"https://www.medrxiv.org/content/{doi}" if doi else None

            # Filter by query if provided
            if query and query.lower() not in (title or "").lower():
                continue

            results.append(
                {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "doi": doi,
                    "url": url,
                    "abstract": item.get("abstract", ""),
                    "source": "medRxiv",
                }
            )

        return results[:max_results]
