const fs = require('fs-extra');
const path = require('path');
const logger = require('./logger').child('fileWriter');

async function getAvailableFilename(date, outputDir) {
  const dir = path.resolve(process.cwd(), outputDir);
  await fs.ensureDir(dir);

  const base = `${date}.md`;
  const basePath = path.join(dir, base);

  if (!(await fs.pathExists(basePath))) {
    return base;
  }

  for (let i = 2; i <= 20; i++) {
    const name = `${date}-${i}.md`;
    if (!(await fs.pathExists(path.join(dir, name)))) {
      logger.info(`${base} exists — using ${name}`);
      return name;
    }
  }

  return base;
}

async function writeArticle(filename, content, outputDir) {
  const dir = path.resolve(process.cwd(), outputDir);
  await fs.ensureDir(dir);
  const filePath = path.join(dir, filename);
  await fs.writeFile(filePath, content, 'utf-8');
  logger.info(`Article written to ${filePath}`);
  return filePath;
}

module.exports = { writeArticle, getAvailableFilename };
