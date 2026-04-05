"""Fetch news from RSS feeds and Hacker News API."""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import requests

from config.sources import RSS_FEEDS, HACKERNEWS_TOP_URL, HACKERNEWS_ITEM_URL, HACKERNEWS_MAX_ITEMS

log = logging.getLogger("news")


def fetch_rss_feed(feed: dict) -> list[dict]:
    try:
        parsed = feedparser.parse(feed["url"])
        items = []
        for entry in parsed.entries[:25]:
            items.append({
                "title": (entry.get("title") or "").strip(),
                "link": entry.get("link", ""),
                "description": (entry.get("summary") or "")[:500].strip(),
                "source": feed["name"],
                "source_weight": feed["weight"],
                "category": feed["category"],
                "origin": "rss",
            })
        log.info(f"Fetched {len(items)} items from {feed['name']}")
        return items
    except Exception as e:
        log.warning(f"Failed to fetch {feed['name']}: {e}")
        return []


def fetch_hackernews() -> list[dict]:
    try:
        resp = requests.get(HACKERNEWS_TOP_URL, timeout=10)
        ids = resp.json()[:HACKERNEWS_MAX_ITEMS]

        items = []
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(requests.get, f"{HACKERNEWS_ITEM_URL}/{sid}.json", timeout=8): sid for sid in ids}
            for future in as_completed(futures):
                try:
                    story = future.result().json()
                    if story and story.get("type") == "story" and story.get("title"):
                        items.append({
                            "title": story["title"].strip(),
                            "link": story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
                            "description": "",
                            "source": "Hacker News",
                            "source_weight": 2,
                            "category": "tech",
                            "origin": "hackernews",
                            "score": story.get("score", 0),
                        })
                except Exception:
                    pass

        log.info(f"Fetched {len(items)} stories from Hacker News")
        return items
    except Exception as e:
        log.warning(f"Failed to fetch Hacker News: {e}")
        return []


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", title.lower()).strip().split()[:8]


def deduplicate(items: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for item in items:
        key = " ".join(normalize_title(item["title"]))
        existing = seen.get(key)
        if not existing or item.get("source_weight", 0) > existing.get("source_weight", 0):
            seen[key] = item
    return list(seen.values())


def fetch_all_news() -> list[dict]:
    log.info("Fetching news from all sources...")
    all_items = []

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(fetch_rss_feed, feed) for feed in RSS_FEEDS]
        futures.append(pool.submit(fetch_hackernews))
        for future in as_completed(futures):
            all_items.extend(future.result())

    log.info(f"Raw items: {len(all_items)}")
    unique = deduplicate(all_items)
    log.info(f"After dedup: {len(unique)}")
    return unique
