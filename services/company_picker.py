"""Auto-rotate companies for daily articles. Never repeat recently covered ones."""

import json
import logging
import random
import re
from datetime import datetime
from pathlib import Path

log = logging.getLogger("picker")

COMPANIES = [
    # === BIG TECH ===
    {"name": "Google", "slug": "google", "topics": ["Gemini", "DeepMind", "A2A protocol", "Google Cloud AI", "TensorFlow", "Android AI", "Google Colab", "Vertex AI"]},
    {"name": "Microsoft", "slug": "microsoft", "topics": ["Copilot", "Azure AI", "AutoGen", "Semantic Kernel", "GitHub Copilot", "Bing AI", "TypeChat", "Phi models"]},
    {"name": "Apple", "slug": "apple", "topics": ["Apple Intelligence", "Siri AI", "Core ML", "On-device AI", "Private Cloud Compute", "MLX"]},
    {"name": "Amazon", "slug": "amazon", "topics": ["AWS Bedrock", "Alexa AI", "SageMaker", "Q Developer", "Titan models", "AWS AI services"]},
    {"name": "Meta", "slug": "meta", "topics": ["LLaMA", "PyTorch", "FAIR", "AI Research", "Ray-Ban Meta AI", "Open source models"]},
    {"name": "NVIDIA", "slug": "nvidia", "topics": ["CUDA", "GPU", "NeMo", "Triton", "Omniverse", "DGX", "AI data centers", "Blackwell"]},
    {"name": "Tesla", "slug": "tesla", "topics": ["Optimus robot", "FSD", "Dojo", "Tesla AI", "Autonomous driving"]},
    {"name": "Samsung", "slug": "samsung", "topics": ["Galaxy AI", "Gauss model", "On-device AI", "Tizen AI", "Samsung Research"]},
    {"name": "Intel", "slug": "intel", "topics": ["Gaudi", "AI accelerators", "OpenVINO", "Habana Labs", "Meteor Lake NPU"]},
    {"name": "AMD", "slug": "amd", "topics": ["ROCm", "MI300X", "Ryzen AI", "Xilinx AI", "GPU compute"]},
    {"name": "Qualcomm", "slug": "qualcomm", "topics": ["Snapdragon AI", "On-device ML", "AI Engine", "Cloud AI 100", "Edge AI"]},
    {"name": "IBM", "slug": "ibm", "topics": ["watsonx", "Granite models", "AI governance", "Red Hat AI", "Quantum computing"]},
    {"name": "Oracle", "slug": "oracle", "topics": ["OCI AI", "Oracle AI", "Database AI", "Cloud Infrastructure", "Autonomous DB"]},
    {"name": "Salesforce", "slug": "salesforce", "topics": ["Einstein AI", "Agentforce", "Slack AI", "Data Cloud", "CRM AI"]},
    {"name": "Adobe", "slug": "adobe", "topics": ["Firefly", "Sensei AI", "Creative Cloud AI", "GenStudio", "Content Credentials"]},
    # === FRONTIER AI LABS ===
    {"name": "OpenAI", "slug": "openai", "topics": ["GPT", "ChatGPT", "DALL-E", "Sora", "Agents SDK", "Codex", "Whisper", "API platform"]},
    {"name": "Anthropic", "slug": "anthropic", "topics": ["Claude", "MCP", "Constitutional AI", "Artifacts", "Claude Code", "Agentic AI Foundation"]},
    {"name": "xAI", "slug": "xai", "topics": ["Grok", "Grok models", "Colossus supercomputer", "xAI API"]},
    {"name": "Mistral AI", "slug": "mistral", "topics": ["Mistral models", "Mixtral", "Le Chat", "Open weights", "European AI", "Codestral"]},
    {"name": "Cohere", "slug": "cohere", "topics": ["Command R", "Embed API", "Rerank", "Enterprise AI", "RAG", "Aya"]},
    {"name": "AI21 Labs", "slug": "ai21", "topics": ["Jamba", "Jurassic", "Wordtune", "Task-specific models", "Enterprise LLM"]},
    {"name": "Inflection AI", "slug": "inflection", "topics": ["Pi", "Inflection models", "Personal AI", "Enterprise pivot"]},
    {"name": "Stability AI", "slug": "stabilityai", "topics": ["Stable Diffusion", "SDXL", "Stable Audio", "Open source models"]},
    {"name": "Aleph Alpha", "slug": "alephalpha", "topics": ["Luminous", "Pharia", "European sovereign AI", "Enterprise LLM"]},
    {"name": "DeepSeek", "slug": "deepseek", "topics": ["DeepSeek V3", "DeepSeek Coder", "Open source LLM", "MoE architecture"]},
    {"name": "Zhipu AI", "slug": "zhipu", "topics": ["GLM models", "ChatGLM", "Chinese AI", "CodeGeeX"]},
    {"name": "Minimax", "slug": "minimax", "topics": ["Minimax models", "Hailuo AI", "Video generation", "Chinese AI lab"]},
    # === AI AGENT FRAMEWORKS ===
    {"name": "Fetch.ai", "slug": "fetchai", "topics": ["uAgents", "Agentverse", "ASI Alliance", "DeltaV", "ASI token", "Agent economy"]},
    {"name": "LangChain", "slug": "langchain", "topics": ["LangChain framework", "LangGraph", "LangSmith", "LCEL", "Agent tooling", "RAG"]},
    {"name": "CrewAI", "slug": "crewai", "topics": ["CrewAI framework", "Multi-agent", "Role-playing agents", "Task orchestration", "CrewAI Enterprise"]},
    {"name": "Composio", "slug": "composio", "topics": ["Composio platform", "1000+ toolkits", "Agent tools", "Authentication", "Sandbox execution"]},
    {"name": "Daytona", "slug": "daytona", "topics": ["Daytona platform", "Dev environments", "AI code execution", "Sandboxing", "Infrastructure"]},
    {"name": "AutoGPT", "slug": "autogpt", "topics": ["AutoGPT framework", "Autonomous agents", "Agent marketplace", "Forge"]},
    {"name": "Pydantic AI", "slug": "pydantic-ai", "topics": ["Pydantic AI framework", "Type-safe agents", "Structured outputs", "Python AI tools"]},
    {"name": "Agno", "slug": "agno", "topics": ["Agno framework", "WebTools", "Agent OS", "Multi-backend search", "Tool ecosystem"]},
    {"name": "Semantic Kernel", "slug": "semantic-kernel", "topics": ["Microsoft SK", "AI orchestration", ".NET AI", "Planners", "Plugins"]},
    {"name": "Haystack", "slug": "haystack", "topics": ["Haystack framework", "deepset", "RAG pipelines", "Document AI", "NLP"]},
    {"name": "LlamaIndex", "slug": "llamaindex", "topics": ["LlamaIndex", "Data framework", "RAG", "Agents", "LlamaParse", "LlamaCloud"]},
    {"name": "Dify", "slug": "dify", "topics": ["Dify platform", "LLMOps", "Workflow builder", "RAG engine", "Agent IDE"]},
    {"name": "Flowise", "slug": "flowise", "topics": ["Flowise", "Visual LLM builder", "Drag-and-drop AI", "LangChain UI"]},
    {"name": "Rivet", "slug": "rivet", "topics": ["Rivet", "Visual AI builder", "Ironclad", "AI workflow IDE"]},
    {"name": "SuperAGI", "slug": "superagi", "topics": ["SuperAGI framework", "Agent infrastructure", "Marketplace", "Open source agents"]},
    {"name": "BabyAGI", "slug": "babyagi", "topics": ["BabyAGI", "Task-driven agent", "Autonomous planning", "AI task management"]},
    {"name": "Camel AI", "slug": "camelai", "topics": ["CAMEL framework", "Communicative agents", "Role-playing", "Multi-agent society"]},
    # === AI INFRASTRUCTURE & PLATFORMS ===
    {"name": "Hugging Face", "slug": "huggingface", "topics": ["Transformers", "Model Hub", "Spaces", "Datasets", "Open source AI", "Inference API"]},
    {"name": "Databricks", "slug": "databricks", "topics": ["Mosaic ML", "DBRX", "Lakehouse AI", "MLflow", "Unity Catalog"]},
    {"name": "Snowflake", "slug": "snowflake", "topics": ["Cortex AI", "Snowpark", "Arctic models", "Data Cloud AI", "Streamlit"]},
    {"name": "Weights & Biases", "slug": "wandb", "topics": ["W&B", "ML experiment tracking", "Model registry", "Prompts", "Weave"]},
    {"name": "Scale AI", "slug": "scaleai", "topics": ["Data labeling", "RLHF", "Enterprise AI", "Government AI", "Donovan"]},
    {"name": "Anyscale", "slug": "anyscale", "topics": ["Ray", "Distributed computing", "LLM serving", "Ray Serve", "AI infrastructure"]},
    {"name": "Modal", "slug": "modal", "topics": ["Modal cloud", "Serverless GPU", "Python infrastructure", "ML deployment"]},
    {"name": "Replicate", "slug": "replicate", "topics": ["Replicate platform", "Model hosting", "Cog", "Open source models", "API serving"]},
    {"name": "Together AI", "slug": "togetherai", "topics": ["Together Inference", "Fine-tuning", "Open models", "RedPajama", "GPU cluster"]},
    {"name": "Groq", "slug": "groq", "topics": ["LPU", "Inference speed", "GroqCloud", "AI hardware", "Low-latency AI"]},
    {"name": "Cerebras", "slug": "cerebras", "topics": ["Wafer-scale chip", "CS-3", "AI supercomputer", "Inference", "Condor Galaxy"]},
    {"name": "CoreWeave", "slug": "coreweave", "topics": ["GPU cloud", "AI infrastructure", "Kubernetes GPU", "HPC", "IPO"]},
    {"name": "Lambda", "slug": "lambda", "topics": ["Lambda Cloud", "GPU instances", "AI workstations", "ML infrastructure"]},
    # === AI CODING & DEVELOPER TOOLS ===
    {"name": "Cursor", "slug": "cursor", "topics": ["Cursor IDE", "AI coding", "Code completion", "Agent mode", "MCP integration"]},
    {"name": "Replit", "slug": "replit", "topics": ["Replit Agent", "AI coding", "Ghostwriter", "Cloud IDE", "Deployments"]},
    {"name": "GitHub Copilot", "slug": "github-copilot", "topics": ["Copilot", "Code suggestions", "Copilot Workspace", "Copilot Chat", "Extensions"]},
    {"name": "Codeium", "slug": "codeium", "topics": ["Windsurf", "AI coding", "Supercomplete", "Code search", "Enterprise IDE"]},
    {"name": "Tabnine", "slug": "tabnine", "topics": ["Tabnine AI", "Code completion", "Private models", "Enterprise coding AI"]},
    {"name": "Sourcegraph", "slug": "sourcegraph", "topics": ["Cody AI", "Code search", "Code intelligence", "Batch changes"]},
    {"name": "Vercel", "slug": "vercel", "topics": ["Vercel AI SDK", "v0", "Next.js AI", "Edge functions", "AI gateway"]},
    {"name": "Supabase", "slug": "supabase", "topics": ["Supabase AI", "pgvector", "Edge Functions", "Vector database", "Open source BaaS"]},
    # === AI SEARCH & KNOWLEDGE ===
    {"name": "Perplexity", "slug": "perplexity", "topics": ["Perplexity search", "AI search engine", "Sonar API", "Answer engine"]},
    {"name": "You.com", "slug": "you-com", "topics": ["You.com search", "YouChat", "AI search", "Developer APIs"]},
    {"name": "Brave Search", "slug": "brave-search", "topics": ["Brave Search AI", "Answer engine", "Privacy search", "Brave Leo"]},
    {"name": "Tavily", "slug": "tavily", "topics": ["Tavily search API", "AI research", "Web search for agents", "RAG search"]},
    {"name": "Exa", "slug": "exa", "topics": ["Exa search", "Neural search", "Embeddings search", "Knowledge API"]},
    # === AI IMAGE & VIDEO ===
    {"name": "Midjourney", "slug": "midjourney", "topics": ["Midjourney", "Image generation", "V6", "Discord AI", "AI art"]},
    {"name": "Runway", "slug": "runway", "topics": ["Gen-3", "Video generation", "Creative AI", "Motion Brush", "AI filmmaking"]},
    {"name": "Pika", "slug": "pika", "topics": ["Pika Labs", "Video AI", "Text-to-video", "AI animation"]},
    {"name": "ElevenLabs", "slug": "elevenlabs", "topics": ["Voice AI", "Text-to-speech", "Voice cloning", "Audio AI", "Dubbing"]},
    {"name": "Luma AI", "slug": "lumaai", "topics": ["Dream Machine", "3D capture", "NeRF", "Video generation", "Genie"]},
    {"name": "Leonardo AI", "slug": "leonardoai", "topics": ["Leonardo AI", "Image generation", "Creative tools", "AI assets"]},
    # === ROBOTICS & AUTONOMOUS ===
    {"name": "Boston Dynamics", "slug": "boston-dynamics", "topics": ["Spot", "Atlas", "Stretch", "Robotics AI", "Hyundai"]},
    {"name": "Figure AI", "slug": "figureai", "topics": ["Figure 01", "Humanoid robot", "OpenAI partnership", "BMW factory"]},
    {"name": "Waymo", "slug": "waymo", "topics": ["Waymo One", "Self-driving", "Autonomous vehicles", "Waymo Driver", "Robotaxi"]},
    {"name": "Cruise", "slug": "cruise", "topics": ["Cruise AV", "GM autonomous", "Self-driving cars", "Robotaxi"]},
    {"name": "1X Technologies", "slug": "1x-tech", "topics": ["NEO robot", "EVE", "Humanoid robots", "Embodied AI"]},
    # === WEB3 & CRYPTO AI ===
    {"name": "Ocean Protocol", "slug": "ocean", "topics": ["Ocean Protocol", "Data marketplace", "ASI Alliance", "Compute-to-Data"]},
    {"name": "SingularityNET", "slug": "singularitynet", "topics": ["SingularityNET", "AGIX", "ASI Alliance", "Decentralized AI", "Marketplace"]},
    {"name": "Bittensor", "slug": "bittensor", "topics": ["Bittensor", "TAO", "Decentralized ML", "Subnet mining", "AI incentives"]},
    {"name": "Render Network", "slug": "render", "topics": ["Render", "GPU rendering", "Decentralized compute", "RNDR token"]},
    {"name": "Chainlink", "slug": "chainlink", "topics": ["Chainlink", "Oracles", "CCIP", "Functions", "Smart contract data"]},
    # === AI SECURITY & SAFETY ===
    {"name": "Anthropic Safety", "slug": "anthropic-safety", "topics": ["AI safety", "Constitutional AI", "RLHF", "Alignment", "Interpretability"]},
    {"name": "OpenAI Safety", "slug": "openai-safety", "topics": ["Superalignment", "Red teaming", "AI safety", "Preparedness", "Governance"]},
    {"name": "Lakera", "slug": "lakera", "topics": ["Lakera Guard", "Prompt injection", "LLM security", "AI firewall"]},
    {"name": "Protect AI", "slug": "protectai", "topics": ["Protect AI", "ML security", "Model scanning", "Guardian", "AI BOM"]},
    # === AI DATA & VECTOR ===
    {"name": "Pinecone", "slug": "pinecone", "topics": ["Pinecone", "Vector database", "Serverless", "RAG", "Similarity search"]},
    {"name": "Weaviate", "slug": "weaviate", "topics": ["Weaviate", "Vector database", "Hybrid search", "Open source", "GraphQL"]},
    {"name": "Qdrant", "slug": "qdrant", "topics": ["Qdrant", "Vector search", "Rust-based", "Open source", "Filtering"]},
    {"name": "Chroma", "slug": "chroma", "topics": ["Chroma DB", "Embedding database", "Open source", "AI-native", "RAG"]},
    {"name": "Milvus", "slug": "milvus", "topics": ["Milvus", "Zilliz", "Vector database", "Distributed", "Open source"]},
    # === MCP & PROTOCOLS ===
    {"name": "MCP Ecosystem", "slug": "mcp-ecosystem", "topics": ["Model Context Protocol", "MCP servers", "MCP spec", "Tool integration", "Smithery"]},
    {"name": "Google A2A", "slug": "google-a2a", "topics": ["Agent-to-Agent protocol", "A2A spec", "Google agents", "Interoperability"]},
    # === EMERGING AI STARTUPS ===
    {"name": "Glean", "slug": "glean", "topics": ["Glean", "Enterprise search", "Work AI", "Knowledge graph", "Enterprise LLM"]},
    {"name": "Jasper AI", "slug": "jasper", "topics": ["Jasper", "AI marketing", "Content generation", "Brand voice", "Enterprise content"]},
    {"name": "Writer", "slug": "writer", "topics": ["Writer AI", "Enterprise content", "Palmyra models", "Full-stack AI"]},
    {"name": "Adept AI", "slug": "adept", "topics": ["Adept", "ACT-2", "Action models", "Computer use", "UI automation"]},
    {"name": "Harvey AI", "slug": "harvey", "topics": ["Harvey", "Legal AI", "AI for lawyers", "Contract analysis", "Due diligence"]},
    {"name": "Cognition", "slug": "cognition", "topics": ["Devin", "AI software engineer", "Autonomous coding", "SWE agent"]},
]

