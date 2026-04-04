# AI Tech Daily Agent

**Automated daily AI news digest** — fetches, filters, summarizes, and publishes a curated article every day.

No manual curation. No scraping. Just clean, structured AI journalism powered by RSS feeds, public APIs, and an LLM.

---

## How It Works

```
RSS Feeds ─┐
Reddit    ─┤─→ Fetch ─→ Deduplicate ─→ Filter AI ─→ Summarize ─→ Generate Article ─→ Commit
HN API    ─┘
```

1. **Fetch** — Pulls latest posts from Google News, TechCrunch, The Verge, Reddit, and Hacker News
2. **Deduplicate** — Normalizes titles and merges duplicate stories across sources
3. **Filter** — Scores each item against 50+ AI/ML keywords, drops irrelevant noise
4. **Rank** — Weights items by source credibility and community engagement
5. **Summarize** — LLM condenses each story into 1-2 punchy sentences
6. **Generate** — LLM writes a full newsletter-style article with trends and analysis
7. **Publish** — Commits the markdown file to `articles/` and pushes to GitHub

Daily articles land in [`articles/`](./articles/) as `YYYY-MM-DD.md`.

---

## Data Sources

| Source | Type | Content |
|--------|------|---------|
| Google News | RSS | AI-related headlines |
| TechCrunch | RSS | AI industry coverage |
| The Verge | RSS | AI product news |
| MIT Tech Review | RSS | Research & policy |
| Hacker News | API | Developer community picks |
| Reddit | API | r/artificial, r/MachineLearning, r/LocalLLaMA |

All sources are free, public, and legally accessible. No scraping of gated platforms.

---

## Quick Start

```bash
git clone https://github.com/gautammanak1/ai-tech-daily-agent.git
cd ai-tech-daily-agent
npm install
cp .env.example .env
# Edit .env with your API keys
node src/main.js
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_API_KEY` | Yes | OpenAI (or compatible) API key |
| `LLM_BASE_URL` | No | Custom endpoint (default: OpenAI) |
| `LLM_MODEL` | No | Model name (default: `gpt-4o-mini`) |
| `REDDIT_CLIENT_ID` | No | Reddit app client ID |
| `REDDIT_SECRET` | No | Reddit app secret |
| `DRY_RUN` | No | Set `true` to skip git commit |

The agent works without Reddit credentials — it simply skips that source.

---

## Daily Automation

A GitHub Actions workflow runs every day at 06:00 UTC:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'
```

To set up:

1. Fork this repo
2. Go to **Settings → Secrets and variables → Actions**
3. Add `LLM_API_KEY` (and optionally `REDDIT_CLIENT_ID`, `REDDIT_SECRET`)
4. The workflow handles everything else — install, run, commit, push

You can also trigger it manually from the **Actions** tab.

---

## Article Format

Each daily article includes:

- **Opening Hook** — leads with the most interesting story
- **Top Stories** — bullet-point summaries with source links
- **Top 3 Trends** — patterns emerging from today's news
- **Insights** — analysis of what the stories mean together
- **Developer's Take** — opinionated perspective from a builder's POV

---

## Architecture

```
src/
├── agents/           Pipeline stages
│   ├── fetchNews.js        Orchestrates all source fetchers
│   ├── filterAI.js         Keyword scoring & ranking
│   ├── summarize.js        LLM batch summarization
│   └── generateArticle.js  LLM article generation
├── services/         Data source adapters
│   ├── rssService.js       RSS feed parser
│   ├── redditService.js    Reddit OAuth + API
│   └── hackernewsService.js  HN Firebase API
├── utils/            Shared utilities
│   ├── logger.js           Structured colored logging
│   ├── fileWriter.js       Article file output
│   └── dateFormatter.js    Date helpers
├── config/
│   └── sources.js    Feed URLs, keywords, weights
└── main.js           Entry point & orchestrator
```

---

## Fallback Behavior

The agent is designed to always produce output:

- **No LLM key?** Falls back to extractive summaries and a template article
- **Reddit credentials missing?** Skips Reddit, uses remaining sources
- **A feed is down?** Logs a warning, continues with other sources
- **Article already exists?** Skips regeneration for that date

---

## License

MIT

---

## Support

If this project is useful to you, consider sponsoring:

**[github.com/sponsors/gautammanak1](https://github.com/sponsors/gautammanak1)**
