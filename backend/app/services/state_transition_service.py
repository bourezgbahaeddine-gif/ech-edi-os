from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.domain.news.state_machine import validate_transition
from app.models.news import Article, NewsStatus
from app.services.job_queue_service import job_queue_service


logger = get_logger("services.state_transition")
settings = get_settings()
SOCIAL_PACKAGE_JOB_TYPE = "social_package_generate"
SOCIAL_PACKAGE_DEFAULT_PLATFORMS = ["facebook", "x", "instagram", "tiktok", "push"]


async def _maybe_enqueue_social_package(*, db: AsyncSession, article: Article, previous_status: NewsStatus) -> None:
    if previous_status == NewsStatus.SOCIAL_PACKAGED:
        logger.info(
            "social_package_skipped_already_packaged",
            article_id=article.id,
            previous_status=previous_status.value,
        )
        return

    if not settings.social_package_enabled:
        logger.info(
            "social_package_skipped_feature_disabled",
            article_id=article.id,
            previous_status=previous_status.value,
        )
        return

    importance_score = int(getattr(article, "importance_score", 0) or 0)
    is_breaking = bool(getattr(article, "is_breaking", False))
    if importance_score < 6 and not is_breaking:
        logger.info(
            "social_package_skipped_low_importance",
            article_id=article.id,
            importance_score=importance_score,
            is_breaking=is_breaking,
        )
        return

    existing_job = await job_queue_service.find_active_job(
        db,
        job_type=SOCIAL_PACKAGE_JOB_TYPE,
        entity_id=str(article.id),
        max_age_minutes=60,
    )
    if existing_job is not None:
        logger.info(
            "social_package_skipped_existing_job",
            article_id=article.id,
            job_id=str(existing_job.id),
        )
        return

    job = None
    try:
        job = await job_queue_service.create_job(
            db,
            job_type=SOCIAL_PACKAGE_JOB_TYPE,
            queue_name="ai_quality",
            payload={
                "article_id": article.id,
                "platforms": list(SOCIAL_PACKAGE_DEFAULT_PLATFORMS),
            },
            entity_id=str(article.id),
            priority="high" if is_breaking else "normal",
        )
        await job_queue_service.enqueue_by_job_type(job_type=SOCIAL_PACKAGE_JOB_TYPE, job_id=str(job.id))
        logger.info(
            "social_package_enqueue_requested",
            article_id=article.id,
            job_id=str(job.id),
            importance_score=importance_score,
            is_breaking=is_breaking,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "social_package_enqueue_failed",
            article_id=article.id,
            error=str(exc),
        )
        if job is not None:
            await job_queue_service.mark_failed(db, job, f"enqueue_failed:{exc}")


class StateTransitionService:
    def assert_transition(self, *, current: NewsStatus, target: NewsStatus, entity: str = "article") -> None:
        result = validate_transition(current, target)
        if result.valid:
            return
        raise HTTPException(
            status_code=409,
            detail={
                "code": "invalid_state_transition",
                "entity": entity,
                "from_state": current.value,
                "to_state": target.value,
                "allowed_targets": [item.value for item in result.allowed_targets],
            },
        )

    async def transition_article(
        self,
        *,
        db: AsyncSession,
        article_id: int,
        target: NewsStatus,
        expected_current: NewsStatus | None = None,
        entity: str | None = None,
        lock_nowait: bool = True,
    ) -> tuple[Article, NewsStatus]:
        entity_name = entity or f"article:{article_id}"
        try:
            row = await db.execute(
                select(Article)
                .where(Article.id == article_id)
                .with_for_update(nowait=lock_nowait)
            )
        except OperationalError as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "transition_conflict",
                    "entity": entity_name,
                    "message": "The article is being updated by another operation. Retry.",
                },
            ) from exc

        article = row.scalar_one_or_none()
        if not article:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "article_not_found",
                    "entity": entity_name,
                },
            )

        current_status = article.status or NewsStatus.NEW
        if expected_current and current_status != expected_current:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "transition_conflict",
                    "entity": entity_name,
                    "message": "The article state changed before transition.",
                    "expected_current_state": expected_current.value,
                    "actual_current_state": current_status.value,
                    "target_state": target.value,
                },
            )

        self.assert_transition(current=current_status, target=target, entity=entity_name)
        article.status = target
        if target == NewsStatus.PUBLISHED:
            await _maybe_enqueue_social_package(db=db, article=article, previous_status=current_status)
        return article, current_status


state_transition_service = StateTransitionService()
