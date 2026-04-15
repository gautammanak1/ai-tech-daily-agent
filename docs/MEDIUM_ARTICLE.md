# I Built an Agent That Writes 300–800+ Line Tech Deep-Dives Every Day — Stack, YAML, and Code Path

> **View this file on GitHub:** [docs/MEDIUM_ARTICLE.md](https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/docs/MEDIUM_ARTICLE.md) · **Raw (import / tools):** [raw.githubusercontent.com/.../MEDIUM_ARTICLE.md](https://raw.githubusercontent.com/gautammanak1/ai-tech-daily-agent/main/docs/MEDIUM_ARTICLE.md)

Images below use **absolute URLs** so imports (Medium, newsletters, etc.) resolve correctly after publish.

![Article cover — AI Tech Daily Agent](https://raw.githubusercontent.com/gautammanak1/ai-tech-daily-agent/main/docs/images/article-cover.png)

---

## Quick links

| What | Link |
|------|------|
| **Agent source** | [github.com/gautammanak1/ai-tech-daily-agent](https://github.com/gautammanak1/ai-tech-daily-agent) |
| **Published articles** | [github.com/gautammanak1/ai-tech-daily](https://github.com/gautammanak1/ai-tech-daily) |
| **Dev.to** | [dev.to/gautammanak1](https://dev.to/gautammanak1) |
| **Fetch.ai uAgents** | [github.com/fetchai/uAgents](https://github.com/fetchai/uAgents) · [fetch.ai](https://fetch.ai) |
| **ASI1 API** | [asi1.ai](https://asi1.ai) |
| **DuckDuckGo (ddgs)** | [github.com/deedy5/ddgs](https://github.com/deedy5/ddgs) |
| **Trafilatura** | [github.com/adbar/trafilatura](https://github.com/adbar/trafilatura) |
| **Dev.to API** | [developers.forem.com/api](https://developers.forem.com/api) |
| **GitPython** | [github.com/gitpython-developers/GitPython](https://github.com/gitpython-developers/GitPython) |
| **uv** | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) |
| **Issues** | [github.com/gautammanak1/ai-tech-daily-agent/issues](https://github.com/gautammanak1/ai-tech-daily-agent/issues) |

---

## What this is

[**AI Tech Daily Agent**](https://github.com/gautammanak1/ai-tech-daily-agent) is a **Python 3.11** pipeline that runs one full research-and-write cycle per execution:

1. **`company_picker`** — one company from **~100** tracked names; skips recently covered picks.
2. **`web_search_service`** — **[DuckDuckGo](https://github.com/deedy5/ddgs)** (ddgs): news, web, GitHub-oriented queries — **no search API key**.
3. **`web_scraper_service`** — **[Trafilatura](https://github.com/adbar/trafilatura)** extracts main text from top URLs.
4. **`image_search_service`** — logo / hero / banner URLs for markdown embeds.
5. **`github_service`** — **19 tracked framework repos** from `config/sources.py` (stars, activity).
6. **`article_service` + `llm_service`** — **[ASI1](https://asi1.ai)** writes **300+ lines** of markdown with required sections and citations.
7. **`publish_service`** — **[GitPython](https://github.com/gitpython-developers/GitPython)** pushes to [**ai-tech-daily**](https://github.com/gautammanak1/ai-tech-daily) and updates the index.
8. **`devto_service`** — **[Dev.to API](https://developers.forem.com/api)** cross-post.

The same flow runs as a **[Fetch.ai uAgent](https://github.com/fetchai/uAgents)** (chat protocol) or via **`uv run python agent.py --cli`** for one-shot runs and **GitHub Actions**.

> Every run is grounded in **live** search, scraped text, and current GitHub signals — not a static template.

---

## Visual workflow (diagrams)

![End-to-end pipeline — search, scrape, LLM, Git, Dev.to](https://raw.githubusercontent.com/gautammanak1/ai-tech-daily-agent/main/docs/images/workflow-pipeline.png)

![Module architecture — services and publishing](https://raw.githubusercontent.com/gautammanak1/ai-tech-daily-agent/main/docs/images/workflow-architecture.png)

![Sequence — one CLI / cron run](https://raw.githubusercontent.com/gautammanak1/ai-tech-daily-agent/main/docs/images/workflow-sequence.png)

*Diagram sources (regenerate with [Kroki](https://kroki.io)):* [`docs/images/_kroki_pipeline.mmd`](https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/docs/images/_kroki_pipeline.mmd) · [`_kroki_architecture.mmd`](https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/docs/images/_kroki_architecture.mmd) · [`_kroki_sequence.mmd`](https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/docs/images/_kroki_sequence.mmd)

---

## Tech stack

| Layer | Technology | Role |
|-------|------------|------|
| Agent | [uAgents](https://github.com/fetchai/uAgents) | Process + optional chat protocol (`protocols/chat_proto.py`) |
| Search | [ddgs](https://github.com/deedy5/ddgs) | News / web / GitHub search |
| Scraping | [Trafilatura](https://github.com/adbar/trafilatura) | Article body extraction |
| Images | DDG Images + logo helpers | Markdown image URLs |
| LLM | [ASI1](https://asi1.ai) | Long-form markdown |
| GitHub | REST API | Tracked repos → metrics |
| Git | [GitPython](https://github.com/gitpython-developers/GitPython) | Commits and push |
| Blog | [Dev.to API](https://developers.forem.com/api) | Cross-post |
| CI/CD | GitHub Actions | Daily cron + `workflow_dispatch` |
| Tooling | [uv](https://github.com/astral-sh/uv) | `pyproject.toml` / `uv run` |

---

## Pipeline as code (`agent.py`)

CLI and Actions both execute **`run_pipeline`** — same call order as production:

```python
def run_pipeline(dry_run: bool = False) -> str:
    """Run the full pipeline once. Returns summary string."""
    from datetime import datetime
    from services.company_picker import pick_company
    from services.web_search_service import search_all
    from services.web_scraper_service import extract_key_content
    from services.image_search_service import get_best_images
    from services.github_service import get_framework_updates
    from services.article_service import generate_article
    from services.publish_service import publish_article
    from services.devto_service import publish_to_devto

    company = pick_company()
    search_data = search_all(company["name"])
    scraped = extract_key_content(search_data)
    images = get_best_images(company["name"], company["slug"])
    frameworks = get_framework_updates()
    article, filename = generate_article(
        company, search_data, scraped, frameworks, images
    )
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    publish_article(article, filename, company["name"], date_str, dry_run=dry_run)
    publish_to_devto(article, company["name"], company["slug"], filename=filename)
    return f"**{company['name']}** — {filename} ({len(article.splitlines())} lines)"
```

- **`uv run python agent.py --cli`** → async wrapper → `run_pipeline`.
- **`uv run python agent.py`** (no args) → **uAgent** with mailbox + chat protocol.

---

## GitHub Actions — `.github/workflows/daily.yml`

Runs **daily at 6:00 UTC** and **`workflow_dispatch`**. Checkout uses **`GH_PAT`** so the job can push to the articles repo.

```yaml
name: Daily AI Tech Article

on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GH_PAT }}
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --no-dev

      - name: Run pipeline
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          ASI_ONE_API_KEY: ${{ secrets.ASI_ONE_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_PAT }}
          DEVTO_API_KEY: ${{ secrets.DEVTO_API_KEY }}
          GIT_USER_NAME: gautammanak1
          GIT_USER_EMAIL: gautammanak1@gmail.com
          DRY_RUN: "false"
        run: uv run python agent.py --cli
```

### Repository secrets

| Secret | Purpose |
|--------|---------|
| `ASI_ONE_API_KEY` | ASI1 LLM |
| `LLM_API_KEY` | Optional second key if your stack splits LLM credentials |
| `GH_PAT` | Checkout + push to [ai-tech-daily](https://github.com/gautammanak1/ai-tech-daily) (`repo` scope) |
| `DEVTO_API_KEY` | [Dev.to](https://dev.to) API |

Local: copy [`.env.example`](https://github.com/gautammanak1/ai-tech-daily-agent/blob/main/.env.example) → `.env`; use `DRY_RUN=true` to skip git during tests.

---

## Local quick start

```bash
git clone https://github.com/gautammanak1/ai-tech-daily-agent.git
cd ai-tech-daily-agent
cp .env.example .env
# ASI_ONE_API_KEY, GH_TOKEN, DEVTO_API_KEY

pip install uv && uv sync
uv run python agent.py          # uAgent + chat protocol
uv run python agent.py --cli    # one article, exit
```

---

## Project layout

```
ai-tech-daily-agent/
├── agent.py
├── protocols/chat_proto.py
├── services/…
├── config/sources.py
├── docs/
│   ├── MEDIUM_ARTICLE.md
│   └── images/           # cover + workflow PNGs, Kroki .mmd sources
├── .github/workflows/daily.yml
└── pyproject.toml
```

---

## Generated article sections (LLM contract)

| Section | Content |
|---------|---------|
| Company Overview | Mission, products, founding, team, funding |
| Latest News | Bullets with **[source](url)** |
| Product Deep Dive | Architecture, features |
| GitHub & Open Source | Repos, stars, activity |
| Code Examples | Install → basic → advanced |
| Market Position | Competitors, tradeoffs |
| Developer Impact | Who benefits |
| What's Next | Outlook |
| Key Takeaways | Numbered |
| Resources | Links |

---

## Limitations

- Retrieval quality varies by company and day — **spot-check** numbers you ship publicly.
- Watch **API limits** (ASI1, GitHub, Dev.to) and **PAT** scopes; inspect **Actions** logs on failure.

---

## Closing

This is a **complete retrieval → generation → publish** loop: **live data**, **structured writing**, **Git as history**, **Dev.to for reach** — with **YAML and Python** you can read line by line.

---

## Author

**Gautam Manak** — uAgents, live web research, and shipping to Git + Dev.to.  
Repo: [github.com/gautammanak1/ai-tech-daily-agent](https://github.com/gautammanak1/ai-tech-daily-agent)

---

## LinkedIn / integrations

Replace `YOUR-HANDLE` before sharing.

> Architecture reviews, **LinkedIn cross-posting**, or extra publishing integrations — **[LinkedIn](https://www.linkedin.com/in/YOUR-HANDLE/)**.

---

## Links

- [ai-tech-daily-agent](https://github.com/gautammanak1/ai-tech-daily-agent) · [ai-tech-daily (articles)](https://github.com/gautammanak1/ai-tech-daily) · [Dev.to](https://dev.to/gautammanak1)  
- [Fetch.ai](https://fetch.ai) · [ASI1](https://asi1.ai)
