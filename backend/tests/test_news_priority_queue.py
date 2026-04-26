from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.api.routes.news import _build_priority_queue_items
from app.models import NewsCategory, NewsStatus, UrgencyLevel


NOW = datetime(2026, 4, 26, 16, 0, 0)


def _article(
    *,
    article_id: int,
    status: NewsStatus,
    importance_score: int,
    hours_ago: float,
    is_breaking: bool = False,
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
    category: NewsCategory = NewsCategory.POLITICS,
) -> SimpleNamespace:
    created_at = NOW - timedelta(hours=hours_ago)
    return SimpleNamespace(
        id=article_id,
        title_ar=f"عنوان {article_id}",
        original_title=f"Original {article_id}",
        status=status,
        category=category,
        source_name="Test Source",
        created_at=created_at,
        published_at=None,
        crawled_at=created_at,
        updated_at=created_at,
        importance_score=importance_score,
        is_breaking=is_breaking,
        urgency=urgency,
    )


def test_priority_queue_endpoint_returns_ordered_items() -> None:
    article_one = _article(
        article_id=1,
        status=NewsStatus.CANDIDATE,
        importance_score=9,
        hours_ago=1,
        is_breaking=True,
        urgency=UrgencyLevel.HIGH,
    )
    article_two = _article(
        article_id=2,
        status=NewsStatus.APPROVED_HANDOFF,
        importance_score=6,
        hours_ago=2,
        urgency=UrgencyLevel.MEDIUM,
    )

    items = _build_priority_queue_items(
        [article_two, article_one],
        now=NOW,
        window_hours=24,
        competitor_map={1: {"count": 2, "max_priority": 8.0}},
        cluster_map={1: 4, 2: 1},
    )

    assert [item["article_id"] for item in items] == [1, 2]
    assert items[0]["priority_score"] > items[1]["priority_score"]


def test_priority_queue_excludes_archived() -> None:
    article = _article(
        article_id=3,
        status=NewsStatus.ARCHIVED,
        importance_score=10,
        hours_ago=0.5,
        is_breaking=True,
        urgency=UrgencyLevel.BREAKING,
    )

    items = _build_priority_queue_items([article], now=NOW, window_hours=24)

    assert items == []


def test_priority_queue_excludes_published_by_default() -> None:
    article = _article(
        article_id=4,
        status=NewsStatus.PUBLISHED,
        importance_score=8,
        hours_ago=1,
    )

    items = _build_priority_queue_items([article], now=NOW, window_hours=24, include_published=False)

    assert items == []


def test_priority_queue_include_published_true_allows_published() -> None:
    article = _article(
        article_id=5,
        status=NewsStatus.PUBLISHED,
        importance_score=8,
        hours_ago=1,
    )
    social_packaged = _article(
        article_id=6,
        status=NewsStatus.SOCIAL_PACKAGED,
        importance_score=7,
        hours_ago=2,
    )

    items = _build_priority_queue_items(
        [article, social_packaged],
        now=NOW,
        window_hours=24,
        include_published=True,
    )

    assert [item["article_id"] for item in items] == [5, 6]


def test_priority_queue_handles_empty_data() -> None:
    items = _build_priority_queue_items([], now=NOW, window_hours=24)
    assert items == []
