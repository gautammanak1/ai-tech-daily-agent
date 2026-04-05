"""Fetch framework repo updates and search trending AI agent repos."""

import logging
import os
from datetime import datetime, timedelta

import requests

from config.sources import TRACKED_FRAMEWORK_REPOS

log = logging.getLogger("github")

SEARCH_QUERIES = [
    "ai agent", "llm agent framework", "mcp server",
    "agentic ai", "autonomous agent", "agent-to-agent",
    "uagents", "crewai", "langchain agent",
]


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "AI-Tech-Daily-Agent/1.0"}
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"token {token.strip()}"
    return h


def get_framework_updates() -> list[dict]:
    """Get latest release/activity for tracked framework repos."""
    results = []
    headers = _headers()

    for repo_info in TRACKED_FRAMEWORK_REPOS:
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        label = repo_info["label"]

        try:
            resp = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()

            release_info = _get_latest_release(owner, repo, headers)

            results.append({
                "name": f"{owner}/{repo}",
                "label": label,
                "url": data["html_url"],
                "description": (data.get("description") or "")[:200],
                "stars": data["stargazers_count"],
                "language": data.get("language"),
                "updated_at": data.get("pushed_at", ""),
                "latest_release": release_info,
                "type": "tracked",
            })
        except Exception as e:
            log.warning(f"Failed to fetch {owner}/{repo}: {e}")

    results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    log.info(f"Tracked {len(results)}/{len(TRACKED_FRAMEWORK_REPOS)} framework repos")
    return results


def _get_latest_release(owner: str, repo: str, headers: dict) -> dict | None:
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/releases",
            headers=headers,
            params={"per_page": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            releases = resp.json()
            if releases:
                r = releases[0]
                return {
                    "tag": r.get("tag_name", ""),
                    "name": r.get("name", ""),
                    "published_at": r.get("published_at", ""),
                    "url": r.get("html_url", ""),
                }
    except Exception:
        pass
    return None


def search_trending_repos() -> list[dict]:
    """Search GitHub for new trending AI agent repos."""
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    all_repos: list[dict] = []
    headers = _headers()

    for query in SEARCH_QUERIES:
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": f"{query} created:>{one_week_ago}", "sort": "stars", "order": "desc", "per_page": 5},
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            for r in resp.json().get("items", []):
                all_repos.append({
                    "name": r["full_name"],
                    "url": r["html_url"],
                    "description": (r.get("description") or "")[:200],
                    "stars": r["stargazers_count"],
                    "language": r.get("language"),
                    "type": "trending",
                })
        except Exception as e:
            log.warning(f'GitHub search failed for "{query}": {e}')

    seen = set()
    unique = []
    for r in all_repos:
        if r["name"] not in seen:
            seen.add(r["name"])
            unique.append(r)

    unique.sort(key=lambda x: x["stars"], reverse=True)
    top = unique[:10]
    log.info(f"Found {len(top)} trending repos")
    return top


def get_all_repos() -> dict:
    """Get both tracked frameworks and trending new repos."""
    frameworks = get_framework_updates()
    trending = search_trending_repos()
    return {"frameworks": frameworks, "trending": trending}
