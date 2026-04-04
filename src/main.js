require('dotenv').config();

const { fetchAllNews } = require('./agents/fetchNews');
const { filterAndRankAIContent, extractTrendingTopics } = require('./agents/filterAI');
const { summarizeItems } = require('./agents/summarize');
const { generateArticle } = require('./agents/generateArticle');
const { writeArticle, articleExists } = require('./utils/fileWriter');
const { publishToPublicRepo } = require('./services/publishService');
const { toISODate } = require('./utils/dateFormatter');
const { ARTICLE_CONFIG } = require('./config/sources');
const logger = require('./utils/logger').child('main');
const simpleGit = require('simple-git');
const path = require('path');

const git = simpleGit(path.resolve(__dirname, '..'));

async function commitAndPush(filePath, date) {
  if (process.env.DRY_RUN === 'true') {
    logger.info('DRY_RUN enabled — skipping git commit');
    return;
  }

  try {
    const userName = process.env.GIT_USER_NAME || 'ai-tech-daily-bot';
    const userEmail = process.env.GIT_USER_EMAIL || 'bot@example.com';

    await git.addConfig('user.name', userName, false, 'local');
    await git.addConfig('user.email', userEmail, false, 'local');
    await git.add(filePath);
    await git.commit(`docs: add AI trends article for ${date}`);
    await git.push();
    logger.info('Changes committed and pushed');
  } catch (err) {
    logger.error(`Git operation failed: ${err.message}`);
    throw err;
  }
}

async function run() {
  const startTime = Date.now();
  const date = toISODate();
  const filename = `${date}.md`;

  logger.info(`--- AI Tech Daily Agent — ${date} ---`);

  const exists = await articleExists(filename, ARTICLE_CONFIG.outputDir);
  if (exists) {
    logger.info(`Article for ${date} already exists — skipping`);
    return;
  }

  logger.info('Step 1/5: Fetching news from all sources...');
  const rawItems = await fetchAllNews();

  if (rawItems.length === 0) {
    logger.error('No items fetched from any source — aborting');
    process.exitCode = 1;
    return;
  }

  logger.info('Step 2/5: Filtering AI-relevant content...');
  let aiItems = filterAndRankAIContent(rawItems);

  if (aiItems.length === 0) {
    logger.warn('No AI-relevant items found — using top raw items as fallback');
    aiItems = rawItems.slice(0, 10).map((item) => ({ ...item, relevance: 1 }));
  }

  logger.info('Step 3/5: Extracting trending topics...');
  const trends = extractTrendingTopics(aiItems, ARTICLE_CONFIG.maxTopTrends);
  logger.info('Trending topics:', trends);

  logger.info('Step 4/5: Summarizing news items...');
  const summarized = await summarizeItems(aiItems);

  logger.info('Step 5/5: Generating article...');
  const article = await generateArticle(summarized, trends);

  const filePath = await writeArticle(filename, article, ARTICLE_CONFIG.outputDir);
  await commitAndPush(filePath, date);

  logger.info('Step 6/6: Publishing to public repo...');
  await publishToPublicRepo(article, date);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  logger.info(`Done in ${elapsed}s — article: ${filename}`);
}

run().catch((err) => {
  logger.error(`Fatal error: ${err.message}`);
  process.exitCode = 1;
});