HISTORY_FILE = "company_history.json"


def _load_history() -> list[dict]:
    path = Path(HISTORY_FILE)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return []


def _save_history(history: list[dict]):
    Path(HISTORY_FILE).write_text(json.dumps(history, indent=2))


def pick_company() -> dict:
    """Pick a company that hasn't been covered recently."""
    history = _load_history()
    recent_slugs = {h["slug"] for h in history[-50:]}

    available = [c for c in COMPANIES if c["slug"] not in recent_slugs]
    if not available:
        available = COMPANIES.copy()
        log.info("All companies covered — resetting rotation")

    chosen = random.choice(available)

    history.append({
        "slug": chosen["slug"],
        "name": chosen["name"],
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
    })
    _save_history(history)

    log.info(f"Today's company: {chosen['name']} (topics: {', '.join(chosen['topics'][:4])})")
    return chosen


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-") or "topic"


def resolve_company(topic: str) -> dict:
    """Resolve a free-form topic to a company dict (known list or custom).

    Does not update company_history — manual topic runs stay outside daily rotation.
    """
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic is required")

    needle = topic.lower()
    slug_needle = _slugify(topic)

    for company in COMPANIES:
        if company["slug"] == slug_needle or company["name"].lower() == needle:
            log.info(f"Resolved topic to known company: {company['name']}")
            return dict(company)

    for company in COMPANIES:
        if needle in company["name"].lower() or slug_needle in company["slug"]:
            log.info(f"Resolved topic to known company: {company['name']}")
            return dict(company)

    custom = {
        "name": topic,
        "slug": slug_needle,
        "topics": [topic],
    }
    log.info(f"Using custom topic: {custom['name']} (slug={custom['slug']})")
    return custom


def get_history() -> list[dict]:
    return _load_history()
