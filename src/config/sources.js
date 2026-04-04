const RSS_FEEDS = [
  // AI & AI Agents
  {
    name: 'Google News — AI',
    url: 'https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en',
    weight: 3,
    category: 'ai',
  },
  {
    name: 'Google News — AI Agents',
    url: 'https://news.google.com/rss/search?q=%22ai+agent%22+OR+%22ai+agents%22+OR+%22autonomous+agent%22&hl=en-US&gl=US&ceid=US:en',
    weight: 4,
    category: 'agents',
  },
  {
    name: 'TechCrunch — AI',
    url: 'https://techcrunch.com/category/artificial-intelligence/feed/',
    weight: 4,
    category: 'ai',
  },
  {
    name: 'The Verge — AI',
    url: 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
    weight: 4,
    category: 'ai',
  },
  {
    name: 'MIT Technology Review — AI',
    url: 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
    weight: 3,
    category: 'ai',
  },
  {
    name: 'Ars Technica — Tech',
    url: 'https://feeds.arstechnica.com/arstechnica/technology-lab',
    weight: 2,
    category: 'tech',
  },

  // Web3 / Blockchain / Crypto
  {
    name: 'CoinDesk',
    url: 'https://www.coindesk.com/arc/outboundfeeds/rss/',
    weight: 3,
    category: 'web3',
  },
  {
    name: 'The Block',
    url: 'https://www.theblock.co/rss.xml',
    weight: 3,
    category: 'web3',
  },
  {
    name: 'Google News — Web3',
    url: 'https://news.google.com/rss/search?q=web3+OR+blockchain+OR+defi+OR+%22smart+contract%22&hl=en-US&gl=US&ceid=US:en',
    weight: 2,
    category: 'web3',
  },

  // Market & Startups
  {
    name: 'Google News — Tech Market',
    url: 'https://news.google.com/rss/search?q=tech+stocks+OR+startup+funding+OR+tech+layoffs+OR+IPO&hl=en-US&gl=US&ceid=US:en',
    weight: 2,
    category: 'market',
  },
  {
    name: 'TechCrunch — Startups',
    url: 'https://techcrunch.com/category/startups/feed/',
    weight: 3,
    category: 'market',
  },

  // Developer / Learning
  {
    name: 'Dev.to — AI',
    url: 'https://dev.to/feed/tag/ai',
    weight: 3,
    category: 'learning',
  },
  {
    name: 'Dev.to — Web3',
    url: 'https://dev.to/feed/tag/web3',
    weight: 3,
    category: 'learning',
  },
  {
    name: 'Dev.to — Tutorial',
    url: 'https://dev.to/feed/tag/tutorial',
    weight: 2,
    category: 'learning',
  },
];

const HACKERNEWS = {
  topStoriesUrl: 'https://hacker-news.firebaseio.com/v0/topstories.json',
  itemUrl: 'https://hacker-news.firebaseio.com/v0/item',
  maxItems: 50,
  weight: 2,
};

const AI_KEYWORDS = [
  'ai', 'artificial intelligence', 'machine learning', 'deep learning',
  'neural network', 'llm', 'large language model', 'gpt', 'openai',
  'anthropic', 'claude', 'gemini', 'mistral', 'llama', 'transformer',
  'diffusion', 'stable diffusion', 'midjourney', 'generative ai',
  'chatbot', 'nlp', 'natural language', 'computer vision', 'robotics',
  'autonomous', 'reinforcement learning', 'fine-tuning', 'rag',
  'retrieval augmented', 'vector database', 'embedding', 'prompt',
  'multi-modal', 'multimodal', 'foundation model', 'copilot',
  'hugging face', 'pytorch', 'tensorflow', 'mlops', 'ai safety',
  'alignment', 'agi', 'superintelligence',
];

const AGENT_KEYWORDS = [
  'ai agent', 'ai agents', 'autonomous agent', 'agentic', 'agentic ai',
  'multi-agent', 'multi agent', 'agent framework', 'langchain', 'langgraph',
  'autogen', 'crewai', 'crew ai', 'autogpt', 'auto-gpt', 'babyagi',
  'function calling', 'tool use', 'tool calling', 'mcp', 'model context protocol',
  'a2a', 'agent-to-agent', 'agent protocol', 'agent orchestration',
  'openai agents', 'claude agent', 'gemini agent', 'copilot agent',
  'browser agent', 'coding agent', 'agent sdk', 'swarm', 'taskweaver',
  'semantic kernel', 'fetch.ai', 'uagent', 'agent memory', 'agent planning',
  'react agent', 'reasoning agent', 'chain of thought',
];

const WEB3_KEYWORDS = [
  'web3', 'blockchain', 'ethereum', 'solana', 'polygon', 'bitcoin',
  'smart contract', 'defi', 'decentralized finance', 'nft', 'dao',
  'dapp', 'decentralized app', 'token', 'tokenomics', 'staking',
  'layer 2', 'l2', 'rollup', 'zk proof', 'zero knowledge',
  'ipfs', 'decentralized storage', 'web3 wallet', 'metamask',
  'hardhat', 'foundry', 'solidity', 'rust blockchain', 'cosmos',
  'polkadot', 'avalanche', 'arbitrum', 'optimism', 'base chain',
  'crypto', 'cryptocurrency', 'depin', 'rwa', 'real world asset',
];

const MARKET_KEYWORDS = [
  'funding', 'valuation', 'ipo', 'acquisition', 'merger', 'startup',
  'series a', 'series b', 'series c', 'venture capital', 'vc',
  'layoff', 'hiring', 'revenue', 'earnings', 'stock', 'market cap',
  'regulation', 'antitrust', 'lawsuit', 'partnership', 'deal',
  'apple', 'google', 'microsoft', 'amazon', 'meta', 'nvidia', 'tesla',
  'semiconductor', 'chip', 'data center', 'cloud computing',
];

const ARTICLE_CONFIG = {
  maxItemsInArticle: 25,
  maxTopTrends: 5,
  outputDir: 'articles',
};

module.exports = {
  RSS_FEEDS,
  HACKERNEWS,
  AI_KEYWORDS,
  AGENT_KEYWORDS,
  WEB3_KEYWORDS,
  MARKET_KEYWORDS,
  ARTICLE_CONFIG,
};
