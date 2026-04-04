const { AI_KEYWORDS, AGENT_KEYWORDS, WEB3_KEYWORDS, MARKET_KEYWORDS } = require('../config/sources');
const logger = require('../utils/logger').child('filter');

const ALL_KEYWORDS = [...AI_KEYWORDS, ...AGENT_KEYWORDS, ...WEB3_KEYWORDS, ...MARKET_KEYWORDS];

function classifyItem(item) {
  const text = `${item.title} ${item.description}`.toLowerCase();
  let aiScore = 0;
  let agentScore = 0;
  let web3Score = 0;
  let marketScore = 0;

  for (const kw of AI_KEYWORDS) {
    if (text.includes(kw)) aiScore += kw.includes(' ') ? 3 : 2;
  }
  for (const kw of AGENT_KEYWORDS) {
    if (text.includes(kw)) agentScore += kw.includes(' ') ? 4 : 3;
  }
  for (const kw of WEB3_KEYWORDS) {
    if (text.includes(kw)) web3Score += kw.includes(' ') ? 3 : 2;
  }
  for (const kw of MARKET_KEYWORDS) {
    if (text.includes(kw)) marketScore += kw.includes(' ') ? 2 : 1;
  }

  if (item.category === 'learning') {
    return { category: 'learning', aiScore, agentScore, web3Score, marketScore, totalScore: aiScore + agentScore + web3Score + marketScore + 3 };
  }

  const scores = { ai: aiScore, agents: agentScore, web3: web3Score, market: marketScore };
  const category = Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
  const finalCategory = scores[category] > 0 ? category : (item.category || 'ai');

  return { category: finalCategory, aiScore, agentScore, web3Score, marketScore, totalScore: aiScore + agentScore + web3Score + marketScore };
}

function computeRelevanceScore(item) {
  const scores = classifyItem(item);
  let relevance = scores.totalScore;
  if (item.sourceWeight) relevance += item.sourceWeight;
  if (item.score) relevance += Math.min(Math.log10(Math.max(item.score, 1)), 3);
  return { ...scores, relevance };
}

function filterAndRankAIContent(items, { minScore = 1, limit = 50 } = {}) {
  const scored = items
    .map((item) => {
      const scores = computeRelevanceScore(item);
      return { ...item, ...scores };
    })
    .filter((item) => item.relevance >= minScore);

  scored.sort((a, b) => b.relevance - a.relevance);

  const filtered = scored.slice(0, limit);

  const counts = { ai: 0, agents: 0, web3: 0, market: 0, learning: 0 };
  for (const item of filtered) {
    counts[item.category] = (counts[item.category] || 0) + 1;
  }

  logger.info(
    `Filtered ${items.length} → ${filtered.length} relevant items ` +
    `(AI: ${counts.ai}, Agents: ${counts.agents}, Web3: ${counts.web3}, Market: ${counts.market}, Learning: ${counts.learning})`,
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
  return {
    ai: items.filter((i) => i.category === 'ai'),
    agents: items.filter((i) => i.category === 'agents'),
    web3: items.filter((i) => i.category === 'web3'),
    market: items.filter((i) => i.category === 'market'),
    learning: items.filter((i) => i.category === 'learning'),
  };
}

module.exports = {
  filterAndRankAIContent,
  extractTrendingTopics,
  computeRelevanceScore,
  splitByCategory,
};
