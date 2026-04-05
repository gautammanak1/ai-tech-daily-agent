"""LLM and image generation via ASI1 API."""

import base64
import json
import logging
import os
import re
import time
from pathlib import Path

import requests

log = logging.getLogger("llm")

API_BASE = "https://api.asi1.ai/v1"
IMAGE_URL = f"{API_BASE}/image/generate"


def _get_api_key() -> str | None:
    return os.getenv("LLM_API_KEY")

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


def _extract_base64(data: dict) -> str | None:
    """Extract base64 image data from any API response shape."""
    candidates = []

    for key in ("images", "data", "results"):
        val = data.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    for field in ("b64_json", "base64", "image", "data"):
                        s = item.get(field)
                        if isinstance(s, str) and len(s) > 100:
                            candidates.append(s)
                elif isinstance(item, str) and len(item) > 100:
                    candidates.append(item)
        elif isinstance(val, str) and len(val) > 100:
            candidates.append(val)

    if not candidates:
        return None

    b64 = candidates[0]
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return b64


def generate_image(prompt: str, date_str: str, name: str, images_dir: str = "images") -> str | None:
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        resp = requests.post(
            IMAGE_URL,
            json={"model": "asi1-mini", "prompt": prompt, "size": "1024x1024"},
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

        url = (data.get("images") or [{}])[0].get("url")
        if url and url.startswith("http"):
            return url

        b64 = _extract_base64(data)
        if b64:
            out_dir = Path(images_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{name}-{date_str}.png"
            filepath = out_dir / filename
            filepath.write_bytes(base64.b64decode(b64))
            log.info(f"Image saved: {filename}")
            return f"{images_dir}/{filename}"

        log.warning(f"Unexpected image response: {list(data.keys())}")
        return None
    except Exception as e:
        log.warning(f"Image generation failed: {e}")
        return None


def generate_article_images(trends: list[dict], date_str: str) -> dict[str, str]:
    top_trend = trends[0]["topic"] if trends else "artificial intelligence"
    prompts = {
        "banner": f'Modern tech newsletter banner: "{top_trend}" theme, futuristic digital art, dark background, glowing blue-purple accents, no text',
        "ai": "Neural network brain illustration, glowing nodes, abstract modern tech art, blue cyan tones",
        "agents": "Autonomous AI agents collaborating in digital workspace, purple teal color scheme, futuristic",
        "web3": "Blockchain decentralized network illustration, interconnected nodes, gold dark theme",
    }

    images = {}
    for key, prompt in prompts.items():
        url = generate_image(prompt, date_str, key)
        if url:
            images[key] = url
    log.info(f"Generated {len(images)}/{len(prompts)} images")
    return images
