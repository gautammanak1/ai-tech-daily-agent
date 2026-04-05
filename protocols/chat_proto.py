"""Chat protocol for AI Tech Daily agent.

Users can chat with this agent to generate news articles on demand.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from services.news_service import fetch_all_news
from services.filter_service import filter_and_rank, extract_trends
from services.llm_service import summarize_items
from services.github_service import get_all_repos
from services.article_service import generate_article
from services.publish_service import save_article, commit_and_push, publish_to_public_repo

daily_chat_proto = Protocol(spec=chat_protocol_spec)


def _create_text(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=None,
        content=[TextContent(type="text", text=text)],
    )


async def _ack(ctx: Context, sender: str, msg: ChatMessage) -> None:
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )


async def _run_pipeline(ctx: Context) -> str:
    ctx.logger.info("Starting news pipeline...")

    raw = await asyncio.to_thread(fetch_all_news)
    ctx.logger.info(f"Fetched {len(raw)} items")

    ranked = await asyncio.to_thread(filter_and_rank, raw)
    ctx.logger.info(f"Filtered to {len(ranked)} items")

    summarized = await asyncio.to_thread(summarize_items, ranked)
    trends = extract_trends(ranked)
    repos = await asyncio.to_thread(get_all_repos)

    dt = datetime.utcnow()
    article = await asyncio.to_thread(generate_article, summarized, trends, repos, dt)
    date_str = dt.strftime("%Y-%m-%d")

    filename, filepath = save_article(article, date_str)
    ctx.logger.info(f"Saved: {filename}")

    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    if not dry_run:
        await asyncio.to_thread(commit_and_push, filepath, date_str)
        await asyncio.to_thread(publish_to_public_repo, article, date_str)

    return f"Article generated: **{filename}**\n\nTopics: {', '.join(t['topic'] for t in trends[:5])}\nSources: {len(raw)} items from 12+ feeds"


@daily_chat_proto.on_message(model=ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage) -> None:
    ctx.logger.info(f"ChatMessage from {sender}")
    await _ack(ctx, sender, msg)

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Session started with {sender}")
            await ctx.send(sender, _create_text(
                "Welcome to **AI & Tech Daily Agent**! I generate daily AI/Web3/tech news articles.\n\n"
                "Commands:\n"
                "- **generate** — generate today's article\n"
                "- **status** — check last generation\n"
                "- **help** — show commands"
            ))

        elif isinstance(item, TextContent):
            user_text = (item.text or "").strip().lower()
            ctx.logger.info(f"Message: {user_text}")

            if any(kw in user_text for kw in ["generate", "article", "news", "run", "start"]):
                await ctx.send(sender, _create_text("Starting article generation pipeline... This takes 1-2 minutes."))
                try:
                    result = await _run_pipeline(ctx)
                    await ctx.send(sender, _create_text(result))
                except Exception as e:
                    ctx.logger.error(f"Pipeline failed: {e}")
                    await ctx.send(sender, _create_text(f"Pipeline failed: {e}"))

            elif "status" in user_text:
                from pathlib import Path
                articles_dir = Path("articles")
                if articles_dir.exists():
                    files = sorted(articles_dir.glob("*.md"), reverse=True)
                    if files:
                        latest = files[0].name
                        count = len(files)
                        await ctx.send(sender, _create_text(f"Latest article: **{latest}**\nTotal articles: {count}"))
                    else:
                        await ctx.send(sender, _create_text("No articles generated yet."))
                else:
                    await ctx.send(sender, _create_text("Articles directory not found."))

            elif "help" in user_text:
                await ctx.send(sender, _create_text(
                    "**Commands:**\n"
                    "- `generate` — run pipeline and create article\n"
                    "- `status` — check latest article\n"
                    "- `help` — this message"
                ))
            else:
                await ctx.send(sender, _create_text(
                    f'I received: "{user_text}"\n\nType **generate** to create an article, or **help** for commands.'
                ))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Session ended with {sender}")
            await ctx.send(sender, _create_text("Session ended. Goodbye!"))


@daily_chat_proto.on_message(model=ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info(f"Ack from {sender} for {msg.acknowledged_msg_id}")
