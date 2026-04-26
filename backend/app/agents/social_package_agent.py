from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.news import Article
from app.services.smart_editor_service import smart_editor_service

logger = get_logger("agents.social_package")
settings = get_settings()

DEFAULT_SOCIAL_PLATFORMS = (
    "facebook",
    "x",
    "instagram",
    "tiktok",
    "push",
    "summary_120",
    "breaking_alert",
)


class SocialPackageAgent:
    async def generate_social_package(
        self,
        db: AsyncSession,
        article_id: int,
        platforms: list[str] | None = None,
    ) -> dict:
        if not settings.social_package_enabled:
            return {
                "enabled": False,
                "article_id": article_id,
                "platforms": list(platforms or DEFAULT_SOCIAL_PLATFORMS),
                "variants": {},
            }

        row = await db.execute(select(Article).where(Article.id == article_id))
        article = row.scalar_one_or_none()
        if not article:
            raise RuntimeError("article_not_found")

        source_text = "\n".join(
            [
                article.original_title or "",
                article.summary or "",
                article.original_content or "",
            ]
        ).strip()
        variants = await smart_editor_service.social_variants(
            source_text=source_text,
            draft_title=article.title_ar or article.original_title or f"Article #{article.id}",
            draft_html=article.body_html or article.original_content or "",
        )
        requested = [item.strip().lower() for item in (platforms or DEFAULT_SOCIAL_PLATFORMS) if item and item.strip()]
        filtered = {key: variants.get(key, "") for key in requested}
        logger.info(
            "social_package_generated",
            article_id=article_id,
            requested_platforms=requested,
            generated_keys=sorted(filtered.keys()),
        )
        return {
            "enabled": True,
            "article_id": article_id,
            "platforms": requested,
            "variants": filtered,
        }


social_package_agent = SocialPackageAgent()
