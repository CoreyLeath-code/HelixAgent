"""
web_search.py
=============
Tool for the Agentic AI Assistant: performs a web search and returns a
short summary suitable for LLM consumption.

Real implementations could use:
  • SerpAPI
  • Bing Web Search (Azure Cognitive Services)
  • Google Programmable Search

For demo purposes this module:
  1. Queries DuckDuckGo’s HTML results page
  2. Extracts the top N result titles/snippets
  3. Returns a concatenated summary string

Dependencies:
    pip install ddgs
"""

from ddgs import DDGS

def search_and_summarize(query: str, max_results: int = 5) -> str:
    """
    Run a web search and summarize the top results.

    Parameters
    ----------
    query : str
        The user’s search question.
    max_results : int
        How many results to consider (default 5).

    Returns
    -------
    str
        A multi-line summary of result titles + snippets.
    """
    summary_lines = []
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        for idx, res in enumerate(results, 1):
            title = res.get("title", "")
            snippet = res.get("body", "")
            summary_lines.append(f"{idx}. {title} — {snippet}")

    return "\n".join(summary_lines)


# Quick CLI test
if __name__ == "__main__":
    print(search_and_summarize("latest advances in agentic AI", 3))
