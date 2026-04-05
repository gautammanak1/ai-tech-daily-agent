"""Scrape article content from URLs for deep research."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import trafilatura

log = logging.getLogger("scraper")


def scrape_url(url: str) -> dict | None:
    """Extract main content from a URL."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )
        if not text or len(text) < 100:
            return None

        metadata = trafilatura.extract(
            downloaded,
            output_format="json",
            include_comments=False,
        )

        return {
            "url": url,
            "text": text[:5000],
            "metadata": metadata,
        }
    except Exception as e:
        log.warning(f"Failed to scrape {url}: {e}")
        return None


def scrape_multiple(urls: list[str], max_workers: int = 5, max_urls: int = 10) -> list[dict]:
    """Scrape multiple URLs in parallel."""
    urls = urls[:max_urls]
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scrape_url, url): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    log.info(f"Scraped {len(results)}/{len(urls)} URLs successfully")
    return results


def extract_key_content(search_results: dict) -> str:
    """Scrape top URLs from search results and combine content."""
    urls = []

    for item in search_results.get("news", [])[:5]:
        if item.get("url"):
            urls.append(item["url"])

    for item in search_results.get("web", [])[:5]:
        if item.get("url"):
            urls.append(item["url"])

    scraped = scrape_multiple(urls)

    combined = []
    for s in scraped:
        combined.append(f"=== Source: {s['url']} ===\n{s['text']}\n")

    full_text = "\n".join(combined)
    log.info(f"Extracted {len(full_text)} chars from {len(scraped)} sources")
    return full_text
