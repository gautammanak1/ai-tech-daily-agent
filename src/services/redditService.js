const axios = require('axios');
const logger = require('../utils/logger').child('reddit');

let cachedToken = null;
let tokenExpiry = 0;

async function getAccessToken(clientId, clientSecret) {
  if (cachedToken && Date.now() < tokenExpiry) return cachedToken;

  try {
    const { data } = await axios.post(
      'https://www.reddit.com/api/v1/access_token',
      'grant_type=client_credentials',
      {
        auth: { username: clientId, password: clientSecret },
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        timeout: 10_000,
      },
    );
    cachedToken = data.access_token;
    tokenExpiry = Date.now() + (data.expires_in - 60) * 1000;
    return cachedToken;
  } catch (err) {
    logger.warn(`Reddit auth failed: ${err.message}`);
    return null;
  }
}

async function fetchSubreddit(subredditConfig, token) {
  const { subreddit, name, weight } = subredditConfig;
  try {
    const { data } = await axios.get(
      `https://oauth.reddit.com/r/${subreddit}/hot.json?limit=20`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'User-Agent': 'AI-Tech-Daily-Agent/1.0',
        },
        timeout: 10_000,
      },
    );

    const items = (data?.data?.children || [])
      .filter((c) => !c.data.stickied)
      .map((c) => ({
        title: c.data.title?.trim() || '',
        link: `https://reddit.com${c.data.permalink}`,
        description: (c.data.selftext || '').slice(0, 500).trim(),
        publishedAt: new Date(c.data.created_utc * 1000).toISOString(),
        source: name,
        sourceWeight: weight,
        origin: 'reddit',
        score: c.data.score || 0,
      }));

    logger.info(`Fetched ${items.length} posts from ${name}`);
    return items;
  } catch (err) {
    logger.warn(`Failed to fetch ${name}: ${err.message}`);
    return [];
  }
}

async function fetchAllSubreddits(subreddits) {
  const clientId = process.env.REDDIT_CLIENT_ID;
  const clientSecret = process.env.REDDIT_SECRET;

  if (!clientId || !clientSecret) {
    logger.warn('Reddit credentials not configured — skipping Reddit');
    return [];
  }

  const token = await getAccessToken(clientId, clientSecret);
  if (!token) return [];

  const results = await Promise.allSettled(
    subreddits.map((sub) => fetchSubreddit(sub, token)),
  );
  return results.flatMap((r) => (r.status === 'fulfilled' ? r.value : []));
}

module.exports = { fetchAllSubreddits };
