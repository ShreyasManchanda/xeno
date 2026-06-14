import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from services.trend_utils import (
    normalize_trend_highlight,
    normalize_trend_highlights,
    normalize_variant_targets,
    tavily_result_to_snippet,
)


def test_normalize_trend_highlight_strips_markdown():
    raw = (
        "Indian Fashion Trends 2026: Indo-Western kurta sets and linen co-ords "
        "are rising across major Indian metros this season."
    )
    cleaned = normalize_trend_highlight(raw)
    assert cleaned
    assert "#" not in cleaned
    assert "**" not in cleaned
    assert "*" not in cleaned
    assert cleaned[0].isupper()


def test_normalize_trend_highlights_never_empty():
    messy = [
        "Samyakk: Sarees | Sherwani | Salwar Suits | Kurti | Lehenga | Gowns | Mens Wear. * Gown / Indian Ethnic Wear",
        "Latest Fashion Trends 2026: The Hottest Indian Fashion Picks for Women). *Latest fashion trends 2026 centre around Indo-Western",
    ]
    highlights = normalize_trend_highlights(messy, season="summer", limit=3)
    assert len(highlights) == 3
    for item in highlights:
        assert "#" not in item
        assert "**" not in item
        assert len(item) <= 141


def test_tavily_result_to_snippet():
    snippet = tavily_result_to_snippet(
        {
            "title": "Summer Kurta Trends 2026",
            "content": "Light linen kurtas and pastel co-ords are everywhere this season.",
        }
    )
    assert "Summer Kurta Trends" in snippet
    assert "linen" in snippet.lower()


def test_normalize_variant_targets_maps_invalid_age_group():
    variants = [
        {"id": "B", "targets": {"age_group": "26-42"}, "message": "Hi {name}"},
    ]
    fixed = normalize_variant_targets(variants)
    assert fixed[0]["targets"]["age_group"] == "26-35"
