const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const logger = require('../utils/logger').child('image');

const IMAGE_API_URL = 'https://api.asi1.ai/v1/image/generate';
const IMAGES_DIR = path.resolve(process.cwd(), 'images');

async function saveBase64Image(base64Data, filename) {
  await fs.ensureDir(IMAGES_DIR);
  const filePath = path.join(IMAGES_DIR, filename);

  let raw = base64Data;
  if (typeof raw === 'object') {
    raw = raw.b64_json || raw.base64 || JSON.stringify(raw);
  }
  if (typeof raw === 'string' && raw.startsWith('data:')) {
    raw = raw.split(',')[1];
  }

  const buffer = Buffer.from(raw, 'base64');
  await fs.writeFile(filePath, buffer);
  logger.info(`Image saved: ${filename}`);
  return `images/${filename}`;
}

async function generateImage(prompt, { size = '1024x1024', model = 'asi1-mini' } = {}) {
  const apiKey = process.env.LLM_API_KEY;
  if (!apiKey) {
    logger.warn('No LLM_API_KEY — skipping image generation');
    return null;
  }

  try {
    const { data } = await axios.post(
      IMAGE_API_URL,
      { model, prompt, size },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 90_000,
      },
    );

    const url = data?.images?.[0]?.url;
    if (url && url.startsWith('http')) {
      logger.info(`Image URL received: ${prompt.slice(0, 40)}...`);
      return url;
    }

    const b64 = data?.images?.[0]?.b64_json
      || data?.images?.[0]?.base64
      || data?.data?.[0]?.b64_json
      || data?.data?.[0]?.base64
      || data?.data;

    if (b64) {
      return b64;
    }

    logger.warn(`Image API: unexpected response shape — keys: ${Object.keys(data || {})}`);
    return null;
  } catch (err) {
    const resp = err.response?.data;
    logger.warn(`Image generation failed: ${err.message}${resp ? ' — ' + JSON.stringify(resp).slice(0, 200) : ''}`);
    return null;
  }
}

async function generateArticleImages(trends, dateStr) {
  const topTrend = trends[0]?.topic || 'artificial intelligence';
  const prompts = {
    banner: `Modern tech newsletter banner: "${topTrend}" theme, futuristic digital art, dark background, glowing blue-purple accents, no text`,
    ai: 'Neural network brain illustration, glowing nodes, abstract modern tech art, blue cyan tones',
    agents: 'Autonomous AI agents collaborating in digital workspace, purple teal color scheme, futuristic',
    web3: 'Blockchain decentralized network illustration, interconnected nodes, gold dark theme',
  };

  const images = {};

  for (const [key, prompt] of Object.entries(prompts)) {
    const result = await generateImage(prompt);
    if (!result) continue;

    if (typeof result === 'string' && result.startsWith('http')) {
      images[key] = result;
    } else {
      const filename = `${key}-${dateStr}.png`;
      const relativePath = await saveBase64Image(result, filename);
      images[key] = relativePath;
    }
  }

  logger.info(`Generated ${Object.keys(images).length}/${Object.keys(prompts).length} images`);
  return images;
}

module.exports = { generateImage, generateArticleImages };
