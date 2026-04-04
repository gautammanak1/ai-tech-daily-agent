const Parser = require('rss-parser');
const logger = require('../utils/logger').child('rss');

const parser = new Parser({
  timeout: 15_000,
  headers: {
    'User-Agent': 'AI-Tech-Daily-Agent/1.0 (RSS Reader)',
  },
});

async function fetchFeed(feed) {
  try {
    const data = await parser.parseURL(feed.url);
    const items = (data.items || []).slice(0, 25).map((item) => ({
      title: item.title?.trim() || '',
      link: item.link || '',
      description: (item.contentSnippet || item.content || '').slice(0, 500).trim(),
      publishedAt: item.isoDate || item.pubDate || null,
      source: feed.name,
      sourceWeight: feed.weight,
      origin: 'rss',
    }));
    logger.info(`Fetched ${items.length} items from ${feed.name}`);
    return items;
  } catch (err) {
    logger.warn(`Failed to fetch ${feed.name}: ${err.message}`);
    return [];
  }
}

async function fetchAllFeeds(feeds) {
  const results = await Promise.allSettled(feeds.map(fetchFeed));
  return results.flatMap((r) => (r.status === 'fulfilled' ? r.value : []));
}

module.exports = { fetchFeed, fetchAllFeeds };
