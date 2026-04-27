from app.api.routes.news import _parse_news_status_query
from app.models import NewsStatus


def test_parse_news_status_query_accepts_uppercase_name() -> None:
    assert _parse_news_status_query("NEW") == NewsStatus.NEW


def test_parse_news_status_query_accepts_lowercase_value() -> None:
    assert _parse_news_status_query("new") == NewsStatus.NEW


def test_parse_news_status_query_accepts_social_packaged_name_and_value() -> None:
    assert _parse_news_status_query("SOCIAL_PACKAGED") == NewsStatus.SOCIAL_PACKAGED
    assert _parse_news_status_query("social_packaged") == NewsStatus.SOCIAL_PACKAGED
