from app.schemas import ArticleBrief, ArticleResponse


def test_article_brief_display_title_falls_back_to_original_title() -> None:
    article = ArticleBrief.model_validate(
        {
            "id": 1,
            "title_ar": None,
            "original_title": "Original incoming title",
            "original_url": "https://example.com/story",
            "source_name": "APS",
            "category": "local_algeria",
            "importance_score": 5,
            "urgency": "medium",
            "is_breaking": False,
            "status": "new",
            "crawled_at": "2026-04-26T10:00:00",
            "created_at": "2026-04-26T10:00:00",
            "summary": None,
        }
    )

    assert article.display_title == "Original incoming title"
    assert article.title == "Original incoming title"


def test_article_response_display_title_falls_back_to_original_url_then_default() -> None:
    article = ArticleResponse.model_validate(
        {
            "id": 2,
            "unique_hash": "abc123",
            "title_ar": "",
            "original_title": "",
            "original_url": "https://example.com/fallback-only",
            "published_at": None,
            "crawled_at": "2026-04-26T11:00:00",
            "source_name": None,
            "summary": None,
            "body_html": None,
            "category": None,
            "importance_score": 3,
            "urgency": None,
            "is_breaking": False,
            "sentiment": None,
            "truth_score": None,
            "entities": [],
            "keywords": [],
            "seo_title": None,
            "seo_description": None,
            "status": "new",
            "reviewed_by": None,
            "reviewed_at": None,
            "published_url": None,
            "processing_time_ms": None,
            "ai_model_used": None,
            "trace_id": None,
            "created_at": "2026-04-26T11:00:00",
            "updated_at": "2026-04-26T11:00:00",
        }
    )

    assert article.display_title == "https://example.com/fallback-only"
    assert article.title == "https://example.com/fallback-only"
