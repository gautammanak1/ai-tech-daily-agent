const { RSS_FEEDS } = require('../config/sources');
const { fetchAllFeeds } = require('../services/rssService');
const { fetchTopStories } = require('../services/hackernewsService');
const logger = require('../utils/logger').child('fetchNews');

function deduplicateItems(items) {
  const seen = new Map();

  for (const item of items) {
    const key = normalizeTitle(item.title);
    const existing = seen.get(key);

    if (!existing || rankItem(item) > rankItem(existing)) {
      seen.set(key, item);
    }
  }

  return [...seen.values()];
}

function normalizeTitle(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .slice(0, 8)
    .join(' ');
}

function rankItem(item) {
  let rank = item.sourceWeight || 1;
  if (item.score) rank += Math.log10(Math.max(item.score, 1));
  return rank;
}

async function fetchAllNews() {
  logger.info('Starting news fetch from all sources...');

  const [rssItems, hnItems] = await Promise.allSettled([
    fetchAllFeeds(RSS_FEEDS),
    fetchTopStories(),
  ]).then((results) =>
    results.map((r) => (r.status === 'fulfilled' ? r.value : [])),
  );

  const allItems = [...rssItems, ...hnItems];
  logger.info(`Raw items collected: ${allItems.length}`);

  const unique = deduplicateItems(allItems);
  logger.info(`After deduplication: ${unique.length}`);

  return unique;
}

module.exports = { fetchAllNews, deduplicateItems };
