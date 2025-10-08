import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("PubMedTool")
class PubMedTool(BaseTool):
    """
    Search PubMed using NCBI E-utilities (esearch + esummary) and return
    articles.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.esearch_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        self.esummary_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        )

    def run(self, arguments):
        query = arguments.get("query")
        limit = int(arguments.get("limit", 10))
        api_key = arguments.get("api_key")  # optional NCBI API key
        if not query:
            return {"error": "`query` parameter is required."}
        return self._search(query, limit, api_key)

    def _search(self, query, limit, api_key=None):
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max(1, min(limit, 200)),
            "retmode": "json",
        }
        if api_key:
            params["api_key"] = api_key

        try:
            r = requests.get(self.esearch_url, params=params, timeout=20)
        except requests.RequestException as e:
            return {
                "error": "Network error calling PubMed esearch",
                "reason": str(e),
            }
        if r.status_code != 200:
            return {
                "error": f"PubMed esearch error {r.status_code}",
                "reason": r.reason,
            }

        data = r.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        summary_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
        }
        if api_key:
            summary_params["api_key"] = api_key

        try:
            s = requests.get(
                self.esummary_url,
                params=summary_params,
                timeout=20,
            )
        except requests.RequestException as e:
            return {
                "error": "Network error calling PubMed esummary",
                "reason": str(e),
            }
        if s.status_code != 200:
            return {
                "error": f"PubMed esummary error {s.status_code}",
                "reason": s.reason,
            }

        result = s.json().get("result", {})
        uids = result.get("uids", [])
        articles = []
        for uid in uids:
            rec = result.get(uid, {})
            title = rec.get("title")
            journal = rec.get("fulljournalname") or rec.get("source")
            year = None
            pubdate = rec.get("pubdate")
            if pubdate and len(pubdate) >= 4 and pubdate[:4].isdigit():
                year = int(pubdate[:4])
            doi = None
            for id_obj in rec.get("articleids", []):
                if id_obj.get("idtype") == "doi":
                    doi = id_obj.get("value")
                    break
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            articles.append(
                {
                    "title": title,
                    "journal": journal,
                    "year": year,
                    "doi": doi,
                    "url": url,
                }
            )

        return articles
