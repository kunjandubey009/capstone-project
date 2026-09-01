"""
Tool 1/5: web_search_tool

Stubbed provider-agnostic web search. In production, replace the body of
`_call_search_provider` with a real call (Tavily, Bing, SerpAPI, Google CSE,
etc.) using config.SEARCH_API_KEY. The function signature the agent sees
never has to change.
"""
from agents import function_tool
import config


def _call_search_provider(query: str, max_results: int) -> list[dict]:
    if config.SEARCH_API_KEY:
        # --- Real provider integration point ---
        # import requests
        # resp = requests.get("https://api.your-search-provider.com/search",
        #                      params={"q": query, "limit": max_results},
        #                      headers={"Authorization": f"Bearer {config.SEARCH_API_KEY}"})
        # return resp.json()["results"]
        pass

    # Deterministic offline stub so the tool always returns something usable.
    return [
        {
            "title": f"Industry report: {query}",
            "snippet": f"Simulated search result summarising public signal on '{query}'.",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
        }
        for _ in range(max_results)
    ]


@function_tool
def web_search_tool(query: str, max_results: int = 3) -> list[dict]:
    """Search the public web for information relevant to the business goal.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.
    """
    return _call_search_provider(query, max_results)
