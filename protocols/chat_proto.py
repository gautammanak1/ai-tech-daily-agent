"""Chat protocol for AI Tech Daily agent.

Users can chat to trigger article generation or check status.
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
    from agent import run_pipeline
    ctx.logger.info("Starting pipeline...")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    result = await asyncio.to_thread(run_pipeline, dry_run)
    return result


@daily_chat_proto.on_message(model=ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage) -> None:
    ctx.logger.info(f"ChatMessage from {sender}")
    await _ack(ctx, sender, msg)

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Session started with {sender}")
            await ctx.send(sender, _create_text(
                "Welcome to **AI & Tech Daily Agent**!\n\n"
                "I write daily deep-dive articles about AI/tech companies.\n\n"
                "Commands:\n"
                "- **generate** — pick a company and write today's article\n"
                "- **status** — check recent articles\n"
                "- **help** — show commands"
            ))

        elif isinstance(item, TextContent):
            user_text = (item.text or "").strip().lower()
            ctx.logger.info(f"Message: {user_text}")

            if any(kw in user_text for kw in ["generate", "article", "news", "run", "start", "write"]):
                await ctx.send(sender, _create_text("Starting deep-dive pipeline... This takes 2-3 minutes."))
                try:
                    result = await _run_pipeline(ctx)
                    await ctx.send(sender, _create_text(f"Article published: {result}"))
                except Exception as e:
                    ctx.logger.error(f"Pipeline failed: {e}")
                    await ctx.send(sender, _create_text(f"Pipeline failed: {e}"))

            elif "status" in user_text:
                try:
                    from services.company_picker import get_history
                    history = get_history()
                    if history:
                        recent = history[-5:]
                        lines = "\n".join(f"- **{h['name']}** ({h['date']})" for h in reversed(recent))
                        await ctx.send(sender, _create_text(f"Recent articles:\n{lines}\n\nTotal: {len(history)}"))
                    else:
                        await ctx.send(sender, _create_text("No articles generated yet."))
                except Exception:
                    await ctx.send(sender, _create_text("No history available."))

            elif "help" in user_text:
                await ctx.send(sender, _create_text(
                    "**Commands:**\n"
                    "- `generate` — write today's deep-dive article\n"
                    "- `status` — check recent articles\n"
                    "- `help` — this message"
                ))
            else:
                await ctx.send(sender, _create_text(
                    f'Got: "{user_text}"\n\nType **generate** to create an article, or **help** for commands.'
                ))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Session ended with {sender}")
            await ctx.send(sender, _create_text("Session ended. Goodbye!"))


@daily_chat_proto.on_message(model=ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info(f"Ack from {sender} for {msg.acknowledged_msg_id}")
