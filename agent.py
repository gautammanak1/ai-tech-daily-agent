#!/usr/bin/env python3
"""
AI Tech Daily Agent

A uAgent that generates daily AI/Web3/tech news articles.
Supports chat protocol for on-demand generation and CLI mode for scheduled runs.
"""

import asyncio
import logging
import os
import sys

import dotenv
from uagents import Agent, Context

from protocols.chat_proto import daily_chat_proto, _run_pipeline

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


async def run_cli_pipeline():
    """Run the full pipeline once (for GitHub Actions / CLI)."""
    from services.news_service import fetch_all_news
    from services.filter_service import filter_and_rank, extract_trends
    from services.llm_service import summarize_items
    from services.github_service import get_all_repos
    from services.article_service import generate_article
    from services.publish_service import save_article, commit_and_push, publish_to_public_repo
    from datetime import datetime

    log.info("=== AI Tech Daily Agent — CLI Mode ===")

    raw = fetch_all_news()
    log.info(f"Fetched {len(raw)} items")

    ranked = filter_and_rank(raw)
    log.info(f"Filtered to {len(ranked)} items")

    if not ranked:
        log.warning("No relevant items found. Using top raw items.")
        ranked = raw[:20]

    summarized = summarize_items(ranked)
    trends = extract_trends(ranked)
    repos = get_all_repos()

    dt = datetime.utcnow()
    date_str = dt.strftime("%Y-%m-%d")

    article = generate_article(summarized, trends, repos, dt)

    filename, filepath = save_article(article, date_str)
    log.info(f"Article saved: {filename}")

    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    if not dry_run:
        commit_and_push(filepath, date_str, dry_run=False)
        publish_to_public_repo(article, date_str)
    else:
        log.info("DRY_RUN mode — skipping git operations")

    log.info(f"Done — {filename}")


def run_agent():
    """Run as a uAgent with chat protocol."""
    agent = Agent(
        name="ai_tech_daily_agent",
        port=8030,
        seed=_load_seed(),
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
        asyncio.run(run_cli_pipeline())
    else:
        run_agent()
