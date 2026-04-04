const { AI_KEYWORDS, AGENT_KEYWORDS, MARKET_KEYWORDS } = require('../config/sources');
const logger = require('../utils/logger').child('filter');

const ALL_KEYWORDS = [...AI_KEYWORDS, ...AGENT_KEYWORDS, ...MARKET_KEYWORDS];

function classifyItem(item) {
  const text = `${item.title} ${item.description}`.toLowerCase();
  let aiScore = 0;
  let agentScore = 0;
  let marketScore = 0;

  for (const kw of AI_KEYWORDS) {
    if (text.includes(kw)) aiScore += kw.includes(' ') ? 3 : 2;
  }
  for (const kw of AGENT_KEYWORDS) {
    if (text.includes(kw)) agentScore += kw.includes(' ') ? 4 : 3;
  }
  for (const kw of MARKET_KEYWORDS) {
    if (text.includes(kw)) marketScore += kw.includes(' ') ? 2 : 1;
  }

  const category =
    agentScore > aiScore && agentScore > marketScore ? 'agents'
    : aiScore >= marketScore ? 'ai'
    : 'market';

  const totalScore = aiScore + agentScore + marketScore;
  return { category, aiScore, agentScore, marketScore, totalScore };
}

function computeRelevanceScore(item) {
  const scores = classifyItem(item);
  let relevance = scores.totalScore;
  if (item.sourceWeight) relevance += item.sourceWeight;
  if (item.score) relevance += Math.min(Math.log10(Math.max(item.score, 1)), 3);
  return { ...scores, relevance };
}

function filterAndRankAIContent(items, { minScore = 2, limit = 40 } = {}) {
  const scored = items
    .map((item) => {
      const scores = computeRelevanceScore(item);
      return { ...item, ...scores };
    })
    .filter((item) => item.relevance >= minScore);

  scored.sort((a, b) => b.relevance - a.relevance);

  const filtered = scored.slice(0, limit);

  const aiCount = filtered.filter((i) => i.category === 'ai').length;
  const agentCount = filtered.filter((i) => i.category === 'agents').length;
  const marketCount = filtered.filter((i) => i.category === 'market').length;

  logger.info(
    `Filtered ${items.length} → ${filtered.length} relevant items ` +
    `(AI: ${aiCount}, Agents: ${agentCount}, Market: ${marketCount})`,
  );

  return filtered;
}

function extractTrendingTopics(items, topN = 5) {
  const frequency = new Map();

  for (const item of items) {
    const text = `${item.title} ${item.description}`.toLowerCase();
    for (const keyword of ALL_KEYWORDS) {
      if (text.includes(keyword)) {
        frequency.set(keyword, (frequency.get(keyword) || 0) + 1);
      }
    }
  }

  return [...frequency.entries()]
    .filter(([kw]) => kw.length > 2)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([topic, count]) => ({ topic, count }));
}

function splitByCategory(items) {
  const ai = items.filter((i) => i.category === 'ai');
  const agents = items.filter((i) => i.category === 'agents');
  const market = items.filter((i) => i.category === 'market');
  return { ai, agents, market };
}

module.exports = {
  filterAndRankAIContent,
  extractTrendingTopics,
  computeRelevanceScore,
  splitByCategory,
};
