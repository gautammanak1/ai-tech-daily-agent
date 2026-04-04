const axios = require('axios');
const logger = require('../utils/logger').child('github');

const SEARCH_QUERIES = [
  'ai agent',
  'llm agent framework',
  'mcp server',
  'agentic ai',
  'autonomous agent',
];

async function searchTrendingRepos() {
  const oneWeekAgo = new Date(Date.now() - 7 * 86400_000).toISOString().slice(0, 10);

  const allRepos = [];

  for (const query of SEARCH_QUERIES) {
    try {
      const { data } = await axios.get('https://api.github.com/search/repositories', {
        params: {
          q: `${query} created:>${oneWeekAgo}`,
          sort: 'stars',
          order: 'desc',
          per_page: 5,
        },
        headers: {
          Accept: 'application/vnd.github+json',
          'User-Agent': 'AI-Tech-Daily-Agent/1.0',
        },
        timeout: 15_000,
      });

      const repos = (data?.items || []).map((r) => ({
        name: r.full_name,
        url: r.html_url,
        description: (r.description || '').slice(0, 200),
        stars: r.stargazers_count,
        language: r.language,
        createdAt: r.created_at,
        query,
      }));

      allRepos.push(...repos);
    } catch (err) {
      logger.warn(`GitHub search failed for "${query}": ${err.message}`);
    }
  }

  const unique = deduplicateRepos(allRepos);
  unique.sort((a, b) => b.stars - a.stars);

  const top = unique.slice(0, 8);
  logger.info(`Found ${top.length} trending AI agent repos`);
  return top;
}

function deduplicateRepos(repos) {
  const seen = new Set();
  return repos.filter((r) => {
    if (seen.has(r.name)) return false;
    seen.add(r.name);
    return true;
  });
}

module.exports = { searchTrendingRepos };
