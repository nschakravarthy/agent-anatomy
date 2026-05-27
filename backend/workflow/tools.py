import os
from functools import lru_cache

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from tavily import AsyncTavilyClient

@lru_cache(maxsize=1)
def _tavily_client() -> AsyncTavilyClient:
    return AsyncTavilyClient(api_key = os.environ.get("TAVILY_API_KEY"))

@tool
async def tavily_search(query:str) -> str:
    """
    Search the web for current information
    Use this for anything that may have changed since your training cutoff,
    breaking news, current events, or facts you're not confident about.
    Returns the top results as a compact text summary.
    """
    client = _tavily_client()
    result = await client.search(query = query, max_results = 3, search_depth = "basic")
    print("Web search result: ", result)
    lines = []
    for r in result.get("results",[]):
        snippet = (r.get("content") or "")[:300]
        lines.append(f"- {r.get('title')} ({r.get('url')})\n  {snippet}")
    return "\n".join(lines) if lines else "No results."
