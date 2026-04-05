"""Search for company logos and tech images via DuckDuckGo."""

import logging

from ddgs import DDGS

log = logging.getLogger("imgsearch")


def search_company_images(company: str, max_results: int = 5) -> list[dict]:
    """Search for images related to a company."""
    results = []
    queries = [
        f"{company} logo transparent",
        f"{company} AI technology product",
        f"{company} tech announcement 2026",
    ]

    with DDGS() as ddgs:
        for query in queries:
            try:
                for r in ddgs.images(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("image", ""),
                        "thumbnail": r.get("thumbnail", ""),
                        "source": r.get("source", ""),
                        "width": r.get("width", 0),
                        "height": r.get("height", 0),
                    })
            except Exception as e:
                log.warning(f"Image search failed for '{query}': {e}")

    unique = _dedupe(results)
    good = [img for img in unique if img.get("url") and img["url"].startswith("http")]
    log.info(f"Found {len(good)} images for '{company}'")
    return good


LOGO_DOMAINS = {
    "google": "google.com", "microsoft": "microsoft.com", "apple": "apple.com",
    "amazon": "amazon.com", "meta": "meta.com", "nvidia": "nvidia.com",
    "tesla": "tesla.com", "openai": "openai.com", "anthropic": "anthropic.com",
    "mistral": "mistral.ai", "cohere": "cohere.com", "huggingface": "huggingface.co",
    "cursor": "cursor.com", "replit": "replit.com", "vercel": "vercel.com",
    "perplexity": "perplexity.ai", "databricks": "databricks.com",
    "fetchai": "fetch.ai", "langchain": "langchain.com", "crewai": "crewai.com",
    "composio": "composio.dev", "daytona": "daytona.io",
    "stabilityai": "stability.ai", "xai": "x.ai", "samsung": "samsung.com",
    "intel": "intel.com", "amd": "amd.com", "ibm": "ibm.com",
    "oracle": "oracle.com", "salesforce": "salesforce.com", "adobe": "adobe.com",
    "groq": "groq.com", "pinecone": "pinecone.io", "supabase": "supabase.com",
    "snowflake": "snowflake.com", "runway": "runwayml.com",
    "elevenlabs": "elevenlabs.io", "midjourney": "midjourney.com",
    "deepseek": "deepseek.com", "scaleai": "scale.com",
}


def get_best_images(company: str, slug: str = "") -> dict[str, str]:
    """Get categorized images for the article."""
    result = {}

    domain = LOGO_DOMAINS.get(slug) or LOGO_DOMAINS.get(company.lower().replace(" ", ""))
    if domain:
        result["logo"] = f"https://logo.clearbit.com/{domain}"

    images = search_company_images(company)
    for img in images:
        url = img["url"]
        title = img["title"].lower()

        if any(kw in title for kw in ["product", "tech", "ai", "launch", "screenshot"]) and "hero" not in result:
            result["hero"] = url
        elif "banner" not in result and "logo" not in title:
            result["banner"] = url

        if len(result) >= 3:
            break

    if not result.get("hero") and images:
        result["hero"] = images[0]["url"]

    log.info(f"Selected {len(result)} images: {list(result.keys())}")
    return result


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        key = item.get("url", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
