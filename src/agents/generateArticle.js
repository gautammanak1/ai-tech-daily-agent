const { callLLM } = require('./summarize');
const { splitByCategory } = require('./filterAI');
const { generateArticleImages } = require('../services/imageService');
const { toISODate, toHumanDate } = require('../utils/dateFormatter');
const { ARTICLE_CONFIG } = require('../config/sources');
const logger = require('../utils/logger').child('generateArticle');

function buildBulletList(items) {
  return items
    .map((item) => `- **${item.title}** — ${item.summary} ([source](${item.link}))`)
    .join('\n');
}

function buildRepoList(repos) {
  if (!repos || repos.length === 0) return '- No new repos found this week';
  return repos
    .map((r) => `- **[${r.name}](${r.url})** ⭐ ${r.stars} — ${r.description || 'No description'}${r.language ? ` \`${r.language}\`` : ''}`)
    .join('\n');
}

function buildFallbackArticle(items, trends, date, images, repos) {
  const { ai, agents, web3, market, learning } = splitByCategory(items);
  const humanDate = toHumanDate(date);
  const isoDate = toISODate(date);

  const trendSection = trends.length
    ? trends.map((t) => `- **${capitalize(t.topic)}** — mentioned ${t.count} times across sources`).join('\n')
    : '- General tech industry developments';

  const section = (arr, max, fallback) =>
    arr.length ? buildBulletList(arr.slice(0, max)) : `- ${fallback}`;

  const img = (key, alt) => images[key] ? `\n![${alt}](${images[key]})\n` : '';

  return `${img('banner', 'AI & Tech Daily')}
# AI & Tech Daily — ${humanDate}

> Your daily briefing on AI, AI agents, Web3, and the tech market — curated and analyzed from a builder's perspective.

---

## AI News
${img('ai', 'AI News')}
${section(ai, 7, 'No major AI stories today')}

---

## AI Agents & Agentic AI
${img('agents', 'AI Agents')}
${section(agents, 5, 'No major agent stories today')}

---

## Web3 & Blockchain
${img('web3', 'Web3')}
${section(web3, 5, 'No major Web3 stories today')}

---

## Market & Industry

${section(market, 4, 'No major market stories today')}

---

## Trending AI Repos This Week

${buildRepoList(repos)}

---

## Learning & Tutorials

${section(learning, 4, 'No tutorials surfaced today — check Dev.to for fresh posts')}

---

## Trending Topics

${trendSection}

---

## Insights

Today's developments show how AI, Web3, and agent-based systems are converging. New products are shipping faster than ever, and the tooling ecosystem keeps maturing. For learners and builders, the key is picking one thread and going deep.

---

## Builder's Perspective

The best way to learn is to ship. Pick one story from today, build a small prototype inspired by it, and share what you learn. The gap between reading about tech and building with it is smaller than you think.

---

*Generated on ${isoDate} by [AI Tech Daily Agent](https://github.com/gautammanak1/ai-tech-daily-agent)*
`;
}

async function generateArticle(items, trends, date = new Date(), trendingRepos = []) {
  const { ai, agents, web3, market, learning } = splitByCategory(items);
  const humanDate = toHumanDate(date);
  const isoDate = toISODate(date);

  logger.info('Generating article images...');
  const images = await generateArticleImages(trends, isoDate);

  const formatSection = (sectionItems) =>
    sectionItems.map((item, i) => `${i + 1}. ${item.title} — ${item.summary} (${item.source})`).join('\n');

  const trendList = trends.map((t) => `${t.topic} (${t.count} mentions)`).join(', ');

  const repoList = trendingRepos.length
    ? trendingRepos.map((r) => `- ${r.name} (⭐${r.stars}) — ${r.description} [${r.url}]`).join('\n')
    : 'No trending repos found this week.';

  const imageInstructions = Object.entries(images).length > 0
    ? `\nINCLUDE THESE IMAGES in the article at the specified locations (use markdown image syntax):
${Object.entries(images).map(([key, path]) => `- ${key}: ![${key}](${path})`).join('\n')}
Place banner at the very top. Place others after their section heading.`
    : '';

  const systemPrompt = `You are a developer and tech enthusiast writing a premium daily newsletter called "AI & Tech Daily".
You cover: AI/ML, AI Agents, Web3/Blockchain, Tech Market, Developer Learning, and Trending GitHub Repos.

Your perspective: you're a builder who learns by reading AND shipping.

Your voice:
- Technical but accessible — explain WHY something matters
- When a new product/tool launches, explain what it does and how to get started
- Connect dots between AI, Web3, and agents
- Include practical takeaways and code snippets where relevant
- No hype, no filler. Write like a developer, not a journalist
- Short paragraphs, punchy sentences

Structure the article EXACTLY as markdown:
1. Banner image (if provided) at the very top
2. Opening hook (2-3 sentences, no heading)
3. ## AI News — bullet points with bold titles, summaries, [source] links. Section image after heading
4. ## AI Agents & Agentic AI — agent news with section image
5. ## Web3 & Blockchain — products/protocols, NOT price talk. Section image after heading
6. ## Market & Industry — funding, acquisitions, regulations
7. ## Trending AI Repos This Week — list of new GitHub repos with stars, descriptions, and links
8. ## What to Learn Today — 3-4 actionable items: tutorials, tools to try, repos to star
9. ## Top Trends — 3-5 patterns across all categories
10. ## Deep Dive — pick the most important story, 3-4 paragraphs going deep
11. ## Insights — 2-3 paragraphs connecting dots
12. ## Builder's Perspective — opinionated, end with specific call to action
13. Footer with generation date`;

  const userPrompt = `Write the AI & Tech Daily newsletter for ${humanDate}.
${imageInstructions}

=== AI/ML NEWS ===
${formatSection(ai.slice(0, 8)) || 'No major AI stories today.'}

=== AI AGENTS & AGENTIC AI ===
${formatSection(agents.slice(0, 6)) || 'No major agent stories today.'}

=== WEB3 & BLOCKCHAIN ===
${formatSection(web3.slice(0, 6)) || 'No major Web3 stories today.'}

=== MARKET & INDUSTRY ===
${formatSection(market.slice(0, 5)) || 'No major market stories today.'}

=== DEVELOPER LEARNING / TUTORIALS ===
${formatSection(learning.slice(0, 5)) || 'No tutorials surfaced today.'}

=== TRENDING GITHUB REPOS (new this week) ===
${repoList}

Trending topics: ${trendList || 'General tech developments'}

Source links:
${items.slice(0, 25).map((item, i) => `${i + 1}. ${item.link}`).join('\n')}

IMPORTANT:
- Write the FULL article in markdown
- Include ALL provided images using exact markdown syntax given
- In Trending Repos, format each as: **[repo-name](url)** ⭐ stars — description
- Include at least one code snippet or CLI command
- Make it feel like it was written by a developer who builds things`;

  const generated = await callLLM(systemPrompt, userPrompt, {
    temperature: 0.8,
    maxTokens: 5000,
  });

  if (generated) {
    const article = ensureFooter(generated, isoDate);
    logger.info('Article generated via LLM');
    return article;
  }

  logger.info('Using fallback article template');
  return buildFallbackArticle(items, trends, date, images, trendingRepos);
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
