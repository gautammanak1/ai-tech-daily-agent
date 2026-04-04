const fs = require('fs-extra');
const path = require('path');
const logger = require('./logger').child('fileWriter');

async function writeArticle(filename, content, outputDir) {
  const dir = path.resolve(process.cwd(), outputDir);
  await fs.ensureDir(dir);
  const filePath = path.join(dir, filename);
  await fs.writeFile(filePath, content, 'utf-8');
  logger.info(`Article written to ${filePath}`);
  return filePath;
}

async function articleExists(filename, outputDir) {
  const filePath = path.join(path.resolve(process.cwd(), outputDir), filename);
  return fs.pathExists(filePath);
}

module.exports = { writeArticle, articleExists };
