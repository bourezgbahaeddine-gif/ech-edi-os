"""
Operational monitoring service.
Collects daily snapshots for DB, vector store, queues, and key app sections.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, init_db
from app.core.logging import get_logger
from app.models import (
    Article,
    ArticleVector,
    PipelineRun,
    SocialTask,
    SocialPost,
    ScriptProject,
    DocumentIntelDocument,
)
from app.services.cache_service import cache_service
from app.services.job_queue_service import job_queue_service
from app.services.notification_service import notification_service

logger = get_logger("ops.monitor")


class OpsMonitorService:
    async def collect_snapshot(self, db: AsyncSession) -> dict[str, Any]:
        """Collect a monitoring snapshot for system health."""
        now = datetime.utcnow()

        ping_start = time.perf_counter()
        await db.execute(select(1))
        db_latency_ms = round((time.perf_counter() - ping_start) * 1000, 2)
        size_row = await db.execute(text("select pg_database_size(current_database())"))
        db_size_bytes = int(size_row.scalar() or 0)

        articles_count = int((await db.execute(select(func.count(Article.id)))).scalar() or 0)
        articles_last = (await db.execute(select(func.max(Article.updated_at)))).scalar()

        vectors_count = int((await db.execute(select(func.count(ArticleVector.id)))).scalar() or 0)
        vectors_last = (await db.execute(select(func.max(ArticleVector.updated_at)))).scalar()
        vectors_distinct_articles = int(
            (await db.execute(select(func.count(func.distinct(ArticleVector.article_id))))).scalar() or 0
        )
        vectors_by_type_rows = await db.execute(
            select(ArticleVector.vector_type, func.count(ArticleVector.id)).group_by(ArticleVector.vector_type)
        )
        vectors_by_type = {vector_type: int(count or 0) for vector_type, count in vectors_by_type_rows.all()}

        posts_count = int((await db.execute(select(func.count(SocialPost.id)))).scalar() or 0)
        posts_last = (await db.execute(select(func.max(SocialPost.updated_at)))).scalar()
        tasks_count = int((await db.execute(select(func.count(SocialTask.id)))).scalar() or 0)
        tasks_last = (await db.execute(select(func.max(SocialTask.updated_at)))).scalar()

        scripts_count = int((await db.execute(select(func.count(ScriptProject.id)))).scalar() or 0)
        scripts_last = (await db.execute(select(func.max(ScriptProject.updated_at)))).scalar()

        docs_count = int((await db.execute(select(func.count(DocumentIntelDocument.id)))).scalar() or 0)
        docs_last = (await db.execute(select(func.max(DocumentIntelDocument.updated_at)))).scalar()

        pipeline_rows = await db.execute(
            select(PipelineRun.run_type, func.max(PipelineRun.finished_at)).group_by(PipelineRun.run_type)
        )
        pipeline_last = {run_type: last.isoformat() if last else None for run_type, last in pipeline_rows.all()}

        queue_depth = await job_queue_service.queue_depths()
        total_queue_depth = sum(int(v or 0) for v in queue_depth.values()) if isinstance(queue_depth, dict) else 0

        def _age_minutes(ts: datetime | None) -> float | None:
            if not ts:
                return None
            return round((now - ts).total_seconds() / 60.0, 2)

        sections = [
            {
                "key": "news",
                "label": "الأخبار",
                "count": articles_count,
                "last_update": articles_last.isoformat() if articles_last else None,
                "age_minutes": _age_minutes(articles_last),
            },
            {
                "key": "digital_tasks",
                "label": "مهام التغطية الرقمية",
                "count": tasks_count,
                "last_update": tasks_last.isoformat() if tasks_last else None,
                "age_minutes": _age_minutes(tasks_last),
            },
            {
                "key": "digital_posts",
                "label": "منشورات التغطية الرقمية",
                "count": posts_count,
                "last_update": posts_last.isoformat() if posts_last else None,
                "age_minutes": _age_minutes(posts_last),
            },
            {
                "key": "scripts",
                "label": "سكريبتات الفيديو",
                "count": scripts_count,
                "last_update": scripts_last.isoformat() if scripts_last else None,
                "age_minutes": _age_minutes(scripts_last),
            },
            {
                "key": "document_intel",
                "label": "تحليل الوثائق",
                "count": docs_count,
                "last_update": docs_last.isoformat() if docs_last else None,
                "age_minutes": _age_minutes(docs_last),
            },
        ]

        vector_coverage = round((vectors_distinct_articles / articles_count) * 100.0, 2) if articles_count else 0.0

        return {
            "generated_at": now.isoformat(),
            "database": {
                "status": "connected",
                "latency_ms": db_latency_ms,
                "size_bytes": db_size_bytes,
                "articles_count": articles_count,
                "articles_last_update": articles_last.isoformat() if articles_last else None,
            },
            "vector": {
                "vectors_count": vectors_count,
                "vectors_last_update": vectors_last.isoformat() if vectors_last else None,
                "distinct_articles": vectors_distinct_articles,
                "coverage_percent": vector_coverage,
                "by_type": vectors_by_type,
            },
            "redis": {
                "connected": bool(cache_service.connected),
            },
            "queues": {
                "depths": queue_depth,
                "total_depth": total_queue_depth,
            },
            "pipeline": {
                "last_runs": pipeline_last,
            },
            "sections": sections,
        }

    async def run_daily_monitor(self) -> dict[str, Any]:
        """Run daily monitoring and persist snapshot for later review."""
        await init_db()
        async with async_session() as session:
            snapshot = await self.collect_snapshot(session)

        await cache_service.set_json("ops:daily_monitor:last", snapshot, ttl=timedelta(days=7))

        try:
            db = snapshot.get("database", {})
            vector = snapshot.get("vector", {})
            queues = snapshot.get("queues", {})
            message = (
                "📊 تقرير المراقبة اليومي\n"
                f"- قاعدة البيانات: {db.get('articles_count', 0)} خبر | "
                f"{round((db.get('size_bytes', 0) / (1024**3)), 2)} GB\n"
                f"- المتجهات: {vector.get('vectors_count', 0)} | تغطية {vector.get('coverage_percent', 0)}%\n"
                f"- الطوابير: {queues.get('total_depth', 0)} مهمة معلقة\n"
            )
            await notification_service.send_slack(message)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ops_daily_monitor_notify_failed", error=str(exc))

        logger.info("ops_daily_monitor_completed", snapshot=snapshot)
        return snapshot


ops_monitor_service = OpsMonitorService()
