"""Generate daily article from summarized news items."""

import logging
from datetime import datetime

from services.llm_service import call_llm, generate_article_images
from services.filter_service import split_by_category

log = logging.getLogger("article")


def _human_date(dt: datetime) -> str:
    return dt.strftime("%A, %B %d, %Y")


def _iso_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _bullet_list(items: list[dict], max_items: int = 7) -> str:
    if not items:
        return "- No stories in this category today"
    return "\n".join(
        f"- **{i['title']}** — {i.get('summary', i['title'])} ([source]({i['link']}))"
        for i in items[:max_items]
    )


def _framework_table(frameworks: list[dict]) -> str:
    if not frameworks:
        return "No framework updates available."

    lines = []
    for f in frameworks:
        release = f.get("latest_release")
        rel_text = ""
        if release and release.get("tag"):
            rel_text = f" — latest: **{release['tag']}**"
            if release.get("published_at"):
                pub_date = release["published_at"][:10]
                rel_text += f" ({pub_date})"

        lines.append(
            f"- **[{f['label']}]({f['url']})** ⭐ {f['stars']:,}"
            + rel_text
            + (f" `{f['language']}`" if f.get("language") else "")
        )
    return "\n".join(lines)


def _trending_list(repos: list[dict]) -> str:
    if not repos:
        return "- No new repos found this week"
    return "\n".join(
        f"- **[{r['name']}]({r['url']})** ⭐ {r['stars']} — {r['description']}"
        + (f" `{r['language']}`" if r.get("language") else "")
        for r in repos
    )


def generate_article(items: list[dict], trends: list[dict], repos: dict, dt: datetime | None = None) -> str:
    dt = dt or datetime.utcnow()
    date_str = _iso_date(dt)
    human = _human_date(dt)
    cats = split_by_category(items)

    frameworks = repos.get("frameworks", []) if isinstance(repos, dict) else []
    trending = repos.get("trending", []) if isinstance(repos, dict) else repos

    log.info("Generating article images...")
    images = generate_article_images(trends, date_str)

    def fmt(section_items: list[dict]) -> str:
        return "\n".join(f"{i + 1}. {it['title']} — {it.get('summary', '')} ({it['source']})" for i, it in enumerate(section_items))

    trend_list = ", ".join(f"{t['topic']} ({t['count']} mentions)" for t in trends) or "General tech developments"

    framework_text = ""
    for f in frameworks[:12]:
        release = f.get("latest_release")
        rel = f" [latest release: {release['tag']}]" if release and release.get("tag") else ""
        framework_text += f"- {f['label']} (⭐{f['stars']:,}){rel} — {f['description'][:100]} [{f['url']}]\n"
    framework_text = framework_text or "No framework data."

    trending_text = ""
    for r in trending[:8]:
        trending_text += f"- {r['name']} (⭐{r['stars']}) — {r['description']} [{r['url']}]\n"
    trending_text = trending_text or "No trending repos."

    img_instructions = ""
    if images:
        img_instructions = "\nINCLUDE THESE IMAGES (markdown syntax):\n"
        img_instructions += "\n".join(f"- {k}: ![{k}]({v})" for k, v in images.items())
        img_instructions += "\nPlace banner at top, others after section headings."

    system = """You are a developer writing a daily newsletter called "AI & Tech Daily".
Beats: AI/ML, AI Agent Frameworks, A2A, MCP, uAgents, Fetch.ai, CrewAI, LangChain, Composio, Daytona, Web3/Blockchain, Tech Market, Developer Learning.

Voice: technical but accessible, opinionated, no hype, include code snippets where relevant.

Sections (exact markdown, include ALL sections):
1. Banner image (if provided) + title "AI & Tech Daily — {date}" + opening hook (2-3 sentences)
2. ## AI News — bullets with bold titles, summaries, [source] links
3. ## AI Agents & Frameworks — CRITICAL section. Cover: uAgents (Fetch.ai), CrewAI, LangChain/LangGraph, AutoGen, Composio, Daytona, A2A protocol, MCP, OpenAI Agents SDK, Pydantic AI. Include latest version numbers, framework comparisons, and code examples.
4. ## Framework Spotlight — pick 2-3 frameworks from the data, explain what's new, show a quick code snippet
5. ## Web3 & Blockchain — products/protocols, NOT prices
6. ## Market & Industry
7. ## Trending AI Repos This Week — new repos with stars and links
8. ## What to Learn Today — 3-4 actionable items with framework tutorials
9. ## Top Trends — 3-5 patterns
10. ## Deep Dive — 3-4 paragraphs on the most important story
11. ## Builder's Perspective — opinionated, mention specific frameworks, end with call to action
12. Footer with date"""

    user = f"""Write newsletter for {human}.
{img_instructions}

=== AI NEWS ===
{fmt(cats.get('ai', [])[:8]) or 'None.'}

=== AI AGENTS & FRAMEWORK NEWS ===
{fmt(cats.get('agents', [])[:8]) or 'None.'}

=== TRACKED FRAMEWORK REPOS (include version info!) ===
{framework_text}

=== WEB3 ===
{fmt(cats.get('web3', [])[:6]) or 'None.'}

=== MARKET ===
{fmt(cats.get('market', [])[:5]) or 'None.'}

=== LEARNING ===
{fmt(cats.get('learning', [])[:5]) or 'None.'}

=== NEW TRENDING REPOS (this week) ===
{trending_text}

Trends: {trend_list}

IMPORTANT: The "AI Agents & Frameworks" and "Framework Spotlight" sections MUST reference specific frameworks from the tracked repos data above — uAgents, CrewAI, LangChain, A2A, MCP, Composio, Daytona, etc. Include their star counts and latest versions.

Write FULL article in markdown. Include code snippets. End with generation date."""

    result = call_llm(system, user, temperature=0.8, max_tokens=5000)

    if result:
        if "AI Tech Daily Agent" not in result:
            result += f"\n\n---\n\n*Generated on {date_str} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*\n"
        log.info("Article generated via LLM")
        return result

    log.info("Using fallback template")
    return _fallback_article(cats, trends, frameworks, trending, images, human, date_str)


def _fallback_article(cats, trends, frameworks, trending, images, human, date_str):
    img = lambda k, alt: f"\n![{alt}]({images[k]})\n" if k in images else ""
    trend_text = "\n".join(f"- **{t['topic'].title()}** — mentioned {t['count']} times" for t in trends) or "- General developments"

    return f"""{img('banner', 'AI & Tech Daily')}
# AI & Tech Daily — {human}

> Daily briefing on AI, AI Agent Frameworks, Web3, and tech — from a builder's perspective.

---

## AI News
{img('ai', 'AI News')}
{_bullet_list(cats.get('ai', []))}

---

## AI Agents & Frameworks
{img('agents', 'AI Agents')}
{_bullet_list(cats.get('agents', []), 8)}

---

## Framework Spotlight

### Tracked Frameworks

{_framework_table(frameworks)}

---

## Web3 & Blockchain
{img('web3', 'Web3')}
{_bullet_list(cats.get('web3', []), 5)}

---

## Market & Industry

{_bullet_list(cats.get('market', []), 4)}

---

## Trending AI Repos This Week

{_trending_list(trending)}

---

## Trending Topics

{trend_text}

---

*Generated on {date_str} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*
"""
