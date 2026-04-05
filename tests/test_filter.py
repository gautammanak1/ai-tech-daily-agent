"""Tests for filter service."""

from services.filter_service import classify_item, extract_trends


def test_classify_ai_item():
    item = {"title": "OpenAI releases GPT-5", "description": "New large language model", "source": "Test", "source_weight": 3, "category": "ai"}
    result = classify_item(item)
    assert result["category"] == "ai"
    assert result["relevance"] > 0


def test_classify_agent_item():
    item = {"title": "New AI agent framework launched", "description": "Autonomous agent orchestration", "source": "Test", "source_weight": 2, "category": "tech"}
    result = classify_item(item)
    assert result["category"] == "agents"


def test_extract_trends():
    items = [
        {"title": "OpenAI GPT model", "description": "AI deep learning model"},
        {"title": "GPT-5 is coming", "description": "Large language model update"},
    ]
    trends = extract_trends(items, top_n=3)
    assert len(trends) > 0
    assert trends[0]["count"] > 0
