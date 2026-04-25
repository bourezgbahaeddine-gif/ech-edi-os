"""Media Intelligence Layer API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.rbac import require_roles
from app.api.envelope import error_envelope, success_envelope
from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.mil import MILActionResponse, MILAnalyzeRecentRequest, MILDismissRequest, MILSnoozeRequest
from app.services.job_queue_service import job_queue_service
from app.services.mil_service import mil_service

READ_ALLOWED = (
    UserRole.director,
    UserRole.editor_chief,
    UserRole.journalist,
    UserRole.social_media,
    UserRole.print_editor,
)
MANAGE_ALLOWED = (
    UserRole.director,
    UserRole.editor_chief,
)

router = APIRouter(
    prefix="/mil",
    tags=["Media Intelligence Layer"],
    dependencies=[Depends(require_roles(*READ_ALLOWED))],
)


@router.post("/analyze/recent")
async def analyze_recent(
    payload: MILAnalyzeRecentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active_job = await job_queue_service.find_active_job(
        db,
        job_type="mil_analyze_recent",
        entity_id="mil_recent",
        max_age_minutes=max(15, payload.hours * 3),
    )
    if active_job:
        return success_envelope(
            {
                "job_id": str(active_job.id),
                "status": active_job.status,
                "job_type": active_job.job_type,
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    job = await job_queue_service.create_job(
        db,
        job_type="mil_analyze_recent",
        queue_name="ai_quality",
        payload=payload.model_dump(),
        entity_id="mil_recent",
        actor_user_id=current_user.id,
        actor_username=current_user.username,
        max_attempts=3,
    )
    await job_queue_service.enqueue_by_job_type(job_type="mil_analyze_recent", job_id=str(job.id))
    return success_envelope(
        {"job_id": str(job.id), "status": job.status, "job_type": job.job_type},
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.get("/signals")
async def list_signals(
    triage_action: str | None = Query(default=None, pattern="^(suggest|flag|escalate)$"),
    status_filter: str = Query(default="active", alias="status", pattern="^(active|dismissed|consumed|archived)$"),
    limit: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await mil_service.list_signals(
        db,
        triage_action=triage_action,
        status=status_filter,
        limit=limit,
    )
    return success_envelope([item.model_dump(mode="json") for item in items])


@router.get("/signals/{signal_id}")
async def get_signal_detail(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    signal = await mil_service.get_signal_detail(db, signal_id)
    if not signal:
        return error_envelope(code="mil_signal_not_found", message="إشارة MIL غير موجودة.", status_code=404)
    return success_envelope(signal.model_dump(mode="json"))


@router.post("/signals/{signal_id}/dismiss")
async def dismiss_signal(
    signal_id: int,
    payload: MILDismissRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in MANAGE_ALLOWED:
        return error_envelope(code="forbidden", message="إخفاء إشارات MIL متاح لرئيس التحرير والمدير فقط.", status_code=403)
    signal = await mil_service.dismiss_signal(
        db,
        signal_id=signal_id,
        dismissed_by=current_user.id,
        note=payload.note,
    )
    if not signal:
        return error_envelope(code="mil_signal_not_found", message="إشارة MIL غير موجودة.", status_code=404)
    return success_envelope({"signal_id": signal.id, "status": signal.status, "dismissed_at": signal.dismissed_at})


@router.get("/today/escalations")
async def today_escalations(
    limit: int = Query(default=4, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await mil_service.list_today_escalations(db, limit=limit)
    return success_envelope([item.model_dump(mode="json") for item in items])


@router.get("/today/full")
async def today_full(
    limit_per_section: int = Query(default=4, ge=1, le=8),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await mil_service.get_today_full(db, limit_per_section=limit_per_section)
    return success_envelope(data.model_dump(mode="json"))


@router.get("/dashboard")
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await mil_service.get_dashboard(db)
    return success_envelope(data.model_dump(mode="json"))


@router.get("/entities")
async def entities(
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await mil_service.list_entities(db, limit=limit)
    return success_envelope([item.model_dump(mode="json") for item in items])


@router.get("/clusters")
async def clusters(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await mil_service.list_clusters(db, limit=limit)
    return success_envelope([item.model_dump(mode="json") for item in items])


@router.get("/stories/{story_id}/insights")
async def story_insights(
    story_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await mil_service.get_story_insights(db, story_id=story_id)
    if not data:
        return error_envelope(code="mil_story_not_found", message="القصة غير موجودة.", status_code=404)
    return success_envelope(data.model_dump(mode="json"))


@router.get("/events/{event_id}/insights")
async def event_insights(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await mil_service.get_event_insights(db, event_id=event_id)
    if not data:
        return error_envelope(code="mil_event_not_found", message="الحدث غير موجود.", status_code=404)
    return success_envelope(data.model_dump(mode="json"))


@router.get("/editor/context")
async def editor_context(
    draft_id: int | None = Query(default=None),
    work_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await mil_service.get_editor_context(db, draft_id=draft_id, work_id=work_id)
    if not data:
        return error_envelope(code="mil_editor_context_not_found", message="تعذر إيجاد المسودة المطلوبة.", status_code=404)
    return success_envelope(data.model_dump(mode="json"))


@router.post("/signals/{signal_id}/useful")
async def mark_signal_useful(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    signal = await mil_service.mark_signal_useful(db, signal_id=signal_id, actor_user_id=current_user.id)
    if not signal:
        return error_envelope(code="mil_signal_not_found", message="إشارة MIL غير موجودة.", status_code=404)
    payload = MILActionResponse(
        signal_id=signal.id,
        status=signal.status,
        useful_count=int(signal.useful_count or 0),
        snoozed_until=signal.snoozed_until,
    )
    return success_envelope(payload.model_dump(mode="json"))


@router.post("/signals/{signal_id}/snooze")
async def snooze_signal(
    signal_id: int,
    payload: MILSnoozeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    signal = await mil_service.snooze_signal(db, signal_id=signal_id, hours=payload.hours)
    if not signal:
        return error_envelope(code="mil_signal_not_found", message="إشارة MIL غير موجودة.", status_code=404)
    body = MILActionResponse(
        signal_id=signal.id,
        status=signal.status,
        useful_count=int(signal.useful_count or 0),
        snoozed_until=signal.snoozed_until,
    )
    return success_envelope(body.model_dump(mode="json"))
