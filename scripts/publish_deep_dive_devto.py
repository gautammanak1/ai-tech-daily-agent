#!/usr/bin/env python3
"""Publish or update PROJECT_DEEP_DIVE.md on Dev.to.

Uses jsDelivr URLs for images in the markdown (Dev.to often fails to proxy
raw.githubusercontent.com; jsDelivr serves the same Git files with reliable CORS).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import dotenv
import requests

ROOT = Path(__file__).resolve().parents[1]
dotenv.load_dotenv(ROOT / ".env")

DEVTO_API = "https://dev.to/api/articles"
MD_FILE = ROOT / "PROJECT_DEEP_DIVE.md"
CANONICAL_SUBSTR = "PROJECT_DEEP_DIVE.md"

TAGS = ["ai", "programming", "architecture", "tutorial"]


def _find_existing_article_id(api_key: str) -> int | None:
    """Find our deep-dive post by canonical_url (set on first publish)."""
    headers = {"api-key": api_key, "User-Agent": "AI-Tech-Daily-Agent/1.0"}
    page = 1
    while page <= 10:
        resp = requests.get(
            f"{DEVTO_API}/me",
            params={"page": page, "per_page": 100},
            headers=headers,
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"Warning: articles/me page {page}: {resp.status_code}", file=sys.stderr)
            return None
        data = resp.json()
        # API returns a list of article summary dicts
        for article in data:
            canonical = article.get("canonical_url") or ""
            if CANONICAL_SUBSTR in canonical:
                return int(article["id"])
            title = article.get("title") or ""
            if "Complete Architecture Deep Dive" in title:
                return int(article["id"])
        if len(data) < 100:
            break
        page += 1
    return None


def main() -> int:
    api_key = (os.getenv("DEVTO_API_KEY") or "").strip()
    if not api_key:
        print("Error: DEVTO_API_KEY not set. Add it to .env (see .env.example).", file=sys.stderr)
        return 1

    if not MD_FILE.is_file():
        print(f"Error: {MD_FILE} not found.", file=sys.stderr)
        return 1

    raw = MD_FILE.read_text(encoding="utf-8")
    lines = raw.split("\n")
    title = "Architecture Deep Dive"
    body_lines: list[str] = []
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line[2:].strip()[:128]
            continue
        body_lines.append(line)
    body = "\n".join(body_lines).strip()

    body += (
        "\n\n---\n\n"
        "*Source: [PROJECT_DEEP_DIVE.md on GitHub]"
        "(https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/PROJECT_DEEP_DIVE.md) "
        "— [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent).*"
    )

    canonical = (
        "https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/PROJECT_DEEP_DIVE.md"
    )
    desc = (
        "Complete architecture deep dive: uAgents pipeline, services, data flow, "
        "deployment, and patterns — with diagrams."
    )[:300]

    payload = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": body,
            "tags": TAGS,
            "canonical_url": canonical,
            "description": desc,
        }
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "User-Agent": "AI-Tech-Daily-Agent/1.0",
    }

    override_id = (os.getenv("DEVTO_DEEP_DIVE_ARTICLE_ID") or "").strip()
    article_id: int | None = int(override_id) if override_id.isdigit() else None
    if article_id is None:
        print("Looking for existing Dev.to article (canonical URL or title match)…")
        article_id = _find_existing_article_id(api_key)

    if article_id is not None:
        url = f"{DEVTO_API}/{article_id}"
        print(f"Updating article id={article_id} ({len(body)} chars)…")
        resp = requests.put(url, json=payload, headers=headers, timeout=120)
        ok_code = 200
    else:
        url = DEVTO_API
        print(f"Creating new article ({len(body)} chars)…")
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        ok_code = 201

    if resp.status_code == ok_code:
        data = resp.json()
        out_url = data.get("url", "")
        print(f"OK: {out_url}")
        return 0
    try:
        err = resp.json()
    except json.JSONDecodeError:
        err = resp.text
    print(f"Dev.to API {resp.status_code}: {err}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
