RSS_FEEDS = [
    {"name": "Google News — AI", "url": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en", "weight": 3, "category": "ai"},
    {"name": "Google News — AI Agents", "url": "https://news.google.com/rss/search?q=%22ai+agent%22+OR+%22ai+agents%22+OR+%22autonomous+agent%22&hl=en-US&gl=US&ceid=US:en", "weight": 4, "category": "agents"},
    {"name": "Google News — Agent Frameworks", "url": "https://news.google.com/rss/search?q=langchain+OR+crewai+OR+%22crew+ai%22+OR+autogen+OR+%22fetch.ai%22+OR+composio+OR+daytona+OR+%22a2a+protocol%22&hl=en-US&gl=US&ceid=US:en", "weight": 5, "category": "agents"},
    {"name": "Google News — uAgents Fetch.ai", "url": "https://news.google.com/rss/search?q=%22uagents%22+OR+%22fetch.ai+agent%22+OR+%22agentverse%22+OR+%22asi+alliance%22&hl=en-US&gl=US&ceid=US:en", "weight": 5, "category": "agents"},
    {"name": "Google News — MCP A2A", "url": "https://news.google.com/rss/search?q=%22model+context+protocol%22+OR+%22agent+to+agent%22+OR+%22a2a+protocol%22+OR+%22google+a2a%22&hl=en-US&gl=US&ceid=US:en", "weight": 5, "category": "agents"},
    {"name": "TechCrunch — AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "weight": 4, "category": "ai"},
    {"name": "The Verge — AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "weight": 4, "category": "ai"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "weight": 3, "category": "ai"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "weight": 2, "category": "tech"},
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "weight": 3, "category": "web3"},
    {"name": "Google News — Web3", "url": "https://news.google.com/rss/search?q=web3+OR+blockchain+OR+defi+OR+%22smart+contract%22&hl=en-US&gl=US&ceid=US:en", "weight": 2, "category": "web3"},
    {"name": "Google News — Tech Market", "url": "https://news.google.com/rss/search?q=tech+stocks+OR+startup+funding+OR+tech+layoffs+OR+IPO&hl=en-US&gl=US&ceid=US:en", "weight": 2, "category": "market"},
    {"name": "TechCrunch — Startups", "url": "https://techcrunch.com/category/startups/feed/", "weight": 3, "category": "market"},
    {"name": "Dev.to — AI", "url": "https://dev.to/feed/tag/ai", "weight": 3, "category": "learning"},
    {"name": "Dev.to — AI Agents", "url": "https://dev.to/feed/tag/agents", "weight": 4, "category": "agents"},
    {"name": "Dev.to — LangChain", "url": "https://dev.to/feed/tag/langchain", "weight": 4, "category": "agents"},
    {"name": "Dev.to — Web3", "url": "https://dev.to/feed/tag/web3", "weight": 3, "category": "learning"},
    {"name": "Dev.to — Tutorial", "url": "https://dev.to/feed/tag/tutorial", "weight": 2, "category": "learning"},
]

HACKERNEWS_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKERNEWS_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item"
HACKERNEWS_MAX_ITEMS = 50

# Specific repos to always track for latest releases/activity
TRACKED_FRAMEWORK_REPOS = [
    {"owner": "fetchai", "repo": "uAgents", "label": "Fetch.ai uAgents"},
    {"owner": "fetchai", "repo": "fetchd", "label": "Fetch.ai Network"},
    {"owner": "langchain-ai", "repo": "langchain", "label": "LangChain"},
    {"owner": "langchain-ai", "repo": "langgraph", "label": "LangGraph"},
    {"owner": "crewAIInc", "repo": "crewAI", "label": "CrewAI"},
    {"owner": "microsoft", "repo": "autogen", "label": "Microsoft AutoGen"},
    {"owner": "composiohq", "repo": "composio", "label": "Composio"},
    {"owner": "daytonaio", "repo": "daytona", "label": "Daytona"},
    {"owner": "google", "repo": "A2A", "label": "Google A2A"},
    {"owner": "modelcontextprotocol", "repo": "servers", "label": "MCP Servers"},
    {"owner": "modelcontextprotocol", "repo": "specification", "label": "MCP Spec"},
    {"owner": "Significant-Gravitas", "repo": "AutoGPT", "label": "AutoGPT"},
    {"owner": "openai", "repo": "openai-agents-python", "label": "OpenAI Agents SDK"},
    {"owner": "anthropics", "repo": "anthropic-sdk-python", "label": "Anthropic SDK"},
    {"owner": "phidatahq", "repo": "phidata", "label": "Phidata"},
    {"owner": "pydantic", "repo": "pydantic-ai", "label": "Pydantic AI"},
    {"owner": "BerriAI", "repo": "litellm", "label": "LiteLLM"},
    {"owner": "vercel", "repo": "ai", "label": "Vercel AI SDK"},
    {"owner": "SmitheryAI", "repo": "mcp-registry", "label": "MCP Registry (Smithery)"},
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "llm", "large language model", "gpt", "openai",
    "anthropic", "claude", "gemini", "mistral", "llama", "transformer",
    "diffusion", "stable diffusion", "midjourney", "generative ai",
    "chatbot", "nlp", "natural language", "computer vision", "robotics",
    "autonomous", "reinforcement learning", "fine-tuning", "rag",
    "retrieval augmented", "vector database", "embedding", "prompt",
    "multi-modal", "multimodal", "foundation model", "copilot",
    "hugging face", "pytorch", "tensorflow", "mlops", "ai safety",
    "alignment", "agi", "superintelligence",
]

AGENT_KEYWORDS = [
    "ai agent", "ai agents", "autonomous agent", "agentic", "agentic ai",
    "multi-agent", "multi agent", "agent framework", "langchain", "langgraph",
    "autogen", "crewai", "crew ai", "autogpt", "auto-gpt", "babyagi",
    "function calling", "tool use", "tool calling", "mcp", "model context protocol",
    "a2a", "a2a protocol", "agent-to-agent", "agent protocol", "agent orchestration",
    "openai agents", "claude agent", "copilot agent", "browser agent",
    "coding agent", "agent sdk", "swarm", "fetch.ai", "uagent", "uagents",
    "agentverse", "asi alliance", "composio", "daytona", "phidata",
    "pydantic ai", "litellm", "vercel ai", "smithery",
    "react agent", "reasoning agent", "chain of thought",
    "agent memory", "agent tools", "agent planning", "agent loop",
]

WEB3_KEYWORDS = [
    "web3", "blockchain", "ethereum", "solana", "polygon", "bitcoin",
    "smart contract", "defi", "decentralized finance", "nft", "dao",
    "dapp", "token", "tokenomics", "staking", "layer 2", "l2", "rollup",
    "zk proof", "zero knowledge", "ipfs", "metamask", "hardhat", "foundry",
    "solidity", "cosmos", "polkadot", "avalanche", "arbitrum", "optimism",
    "base chain", "crypto", "cryptocurrency", "depin", "rwa",
    "fetch.ai", "asi token", "ocean protocol",
]

MARKET_KEYWORDS = [
    "funding", "valuation", "ipo", "acquisition", "merger", "startup",
    "series a", "series b", "series c", "venture capital", "vc",
    "layoff", "hiring", "revenue", "earnings", "stock", "market cap",
    "regulation", "antitrust", "lawsuit", "partnership", "deal",
    "apple", "google", "microsoft", "amazon", "meta", "nvidia", "tesla",
    "semiconductor", "chip", "data center", "cloud computing",
]

ALL_KEYWORDS = AI_KEYWORDS + AGENT_KEYWORDS + WEB3_KEYWORDS + MARKET_KEYWORDS

ARTICLE_CONFIG = {
    "max_items": 25,
    "max_trends": 5,
    "output_dir": "articles",
    "images_dir": "images",
}
