const axios = require('axios');
const logger = require('../utils/logger').child('hackernews');
const { HACKERNEWS } = require('../config/sources');

async function fetchItem(id) {
  try {
    const { data } = await axios.get(`${HACKERNEWS.itemUrl}/${id}.json`, {
      timeout: 8_000,
    });
    return data;
  } catch {
    return null;
  }
}

async function fetchTopStories() {
  try {
    const { data: ids } = await axios.get(HACKERNEWS.topStoriesUrl, {
      timeout: 10_000,
    });

    const topIds = ids.slice(0, HACKERNEWS.maxItems);
    const stories = await Promise.allSettled(topIds.map(fetchItem));

    const items = stories
      .map((r) => (r.status === 'fulfilled' ? r.value : null))
      .filter(Boolean)
      .filter((s) => s.type === 'story' && s.title)
      .map((s) => ({
        title: s.title.trim(),
        link: s.url || `https://news.ycombinator.com/item?id=${s.id}`,
        description: '',
        publishedAt: new Date(s.time * 1000).toISOString(),
        source: 'Hacker News',
        sourceWeight: HACKERNEWS.weight,
        origin: 'hackernews',
        score: s.score || 0,
      }));

    logger.info(`Fetched ${items.length} stories from Hacker News`);
    return items;
  } catch (err) {
    logger.warn(`Failed to fetch Hacker News: ${err.message}`);
    return [];
  }
}

module.exports = { fetchTopStories };
