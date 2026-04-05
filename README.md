# AI Tech Daily Agent

A **uAgent** (Fetch.ai) that autonomously generates daily AI/Web3/tech news articles.

Built with [uAgents](https://github.com/fetchai/uAgents) + chat protocol — can run as a **chat agent** or via **CLI/cron**.

---

## What It Does

1. Fetches news from **12+ sources** (RSS, Hacker News, Dev.to, CoinDesk)
2. Filters and ranks by AI / AI Agents / Web3 / Market relevance
3. Summarizes using ASI1 LLM
4. Generates images per article via ASI1 Image API
5. Writes a full newsletter with Deep Dive, Trending Repos, Builder's Perspective
6. Saves locally with unique filenames (`YYYY-MM-DD.md`, `YYYY-MM-DD-2.md`, ...)
7. Pushes to public repo without overwriting previous content

## Live Output

Latest article: [github.com/gautammanak1/ai-tech-daily](https://github.com/gautammanak1/ai-tech-daily)

---

## Architecture

```
agent.py              ← uAgent entry point (chat mode or CLI mode)
├── protocols/
│   └── chat_proto.py ← Chat protocol handler
├── services/
│   ├── news_service.py      ← RSS + Hacker News fetching
│   ├── filter_service.py    ← Keyword scoring, categorization
│   ├── llm_service.py       ← ASI1 LLM + image generation
│   ├── github_service.py    ← Trending repo search
│   ├── article_service.py   ← Newsletter generation
│   └── publish_service.py   ← Git commit + public repo push
├── config/
│   └── sources.py           ← RSS feeds, keywords, settings
├── articles/                ← Generated articles (kept forever)
├── images/                  ← Generated images (per article)
└── tests/
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/gautammanak1/ai-tech-daily-agent.git
cd ai-tech-daily-agent

# Setup
cp .env.example .env
# Edit .env with your API keys

# Install
pip install uv
uv sync

# Run as chat agent
uv run python agent.py

# Run as CLI (one-shot)
uv run python agent.py --cli
```

---

## Modes

### Chat Agent Mode (default)
```bash
uv run python agent.py
```
Runs as a uAgent with chat protocol. Send **"generate"** via Agentverse to create an article.

### CLI Mode
```bash
uv run python agent.py --cli
```
Runs the pipeline once and exits. Used by GitHub Actions.

---

## Article Sections

| Section | Content |
|---------|---------|
| AI News | Latest AI/ML developments |
| AI Agents | Agentic AI, frameworks, MCP |
| Web3 & Blockchain | DeFi, protocols, smart contracts |
| Market & Industry | Funding, acquisitions, earnings |
| Trending Repos | New GitHub repos this week |
| What to Learn | Actionable tutorials |
| Deep Dive | In-depth analysis of top story |
| Builder's Perspective | Opinionated takes |

---

## GitHub Actions Setup

Add these secrets in your repo settings → Secrets and variables → Actions:

| Secret | Value |
|--------|-------|
| `ASI_ONE_API_KEY` | Your ASI1 API key |
| `GH_PAT` | GitHub PAT (classic) with `repo` scope |

Workflow runs daily at 6:00 AM UTC, or manually via "Run workflow".

---

## Tech Stack

- **Python 3.11** + uv
- **uAgents** — Fetch.ai agent framework
- **Chat Protocol** — uagents-core chat spec
- **ASI1 API** — LLM (asi1-mini) + image generation
- **feedparser** — RSS parsing
- **GitPython** — Git operations
- **GitHub Actions** — Daily automation
