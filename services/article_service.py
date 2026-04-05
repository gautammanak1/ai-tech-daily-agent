"""Generate a 300+ line deep-dive article about ONE company using real-time data + images."""

import logging
from datetime import datetime

from services.llm_service import call_llm

log = logging.getLogger("article")


def generate_article(
    company: dict,
    search_data: dict,
    scraped_content: str,
    github_repos: list[dict],
    images: dict[str, str],
) -> tuple[str, str]:
    """
    Generate a deep-dive article about one company.
    Returns (article_content, filename).
    """
    dt = datetime.utcnow()
    date_str = dt.strftime("%Y-%m-%d")
    human_date = dt.strftime("%A, %B %d, %Y")
    name = company["name"]
    slug = company["slug"]
    topics = ", ".join(company["topics"])

    news_text = _format_news(search_data.get("news", []))
    web_text = _format_web(search_data.get("web", []))
    github_text = _format_github(search_data.get("github", []))
    repo_text = _format_tracked_repos(github_repos)

    img_instructions = ""
    if images:
        img_instructions = "\nINCLUDE THESE IMAGES in the article using markdown image syntax:\n"
        for key, url in images.items():
            if key == "logo":
                img_instructions += f'- Company logo (place after title): ![{name} Logo]({url})\n'
            elif key == "hero":
                img_instructions += f'- Hero image (place after TL;DR): ![{name}]({url})\n'
            elif key == "banner":
                img_instructions += f'- Section image (place before Product Deep Dive): ![{name} Technology]({url})\n'
        img_instructions += "\nPlace images naturally between sections. Do NOT cluster them."

    system = f"""You are a senior tech journalist and developer advocate writing an in-depth daily article for "AI & Tech Daily".

TODAY'S FOCUS: {name}

Write a COMPREHENSIVE deep-dive about {name} — covering everything happening RIGHT NOW.

RULES:
- Article MUST be 300+ lines of markdown
- ALL content must be based on the real-time search data provided — do NOT invent facts
- Include specific numbers: star counts, funding, users, version numbers
- Include 2-3 code snippets showing how to use their tools/products
- Include links to sources: [text](url)
- Include images where provided (logo, hero, tech images)
- Be opinionated — give your take on what this means for developers
- Every section must have real, substantial content

REQUIRED SECTIONS (## headings, ALL mandatory):

# {name} — Deep Dive | {human_date}

## Company Overview
What they do, mission, key products, founding story, team size, funding.

## Latest News & Announcements
Everything from the search results. Each item as a bullet with bold title, summary, and [source](url).

## Product & Technology Deep Dive
Detailed look at their main products/platforms. Architecture, features, how it works.

## GitHub & Open Source
Their repos, stars, recent activity, community engagement. Include repo links.

## Getting Started — Code Examples
2-3 practical code snippets. Installation, basic usage, advanced example. Use ```python or ```typescript blocks.

## Market Position & Competition
How they compare to competitors. Market share, pricing, strengths/weaknesses table.

## Developer Impact
What this means for builders. Who should use this and why.

## What's Next
Predictions, upcoming features, roadmap hints from the news.

## Key Takeaways
5-7 numbered actionable points.

## Resources & Links
Useful links organized by category (Official, GitHub, Documentation, Articles).

---
*Generated on {date_str} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*"""

    user = f"""Write a deep-dive article about {name} for {human_date}.

Company topics: {topics}
{img_instructions}

=== REAL-TIME NEWS (searched today) ===
{news_text}

=== WEB SEARCH RESULTS ===
{web_text}

=== GITHUB SEARCH ===
{github_text}

=== TRACKED REPOS DATA ===
{repo_text}

=== SCRAPED ARTICLE CONTENT (from top sources) ===
{scraped_content[:8000]}

IMPORTANT: Write FULL article. 300+ lines minimum. Use ONLY data from above. Include images where instructed. Include code snippets."""

    result = call_llm(system, user, temperature=0.7, max_tokens=8000)

    if result:
        if "AI Tech Daily Agent" not in result:
            result += f"\n\n---\n\n*Generated on {date_str} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent) — Deep dive on {name}*\n"
        log.info(f"Article generated: {len(result.splitlines())} lines")
    else:
        result = _fallback_article(company, search_data, github_repos, images, human_date, date_str)
        log.info("Used fallback template")

    filename = f"{slug}-{date_str}.md"
    return result, filename


def _format_news(news: list[dict]) -> str:
    if not news:
        return "No recent news found."
    lines = []
    for n in news[:15]:
        lines.append(f"- [{n['title']}]({n['url']})")
        if n.get("body"):
            lines.append(f"  {n['body'][:300]}")
        if n.get("date"):
            lines.append(f"  Date: {n['date']}")
        lines.append("")
    return "\n".join(lines)


def _format_web(web: list[dict]) -> str:
    if not web:
        return "No web results."
    return "\n".join(
        f"- [{w['title']}]({w['url']})\n  {w.get('body', '')[:200]}"
        for w in web[:10]
    )


def _format_github(github: list[dict]) -> str:
    if not github:
        return "No GitHub results."
    return "\n".join(
        f"- [{g['title']}]({g['url']})\n  {g.get('body', '')[:200]}"
        for g in github[:8]
    )


def _format_tracked_repos(repos: list[dict]) -> str:
    if not repos:
        return "No tracked repos."
    lines = []
    for r in repos:
        release = r.get("latest_release")
        rel = f" — latest: {release['tag']}" if release and release.get("tag") else ""
        lines.append(f"- {r['label']} (⭐{r['stars']:,}){rel} — {r['description'][:150]} [{r['url']}]")
    return "\n".join(lines)


def _fallback_article(company, search_data, repos, images, human_date, date_str):
    name = company["name"]
    topics = ", ".join(company["topics"])

    logo_img = f"\n![{name} Logo]({images['logo']})\n" if "logo" in images else ""
    hero_img = f"\n![{name}]({images['hero']})\n" if "hero" in images else ""

    news_bullets = "\n".join(
        f"- **{n['title']}** — {n.get('body', '')[:200]} [source]({n['url']})"
        for n in search_data.get("news", [])[:10]
    ) or "- No news available"

    web_bullets = "\n".join(
        f"- [{w['title']}]({w['url']})"
        for w in search_data.get("web", [])[:8]
    ) or "- No web results"

    repo_bullets = "\n".join(
        f"- **[{r['label']}]({r['url']})** ⭐ {r['stars']:,}"
        for r in repos[:10]
    ) or "- No repos tracked"

    return f"""# {name} — Deep Dive | {human_date}
{logo_img}
> Daily deep dive into {name} — covering {topics}.

---

{hero_img}

## Latest News & Announcements

{news_bullets}

---

## Web Resources

{web_bullets}

---

## GitHub & Open Source

{repo_bullets}

---

## Key Takeaways

1. {name} continues to evolve in the AI/tech landscape
2. Monitor their open-source projects for updates
3. Check official channels for latest announcements

---

*Generated on {date_str} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent) — Deep dive on {name}*
"""
