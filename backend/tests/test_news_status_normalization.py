from sqlalchemy.dialects import postgresql

from app.api.routes import editorial as editorial_route
from app.api.routes.news import _article_status_in, _parse_news_status_query
from app.models import NewsStatus
from app.services.time_integrity_service import TimeIntegrityService


def test_parse_news_status_query_accepts_uppercase_name() -> None:
    assert _parse_news_status_query("NEW") == NewsStatus.NEW


def test_parse_news_status_query_accepts_lowercase_value() -> None:
    assert _parse_news_status_query("new") == NewsStatus.NEW


def test_parse_news_status_query_accepts_social_packaged_name_and_value() -> None:
    assert _parse_news_status_query("SOCIAL_PACKAGED") == NewsStatus.SOCIAL_PACKAGED
    assert _parse_news_status_query("social_packaged") == NewsStatus.SOCIAL_PACKAGED


def test_social_packaged_filter_uses_casted_value_not_enum_name() -> None:
    expression = _article_status_in([NewsStatus.PUBLISHED, NewsStatus.SOCIAL_PACKAGED.value])
    compiled = str(expression.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

    assert "social_packaged" in compiled
    assert "SOCIAL_PACKAGED" not in compiled
    assert "CAST" in compiled.upper()


def test_editorial_social_filter_uses_casted_value_not_enum_name() -> None:
    compiled = str(
        editorial_route._article_status_is_social_packaged().compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "social_packaged" in compiled
    assert "SOCIAL_PACKAGED" not in compiled
    assert "CAST" in compiled.upper()


def test_time_integrity_non_published_statuses_exclude_social_packaged() -> None:
    assert NewsStatus.SOCIAL_PACKAGED not in TimeIntegrityService._NON_PUBLISHED_STATUSES
    assert NewsStatus.PUBLISHED not in TimeIntegrityService._NON_PUBLISHED_STATUSES
    assert NewsStatus.ARCHIVED not in TimeIntegrityService._NON_PUBLISHED_STATUSES
