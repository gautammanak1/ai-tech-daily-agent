const { callLLM } = require('./summarize');
const { splitByCategory } = require('./filterAI');
const { toISODate, toHumanDate } = require('../utils/dateFormatter');
const { ARTICLE_CONFIG } = require('../config/sources');
const logger = require('../utils/logger').child('generateArticle');

function buildBulletList(items) {
  return items
    .map((item) => `- **${item.title}** — ${item.summary} ([source](${item.link}))`)
    .join('\n');
}

function buildFallbackArticle(items, trends, date) {
  const { ai, agents, market } = splitByCategory(items);
  const humanDate = toHumanDate(date);
  const isoDate = toISODate(date);

  const trendSection = trends.length
    ? trends.map((t) => `- **${capitalize(t.topic)}** — mentioned ${t.count} times across sources`).join('\n')
    : '- General AI industry developments across the board';

  const aiSection = ai.length
    ? buildBulletList(ai.slice(0, 7))
    : '- No major AI-specific stories today';

  const agentSection = agents.length
    ? buildBulletList(agents.slice(0, 5))
    : '- No major AI agent stories today';

  const marketSection = market.length
    ? buildBulletList(market.slice(0, 5))
    : '- No major market stories today';

  return `# AI & Tech Daily — ${humanDate}

> Your daily briefing on AI, autonomous agents, and the tech market — curated from across the web.

---

## AI News

${aiSection}

---

## AI Agents & Agentic AI

${agentSection}

---

## Market & Industry

${marketSection}

---

## Trending Topics

${trendSection}

---

## Insights

Today's developments highlight the intersection of AI research, agent-based systems, and market dynamics. AI agents are quickly moving from demos to production, while the broader industry continues to attract significant investment and regulatory attention.

---

## Developer's Take

For builders: the real action is in agent frameworks and tooling. Whether it's MCP integrations, multi-agent orchestration, or function calling — the infrastructure to make AI agents useful is maturing fast. Pick a lane, ship something, iterate.

---

*Generated on ${isoDate} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*
`;
}

async function generateArticle(items, trends, date = new Date()) {
  const { ai, agents, market } = splitByCategory(items);
  const humanDate = toHumanDate(date);
  const isoDate = toISODate(date);

  const formatSection = (sectionItems) =>
    sectionItems.map((item, i) => `${i + 1}. ${item.title} — ${item.summary} (${item.source})`).join('\n');

  const trendList = trends.map((t) => `${t.topic} (${t.count} mentions)`).join(', ');

  const systemPrompt = `You are a senior tech journalist writing a daily newsletter called "AI & Tech Daily".
You cover THREE beats: (1) AI/ML developments, (2) AI Agents & agentic AI, (3) tech market & industry news.

Your voice:
- Sharp, concise, like a smart colleague giving you the morning brief
- Concrete — name companies, products, dollar amounts, technical details
- Opinionated but balanced — call out hype, praise real progress
- Zero filler phrases — no "In the ever-evolving landscape" or "It remains to be seen"
- Mix short punchy sentences with longer analytical ones
- Write like a builder who reads the news, not a reporter who watches from outside

Structure the article EXACTLY as markdown with these sections:
1. Opening hook (2-3 sentences, no heading — lead with the single most interesting story of the day)
2. ## AI News — top AI/ML stories as bullet points with bold titles, 1-2 sentence summaries, and [source] links
3. ## AI Agents & Agentic AI — agent-specific news (frameworks, launches, research, tools)
4. ## Market & Industry — funding rounds, acquisitions, earnings, regulations, layoffs
5. ## Top Trends — 3-5 patterns emerging across all categories
6. ## Insights — 2-3 paragraphs connecting the dots across all three beats
7. ## Developer's Take — opinionated paragraph from a builder's perspective on what matters today
8. Footer with generation date`;

  const userPrompt = `Write the AI & Tech Daily newsletter for ${humanDate}.

=== AI/ML NEWS ===
${formatSection(ai.slice(0, 8)) || 'No major AI stories today.'}

=== AI AGENTS & AGENTIC AI ===
${formatSection(agents.slice(0, 6)) || 'No major agent stories today.'}

=== MARKET & INDUSTRY ===
${formatSection(market.slice(0, 6)) || 'No major market stories today.'}

Trending topics across all categories: ${trendList || 'General tech developments'}

Source links:
${items.slice(0, 20).map((item, i) => `${i + 1}. ${item.link}`).join('\n')}

Write the FULL article in markdown. Lead with the most compelling story, not a generic intro.`;

  const generated = await callLLM(systemPrompt, userPrompt, {
    temperature: 0.8,
    maxTokens: 4000,
  });

  if (generated) {
    const article = ensureFooter(generated, isoDate);
    logger.info('Article generated via LLM');
    return article;
  }

  logger.info('Using fallback article template');
  return buildFallbackArticle(items, trends, date);
}

function ensureFooter(content, isoDate) {
  if (!content.includes('AI Tech Daily Agent')) {
    content += `\n\n---\n\n*Generated on ${isoDate} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*\n`;
  }
  return content;
}

function capitalize(str) {
  return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

module.exports = { generateArticle };
