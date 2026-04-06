"""Daily ops monitoring scheduler."""

from __future__ import annotations

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.ops_monitor_service import ops_monitor_service

logger = get_logger("ops.scheduler")
settings = get_settings()

_scheduler: AsyncIOScheduler | None = None


def _run_daily_monitor_sync() -> None:
    asyncio.create_task(ops_monitor_service.run_daily_monitor())


def start_ops_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone=settings.ops_monitor_timezone)
    _scheduler.add_job(
        _run_daily_monitor_sync,
        trigger=CronTrigger(
            hour=settings.ops_monitor_daily_hour,
            minute=settings.ops_monitor_daily_minute,
            timezone=settings.ops_monitor_timezone,
        ),
        id="ops_daily_monitor",
        max_instances=1,
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "ops_monitor_scheduler_started",
        daily=f"{settings.ops_monitor_daily_hour:02d}:{settings.ops_monitor_daily_minute:02d}",
        timezone=settings.ops_monitor_timezone,
    )


def stop_ops_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
    logger.info("ops_monitor_scheduler_stopped")
