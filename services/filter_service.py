"""Filter and rank news items by AI/Web3/Agent relevance."""

import logging
import math

from config.sources import AI_KEYWORDS, AGENT_KEYWORDS, WEB3_KEYWORDS, MARKET_KEYWORDS, ALL_KEYWORDS

log = logging.getLogger("filter")


def classify_item(item: dict) -> dict:
    text = f"{item['title']} {item.get('description', '')}".lower()

    scores = {"ai": 0, "agents": 0, "web3": 0, "market": 0}
    for kw in AI_KEYWORDS:
        if kw in text:
            scores["ai"] += 3 if " " in kw else 2
    for kw in AGENT_KEYWORDS:
        if kw in text:
            scores["agents"] += 4 if " " in kw else 3
    for kw in WEB3_KEYWORDS:
        if kw in text:
            scores["web3"] += 3 if " " in kw else 2
    for kw in MARKET_KEYWORDS:
        if kw in text:
            scores["market"] += 2 if " " in kw else 1

    if item.get("category") == "learning":
        category = "learning"
    else:
        category = max(scores, key=scores.get) if max(scores.values()) > 0 else (item.get("category") or "ai")

    total = sum(scores.values())
    total += item.get("source_weight", 0)
    if item.get("score"):
        total += min(math.log10(max(item["score"], 1)), 3)

    return {**item, "category": category, "relevance": total}


def filter_and_rank(items: list[dict], min_score: int = 1, limit: int = 50) -> list[dict]:
    scored = [classify_item(i) for i in items]
    scored = [i for i in scored if i["relevance"] >= min_score]
    scored.sort(key=lambda x: x["relevance"], reverse=True)
    filtered = scored[:limit]

    counts = {}
    for i in filtered:
        counts[i["category"]] = counts.get(i["category"], 0) + 1
    log.info(f"Filtered {len(items)} → {len(filtered)} items {counts}")

    return filtered


def extract_trends(items: list[dict], top_n: int = 5) -> list[dict]:
    freq: dict[str, int] = {}
    for item in items:
        text = f"{item['title']} {item.get('description', '')}".lower()
        for kw in ALL_KEYWORDS:
            if kw in text and len(kw) > 2:
                freq[kw] = freq.get(kw, 0) + 1

    sorted_topics = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"topic": t, "count": c} for t, c in sorted_topics]


def split_by_category(items: list[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {"ai": [], "agents": [], "web3": [], "market": [], "learning": []}
    for item in items:
        cat = item.get("category", "ai")
        result.setdefault(cat, []).append(item)
    return result
