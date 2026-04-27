from sqlalchemy import String, cast

from app.models import NewsStatus


def article_status_is_social_packaged(status_column):
    return cast(status_column, String) == NewsStatus.SOCIAL_PACKAGED.value
