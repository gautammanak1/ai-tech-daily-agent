const axios = require('axios');
const logger = require('../utils/logger').child('summarize');

function getLLMConfig() {
  return {
    apiKey: process.env.LLM_API_KEY,
    baseUrl: (process.env.LLM_BASE_URL || 'https://api.asi1.ai/v1').replace(/\/+$/, ''),
    model: process.env.LLM_MODEL || 'asi1',
  };
}

async function callLLM(systemPrompt, userPrompt, { temperature = 0.7, maxTokens = 2048 } = {}) {
  const { apiKey, baseUrl, model } = getLLMConfig();

  if (!apiKey) {
    logger.warn('No LLM_API_KEY set — using fallback summarization');
    return null;
  }

  try {
    const { data } = await axios.post(
      `${baseUrl}/chat/completions`,
      {
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature,
        max_tokens: maxTokens,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 60_000,
      },
    );

    return data.choices?.[0]?.message?.content?.trim() || null;
  } catch (err) {
    logger.error(`LLM call failed: ${err.message}`);
    return null;
  }
}

function fallbackSummarize(item) {
  const desc = item.description || '';
  if (desc.length > 120) return desc.slice(0, 200).trim() + '...';
  return item.title;
}

async function summarizeItems(items) {
  const BATCH_SIZE = 8;
  const summarized = [];

  for (let i = 0; i < items.length; i += BATCH_SIZE) {
    const batch = items.slice(i, i + BATCH_SIZE);
    const batchText = batch
      .map((item, idx) => `[${idx + 1}] ${item.title}\n${item.description || '(no description)'}`)
      .join('\n\n');

    const systemPrompt = `You are a sharp tech journalist writing a daily AI newsletter. 
Summarize each news item in 1-2 concise, punchy sentences. 
Write in an engaging but professional voice — avoid hype words like "revolutionary" or "groundbreaking".
Focus on what happened, why it matters, and who it affects.
Return a JSON array of objects with "index" (1-based) and "summary" fields. Return ONLY valid JSON.`;

    const result = await callLLM(systemPrompt, batchText);

    if (result) {
      try {
        const jsonStr = result.replace(/```json\n?/g, '').replace(/```/g, '').trim();
        const parsed = JSON.parse(jsonStr);

        for (const entry of parsed) {
          const originalIdx = i + (entry.index - 1);
          if (originalIdx < items.length) {
            summarized.push({ ...items[originalIdx], summary: entry.summary });
          }
        }
        continue;
      } catch (parseErr) {
        logger.warn(`Failed to parse LLM batch response: ${parseErr.message}`);
      }
    }

    for (const item of batch) {
      summarized.push({ ...item, summary: fallbackSummarize(item) });
    }
  }

  logger.info(`Summarized ${summarized.length}/${items.length} items`);
  return summarized;
}

module.exports = { summarizeItems, callLLM };
