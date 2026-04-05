"""Real-time web search using DuckDuckGo."""

import logging
from ddgs import DDGS

log = logging.getLogger("websearch")


def search_company_news(company: str, max_results: int = 20) -> list[dict]:
    """Search for latest news about a company."""
    results = []
    queries = [
        f"{company} latest news 2026",
        f"{company} AI announcement",
        f"{company} product launch update",
    ]

    with DDGS() as ddgs:
        for query in queries:
            try:
                for r in ddgs.news(query, max_results=max_results // len(queries)):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "body": r.get("body", ""),
                        "source": r.get("source", ""),
                        "date": r.get("date", ""),
                    })
            except Exception as e:
                log.warning(f"News search failed for '{query}': {e}")

    log.info(f"Found {len(results)} news items for '{company}'")
    return _dedupe(results)


def search_company_web(company: str, max_results: int = 15) -> list[dict]:
    """General web search about a company."""
    results = []
    queries = [
        f"{company} AI technology 2026",
        f"{company} developer tools platform",
        f"{company} open source projects GitHub",
    ]

    with DDGS() as ddgs:
        for query in queries:
            try:
                for r in ddgs.text(query, max_results=max_results // len(queries)):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "body": r.get("body", ""),
                    })
            except Exception as e:
                log.warning(f"Web search failed for '{query}': {e}")

    log.info(f"Found {len(results)} web results for '{company}'")
    return _dedupe(results)


def search_company_github(company: str) -> list[dict]:
    """Search for company's GitHub repos and activity."""
    results = []

    with DDGS() as ddgs:
        try:
            for r in ddgs.text(f"site:github.com {company} AI agent", max_results=10):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", ""),
                })
        except Exception as e:
            log.warning(f"GitHub search failed: {e}")

    log.info(f"Found {len(results)} GitHub results for '{company}'")
    return results


def search_all(company: str) -> dict:
    """Run all searches for a company and return combined results."""
    return {
        "news": search_company_news(company),
        "web": search_company_web(company),
        "github": search_company_github(company),
    }


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        key = item.get("url", item.get("title", ""))
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
