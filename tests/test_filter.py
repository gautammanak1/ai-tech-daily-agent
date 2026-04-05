"""Tests for company picker."""

from services.company_picker import COMPANIES


def test_companies_have_required_fields():
    for c in COMPANIES:
        assert "name" in c
        assert "slug" in c
        assert "topics" in c
        assert len(c["topics"]) >= 3


def test_unique_slugs():
    slugs = [c["slug"] for c in COMPANIES]
    assert len(slugs) == len(set(slugs))
