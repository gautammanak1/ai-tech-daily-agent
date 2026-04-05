"""Publish article to public GitHub repo. Each article is a separate file. Never delete old ones."""

import logging
import os
import shutil
import tempfile
from pathlib import Path

log = logging.getLogger("publish")

PUBLIC_REPO = "https://github.com/gautammanak1/ai-tech-daily.git"


def publish_article(article_content: str, filename: str, company_name: str, date_str: str, dry_run: bool = False):
    """Publish article as a new file in the public repo."""
    if dry_run:
        log.info(f"DRY_RUN — would publish {filename}")
        return

    token = os.getenv("GH_TOKEN", "").strip() or os.getenv("GITHUB_TOKEN", "").strip()
    clone_url = PUBLIC_REPO
    if token:
        clone_url = PUBLIC_REPO.replace("https://", f"https://x-access-token:{token}@")

    tmp_dir = tempfile.mkdtemp(prefix="ai-tech-daily-")

    try:
        from git import Repo
        log.info("Cloning public repo...")
        repo = Repo.clone_from(clone_url, tmp_dir)
        repo.config_writer().set_value("user", "name", os.getenv("GIT_USER_NAME", "gautammanak1")).release()
        repo.config_writer().set_value("user", "email", os.getenv("GIT_USER_EMAIL", "gautammanak1@gmail.com")).release()

        articles_dir = Path(tmp_dir) / "articles"
        articles_dir.mkdir(exist_ok=True)

        target = articles_dir / filename
        if target.exists():
            stem = filename.replace(".md", "")
            for i in range(2, 50):
                alt = f"{stem}-{i}.md"
                if not (articles_dir / alt).exists():
                    filename = alt
                    target = articles_dir / alt
                    break

        target.write_text(article_content, encoding="utf-8")
        log.info(f"Article written: articles/{filename}")

        _update_readme(tmp_dir, filename, company_name, date_str)

        repo.git.add("-A")
        if repo.is_dirty() or repo.untracked_files:
            repo.index.commit(f"docs: {company_name} deep dive — {date_str}")
            repo.remotes.origin.push()
            log.info(f"Published articles/{filename}")
        else:
            log.info("No changes to publish")
    except Exception as e:
        log.error(f"Failed to publish: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _update_readme(repo_dir: str, new_filename: str, company_name: str, date_str: str):
    """Update README to list ALL articles. Never remove old entries."""
    readme_path = Path(repo_dir) / "README.md"
    articles_dir = Path(repo_dir) / "articles"

    all_articles = sorted(articles_dir.glob("*.md"), reverse=True)

    rows = []
    for f in all_articles:
        name_parts = f.stem.rsplit("-", 3)
        if len(name_parts) >= 4:
            topic = "-".join(name_parts[:-3])
            date = "-".join(name_parts[-3:])
        else:
            topic = f.stem
            date = ""
        rows.append(f"| [{f.name}](./articles/{f.name}) | {topic} | {date} |")

    article_table = "\n".join(rows) if rows else "| — | — | — |"

    readme = f"""# AI & Tech Daily

> Daily deep-dive articles on AI companies, agent frameworks, and tech — written by an autonomous AI agent.

Each day, the agent **picks a different company** (Google, Microsoft, OpenAI, Anthropic, Fetch.ai, LangChain, CrewAI, Composio, Daytona, and more), does **real-time web research**, and writes a **300+ line deep-dive** article.

---

## Latest Article

**[{new_filename}](./articles/{new_filename})** — {company_name} ({date_str})

---

## All Articles

| Article | Company | Date |
|---------|---------|------|
{article_table}

---

## How It Works

1. Agent auto-picks a company (rotates daily, never repeats recently)
2. Real-time web search via DuckDuckGo (news + web + GitHub)
3. Scrapes top articles for detailed content
4. Tracks 19 agent framework repos (stars, versions, releases)
5. Generates 300+ line deep-dive using ASI1 LLM
6. Publishes here as a separate `.md` file

---

## Companies Covered

Google, Microsoft, OpenAI, Anthropic, Meta, NVIDIA, Fetch.ai, LangChain, CrewAI, Composio, Daytona, Hugging Face, Apple, Amazon, Mistral AI, Cohere, Stability AI, xAI, Vercel, Pydantic AI, AutoGPT, Perplexity, Databricks, Tesla, Cursor, Replit

---

*Powered by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*
"""
    readme_path.write_text(readme, encoding="utf-8")
    log.info(f"README updated — {len(all_articles)} articles listed")
