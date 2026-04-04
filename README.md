# AI Tech Daily Agent

An autonomous agent that fetches AI, Web3, and tech news every day — summarizes it, generates images, writes a full newsletter, and publishes it to GitHub. Zero manual effort.

[![Daily AI Article](https://github.com/gautammanak1/ai-tech-daily-agent/actions/workflows/daily.yml/badge.svg)](https://github.com/gautammanak1/ai-tech-daily-agent/actions/workflows/daily.yml)

**Live output** → [github.com/gautammanak1/ai-tech-daily](https://github.com/gautammanak1/ai-tech-daily)

---

## What It Does

```
RSS Feeds (12+) ─┐
Hacker News API  ─┤─→ Fetch ─→ Deduplicate ─→ Filter & Rank ─→ Summarize (LLM)
Dev.to Feeds     ─┤                                                  │
CoinDesk         ─┘                                                  ▼
                                                          Generate Images (AI)
GitHub Trending ──────────────────────────────────────────────→ │
                                                          Generate Article (LLM)
                                                                │
                                                    ┌───────────┴───────────┐
                                                    ▼                       ▼
                                            Private Repo              Public Repo
                                         (articles/YYYY-MM-DD.md)  (article.md + README)
```

Every day at **06:00 UTC**, the agent:

1. **Fetches** 250+ items from 12+ RSS feeds, Hacker News, Dev.to, and CoinDesk
2. **Deduplicates** stories across sources using normalized title matching
3. **Filters** using 150+ keywords across AI, AI Agents, Web3, and market categories
4. **Ranks** by relevance score (keyword matches + source weight + community engagement)
5. **Summarizes** each story using an LLM in batches of 8
6. **Searches** GitHub for trending AI agent repos created in the last week
7. **Generates images** for each section using ASI1 image generation API
8. **Writes** a full newsletter with Deep Dive, Insights, and Builder's Perspective
9. **Publishes** to both private archive and public repo with updated README

---

## Article Sections

Each daily article includes:

| Section | What's In It |
|---------|-------------|
| **AI News** | Top AI/ML developments with AI-generated section image |
| **AI Agents & Agentic AI** | Agent frameworks, launches, tools, research |
| **Web3 & Blockchain** | New products, protocol updates, DeFi (no price speculation) |
| **Market & Industry** | Funding rounds, acquisitions, regulations |
| **Trending AI Repos** | New GitHub repos from the past week with stars and descriptions |
| **What to Learn Today** | Actionable items — tutorials, tools, repos to explore |
| **Top Trends** | 3-5 patterns emerging across all categories |
| **Deep Dive** | 3-4 paragraphs going deep on the most important story |
| **Insights** | Analysis connecting dots across AI, Web3, and agents |
| **Builder's Perspective** | Opinionated take with a specific call to action |

---

## Data Sources

| Source | Type | Content |
|--------|------|---------|
| Google News (3 feeds) | RSS | AI, AI Agents, Tech Market |
| TechCrunch (2 feeds) | RSS | AI + Startups |
| The Verge | RSS | AI product news |
| MIT Technology Review | RSS | Research & policy |
| Ars Technica | RSS | Tech industry |
| CoinDesk | RSS | Crypto & Web3 |
| Dev.to (3 feeds) | RSS | AI, Web3, Tutorials |
| Hacker News | API | Developer community picks |
| GitHub Search | API | Trending AI agent repos |
| ASI1 | API | AI-generated images |

All sources are free, public, and legally accessible. No scraping of gated platforms.

---

## Quick Start

```bash
git clone https://github.com/gautammanak1/ai-tech-daily-agent.git
cd ai-tech-daily-agent
npm install
cp .env.example .env
```

Edit `.env` with your API key:

```env
LLM_API_KEY=your_asi1_api_key_here
```

Run:

```bash
node src/main.js
```

Dry run (skip git commit):

```bash
DRY_RUN=true node src/main.js
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_API_KEY` | Yes | ASI1 API key (used for LLM + image generation) |
| `LLM_BASE_URL` | No | API endpoint (default: `https://api.asi1.ai/v1`) |
| `LLM_MODEL` | No | Model name (default: `asi1`) |
| `GH_TOKEN` | No | GitHub PAT for pushing to public repo |
| `DRY_RUN` | No | Set `true` to skip git operations |

---

## GitHub Actions Setup

The workflow runs automatically every day. To set up:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these secrets:

| Secret | Value |
|--------|-------|
| `LLM_API_KEY` | Your ASI1 API key |
| `GH_PAT` | GitHub Personal Access Token (with `contents: write` on `ai-tech-daily` repo) |

3. Done. The workflow runs daily at 06:00 UTC, or trigger manually from the **Actions** tab.

---

## Architecture

```
src/
├── agents/                  Pipeline stages
│   ├── fetchNews.js              Orchestrates all source fetchers
│   ├── filterAI.js               Multi-category keyword scoring & ranking
│   ├── summarize.js              LLM batch summarization with fallback
│   └── generateArticle.js        LLM article + image generation
├── services/                Data source adapters
│   ├── rssService.js             RSS feed parser (12+ feeds)
│   ├── hackernewsService.js      HN Firebase API
│   ├── githubService.js          GitHub trending repo search
│   ├── imageService.js           ASI1 image generation + base64 save
│   └── publishService.js         Public repo publisher (article + README + images)
├── utils/                   Shared utilities
│   ├── logger.js                 Structured colored logging
│   ├── fileWriter.js             Article file output
│   └── dateFormatter.js          Date helpers
├── config/
│   └── sources.js            Feed URLs, 150+ keywords, weights, config
└── main.js                   Entry point & orchestrator
```

---

## Fallback Behavior

The agent always produces output, no matter what fails:

| Scenario | What Happens |
|----------|-------------|
| No LLM key | Falls back to extractive summaries + template article |
| A feed is down | Logs warning, continues with other sources |
| Image generation fails | Article generates without images |
| GitHub search fails | Article generates without trending repos |
| Article already exists | Skips regeneration for that date |

---

## Tech Stack

- **Runtime**: Node.js 18+
- **LLM**: ASI1 API (OpenAI-compatible)
- **Image Generation**: ASI1 Image API
- **RSS**: rss-parser
- **HTTP**: axios
- **Git**: simple-git
- **CI/CD**: GitHub Actions

---

## License

MIT

---

## Support

If this project is useful to you, consider sponsoring:

**[github.com/sponsors/gautammanak1](https://github.com/sponsors/gautammanak1)**
