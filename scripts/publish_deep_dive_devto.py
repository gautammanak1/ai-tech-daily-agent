#!/usr/bin/env python3
"""Publish PROJECT_DEEP_DIVE.md to Dev.to (images must use absolute raw GitHub URLs)."""

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

# Dev.to allows at most 4 tags
TAGS = ["ai", "programming", "architecture", "tutorial"]


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
    )
    desc = desc[:300]

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

    print(f"Publishing {MD_FILE.name} ({len(body)} chars body) to Dev.to…")
    resp = requests.post(DEVTO_API, json=payload, headers=headers, timeout=120)
    if resp.status_code == 201:
        data = resp.json()
        url = data.get("url", "")
        print(f"OK: {url}")
        return 0
    try:
        err = resp.json()
    except json.JSONDecodeError:
        err = resp.text
    print(f"Dev.to API {resp.status_code}: {err}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
