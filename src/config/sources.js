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

  // Market & Business
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
  {
    name: 'Google News — Tech Industry',
    url: 'https://news.google.com/rss/search?q=technology+industry+news&hl=en-US&gl=US&ceid=US:en',
    weight: 2,
    category: 'tech',
  },
];

const REDDIT_SUBREDDITS = [
  { name: 'r/artificial', subreddit: 'artificial', weight: 3, category: 'ai' },
  { name: 'r/MachineLearning', subreddit: 'MachineLearning', weight: 4, category: 'ai' },
  { name: 'r/LocalLLaMA', subreddit: 'LocalLLaMA', weight: 3, category: 'agents' },
  { name: 'r/programming', subreddit: 'programming', weight: 1, category: 'tech' },
  { name: 'r/technology', subreddit: 'technology', weight: 2, category: 'market' },
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

const MARKET_KEYWORDS = [
  'funding', 'valuation', 'ipo', 'acquisition', 'merger', 'startup',
  'series a', 'series b', 'series c', 'venture capital', 'vc',
  'layoff', 'hiring', 'revenue', 'earnings', 'stock', 'market cap',
  'regulation', 'antitrust', 'lawsuit', 'partnership', 'deal',
  'apple', 'google', 'microsoft', 'amazon', 'meta', 'nvidia', 'tesla',
  'semiconductor', 'chip', 'data center', 'cloud computing',
];

const ARTICLE_CONFIG = {
  maxItemsInArticle: 20,
  maxTopTrends: 5,
  outputDir: 'articles',
};

module.exports = {
  RSS_FEEDS,
  REDDIT_SUBREDDITS,
  HACKERNEWS,
  AI_KEYWORDS,
  AGENT_KEYWORDS,
  MARKET_KEYWORDS,
  ARTICLE_CONFIG,
};
