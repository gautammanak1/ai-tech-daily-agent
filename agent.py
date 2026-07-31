#!/usr/bin/env python3
"""
AI Tech Daily Agent

A uAgent that generates daily deep-dive articles about AI/tech companies.
Each day picks a different company, does real-time web research, and writes a 300+ line article.
Supports chat protocol for on-demand generation and CLI mode for scheduled runs.
"""

import asyncio
import logging
import os
import sys

import dotenv
from uagents import Agent, Context

from protocols.chat_proto import daily_chat_proto

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("agent")


def _load_seed() -> str:
    seed = os.getenv("AGENT_SEED")
    if seed:
        return seed
    return "ai-tech-daily-agent-default-seed-change-me"


def run_pipeline(
    dry_run: bool = False,
    topic: str | None = None,
    join_series: bool = True,
) -> str:
    """Run the full pipeline once. Returns summary string.

    When ``topic`` is set, that company/topic is used instead of daily rotation.
    When ``join_series`` is False, the Dev.to post is standalone (not in the series).
    """
    from datetime import datetime
    from services.company_picker import pick_company, resolve_company
    from services.web_search_service import search_all
    from services.web_scraper_service import extract_key_content
    from services.image_search_service import get_best_images
    from services.github_service import get_framework_updates
    from services.article_service import generate_article
    from services.publish_service import publish_article
    from services.devto_service import publish_to_devto

    log.info("=== AI Tech Daily Agent ===")

    if topic:
        company = resolve_company(topic)
        log.info(f"Manual topic: {company['name']}")
    else:
        company = pick_company()
        log.info(f"Today's company: {company['name']}")

    log.info("Searching the web (real-time)...")
    search_data = search_all(company["name"])

    log.info("Scraping top articles...")
    scraped = extract_key_content(search_data)

    log.info("Searching for images...")
    images = get_best_images(company["name"], company["slug"])

    log.info("Fetching framework repo data...")
    frameworks = get_framework_updates()

    log.info("Generating article...")
    article, filename = generate_article(company, search_data, scraped, frameworks, images)

    line_count = len(article.splitlines())
    log.info(f"Article: {filename} ({line_count} lines)")

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    publish_article(article, filename, company["name"], date_str, dry_run=dry_run)

    series = "AI Tech Daily" if join_series else ""
    log.info(
        "Publishing to Dev.to%s...",
        " (standalone, no series)" if not join_series else "",
    )
    devto_url = publish_to_devto(
        article,
        company["name"],
        company["slug"],
        filename=filename,
        series=series,
    )
    if devto_url:
        log.info(f"Dev.to article: {devto_url}")

    return f"**{company['name']}** — {filename} ({line_count} lines)"


def _parse_cli_args(argv: list[str]) -> tuple[str | None, bool]:
    """Parse --topic / TOPIC and series flags from CLI argv + env."""
    topic: str | None = None
    join_series = True

    args = list(argv)
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--topic", "-t") and i + 1 < len(args):
            topic = args[i + 1]
            i += 2
            continue
        if arg.startswith("--topic="):
            topic = arg.split("=", 1)[1]
            i += 1
            continue
        if arg in ("--no-series", "--standalone"):
            join_series = False
            i += 1
            continue
        i += 1

    if not topic:
        topic = (os.getenv("TOPIC") or "").strip() or None

    env_series = (os.getenv("DEVTO_JOIN_SERIES") or "").strip().lower()
    if env_series in ("0", "false", "no", "off"):
        join_series = False
    elif env_series in ("1", "true", "yes", "on"):
        join_series = True
    elif topic and env_series == "":
        # Manual topic runs default to standalone posts unless explicitly joining.
        join_series = False

    return topic, join_series


async def run_cli_pipeline(argv: list[str] | None = None):
    """CLI entry point."""
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    topic, join_series = _parse_cli_args(argv or sys.argv[2:])
    result = run_pipeline(dry_run=dry_run, topic=topic, join_series=join_series)
    log.info(f"Done — {result}")


def run_agent():
    """Run as a uAgent with chat protocol."""
    agent = Agent(
        name="ai_tech_daily_agent",
        port=8030,
        seed=_load_seed(),
        mailbox=True,
    )

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"AI Tech Daily Agent started: {agent.address}")
        ctx.logger.info("Ready — send 'generate' to create an article")

    agent.include(daily_chat_proto, publish_manifest=True)
    log.info("Starting uAgent...")
    agent.run()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--run", "run", "--cli", "cli"):
        asyncio.run(run_cli_pipeline(sys.argv[2:]))
    else:
        run_agent()
