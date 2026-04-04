const simpleGit = require('simple-git');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');
const logger = require('../utils/logger').child('publish');

const PUBLIC_REPO = 'https://github.com/gautammanak1/ai-tech-daily.git';
const PUBLIC_FILENAME = 'article.md';

async function publishToPublicRepo(articleContent, date) {
  const tmpDir = path.join(os.tmpdir(), `ai-tech-daily-publish-${Date.now()}`);

  try {
    logger.info(`Cloning public repo to ${tmpDir}...`);
    const git = simpleGit();

    const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || '';
    let cloneUrl = PUBLIC_REPO;
    if (token) {
      cloneUrl = PUBLIC_REPO.replace('https://', `https://x-access-token:${token}@`);
    }

    await git.clone(cloneUrl, tmpDir, ['--depth', '1']);

    const repoGit = simpleGit(tmpDir);
    const userName = process.env.GIT_USER_NAME || 'ai-tech-daily-bot';
    const userEmail = process.env.GIT_USER_EMAIL || 'bot@example.com';
    await repoGit.addConfig('user.name', userName, false, 'local');
    await repoGit.addConfig('user.email', userEmail, false, 'local');

    const filePath = path.join(tmpDir, PUBLIC_FILENAME);
    await fs.writeFile(filePath, articleContent, 'utf-8');

    await repoGit.add(PUBLIC_FILENAME);

    const status = await repoGit.status();
    if (status.staged.length === 0 && status.modified.length === 0) {
      logger.info('No changes to publish — article.md is already up to date');
      return;
    }

    await repoGit.commit(`docs: update AI trends article — ${date}`);
    await repoGit.push('origin', 'main');
    logger.info('Article published to public repo as article.md');
  } catch (err) {
    logger.error(`Failed to publish to public repo: ${err.message}`);
  } finally {
    await fs.remove(tmpDir).catch(() => {});
  }
}

module.exports = { publishToPublicRepo };
