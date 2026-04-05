"""LLM calls via ASI1 API."""

import json
import logging
import os
import re
import time

import requests

log = logging.getLogger("llm")

API_BASE = "https://api.asi1.ai/v1"


def _get_api_key() -> str | None:
    return os.getenv("ASI_ONE_API_KEY") or os.getenv("LLM_API_KEY")


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 2048, retries: int = 3) -> str | None:
    api_key = _get_api_key()
    if not api_key:
        log.warning("No API key set — using fallback")
        return None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                f"{API_BASE}/chat/completions",
                json={
                    "model": "asi1-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                timeout=90,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            log.warning(f"LLM call failed (attempt {attempt}/{retries}): {status or e}")
            if attempt < retries and (not status or status >= 500):
                time.sleep(attempt * 5)

    log.error("LLM failed after all retries")
    return None


def summarize_items(items: list[dict]) -> list[dict]:
    BATCH = 8
    result = []

    for i in range(0, len(items), BATCH):
        batch = items[i : i + BATCH]
        batch_text = "\n\n".join(
            f"[{idx + 1}] {item['title']}\n{item.get('description') or '(no description)'}"
            for idx, item in enumerate(batch)
        )

        system = (
            "You are a sharp tech journalist. Summarize each item in 1-2 punchy sentences. "
            "Focus on what happened and why it matters. "
            "Return a JSON array of {\"index\": N, \"summary\": \"...\"} objects. Return ONLY valid JSON."
        )
        resp = call_llm(system, batch_text)

        if resp:
            try:
                cleaned = re.sub(r"```json\n?|```", "", resp).strip()
                parsed = json.loads(cleaned)
                for entry in parsed:
                    orig_idx = i + (entry["index"] - 1)
                    if orig_idx < len(items):
                        result.append({**items[orig_idx], "summary": entry["summary"]})
                continue
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                log.warning(f"Failed to parse LLM batch: {e}")

        for item in batch:
            desc = item.get("description", "")
            summary = (desc[:200].strip() + "...") if len(desc) > 120 else item["title"]
            result.append({**item, "summary": summary})

    log.info(f"Summarized {len(result)}/{len(items)} items")
    return result
