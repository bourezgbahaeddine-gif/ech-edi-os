from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import editorial as editorial_route
from app.models.news import NewsStatus
from app.models.user import UserRole


class _Result:
    def __init__(self, scalar):
        self._scalar = scalar

    def scalar_one_or_none(self):
        return self._scalar


class _DbStub:
    def __init__(self, article):
        self._article = article
        self.added = []
        self.committed = False

    async def execute(self, _stmt):
        return _Result(self._article)

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True


def _journalist():
    return SimpleNamespace(
        id=7,
        username="journo",
        full_name_ar="Journo",
        role=UserRole.journalist,
    )


def _chief():
    return SimpleNamespace(
        id=9,
        username="chief",
        full_name_ar="Chief",
        role=UserRole.editor_chief,
    )


def _article(status: NewsStatus):
    return SimpleNamespace(
        id=101,
        status=status,
        title_ar="Title",
        original_title="Original",
        body_html="<p>Body</p>",
        reviewed_by=None,
        reviewed_at=None,
        rejection_reason=None,
        published_at=None,
        published_url=None,
    )


def _draft():
    return SimpleNamespace(
        id=11,
        article_id=101,
        work_id="WRK-1",
        status="draft",
    )


@pytest.mark.asyncio
async def test_make_decision_approve_uses_shared_handoff_gate(monkeypatch):
    article = _article(NewsStatus.CANDIDATE)
    db = _DbStub(article)
    seen: list[str] = []

    async def _fake_gate(db_arg, article_arg, user_arg, *, source):
        assert db_arg is db
        assert article_arg is article
        assert user_arg.role == UserRole.editor_chief
        seen.append(source)

    async def _fake_transition(*, article, target_status, **_kwargs):
        article.status = target_status

    async def _noop_keywords(*_args, **_kwargs):
        return None

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _fake_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _fake_transition)
    monkeypatch.setattr(editorial_route, "bump_keyword_interactions", _noop_keywords)
    monkeypatch.setattr(editorial_route, "extract_keywords", lambda _text: [])

    payload = SimpleNamespace(
        decision="approve",
        reason="ok",
        edited_title=None,
        edited_body=None,
    )

    await editorial_route.make_decision(
        article_id=101,
        data=payload,
        db=db,
        current_user=_chief(),
    )

    assert seen == ["editorial_decision_approve"]
    assert article.status == NewsStatus.APPROVED_HANDOFF
    assert db.committed is True


@pytest.mark.asyncio
async def test_make_decision_approve_returns_gate_blockers(monkeypatch):
    article = _article(NewsStatus.CANDIDATE)
    db = _DbStub(article)

    async def _deny_gate(*_args, **_kwargs):
        raise HTTPException(
            status_code=412,
            detail={
                "code": "quality_gate_blocked",
                "message": "blocked",
                "blockers": ["fact blocker"],
            },
        )

    async def _should_not_run(*_args, **_kwargs):
        raise AssertionError("transition should not run when approve gate fails")

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _deny_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _should_not_run)

    payload = SimpleNamespace(
        decision="approve",
        reason="ok",
        edited_title=None,
        edited_body=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        await editorial_route.make_decision(
            article_id=101,
            data=payload,
            db=db,
            current_user=_chief(),
        )

    assert exc_info.value.status_code == 412
    assert exc_info.value.detail["code"] == "quality_gate_blocked"
    assert exc_info.value.detail["blockers"] == ["fact blocker"]
    assert article.status == NewsStatus.CANDIDATE


@pytest.mark.asyncio
async def test_handoff_blocks_candidate_until_shared_gate_passes(monkeypatch):
    article = _article(NewsStatus.CANDIDATE)
    db = _DbStub(article)

    async def _deny_gate(*_args, **_kwargs):
        raise HTTPException(
            status_code=412,
            detail={"message": "gate_failed", "blocking_reasons": ["policy blocker"]},
        )

    async def _should_not_run(*_args, **_kwargs):
        raise AssertionError("transition/scribe should not run when gate blocks handoff")

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _deny_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _should_not_run)
    monkeypatch.setattr(editorial_route.scribe_agent, "write_article", _should_not_run)

    with pytest.raises(HTTPException) as exc_info:
        await editorial_route.handoff_to_scribe(
            article_id=101,
            db=db,
            current_user=_journalist(),
        )

    assert exc_info.value.status_code == 412
    assert exc_info.value.detail["code"] == "quality_gate_blocked"
    assert exc_info.value.detail["blockers"] == ["policy blocker"]
    assert exc_info.value.detail["blocking_reasons"] == ["policy blocker"]


@pytest.mark.asyncio
async def test_handoff_candidate_with_passing_gates_proceeds(monkeypatch):
    article = _article(NewsStatus.CANDIDATE)
    db = _DbStub(article)
    transitions: list[NewsStatus] = []

    async def _allow_gate(*_args, **_kwargs):
        return None

    async def _fake_transition(*, article, target_status, **_kwargs):
        transitions.append(target_status)
        article.status = target_status

    async def _fake_write(*_args, **_kwargs):
        return {"work_id": "WRK-1", "draft_id": 88, "version": 1}

    async def _noop_keywords(*_args, **_kwargs):
        return None

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _allow_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _fake_transition)
    monkeypatch.setattr(editorial_route.scribe_agent, "write_article", _fake_write)
    monkeypatch.setattr(editorial_route, "bump_keyword_interactions", _noop_keywords)
    monkeypatch.setattr(editorial_route, "extract_keywords", lambda _text: [])

    response = await editorial_route.handoff_to_scribe(
        article_id=101,
        db=db,
        current_user=_journalist(),
    )

    assert transitions == [NewsStatus.APPROVED_HANDOFF]
    assert response["draft_id"] == 88


@pytest.mark.asyncio
async def test_handoff_approved_handoff_keeps_existing_behavior(monkeypatch):
    article = _article(NewsStatus.APPROVED_HANDOFF)
    db = _DbStub(article)

    async def _should_not_run(*_args, **_kwargs):
        raise AssertionError("shared gate should not run for already approved handoff")

    async def _fake_write(*_args, **_kwargs):
        return {"work_id": "WRK-1", "draft_id": 91, "version": 3}

    async def _noop_keywords(*_args, **_kwargs):
        return None

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _should_not_run)
    monkeypatch.setattr(editorial_route.scribe_agent, "write_article", _fake_write)
    monkeypatch.setattr(editorial_route, "bump_keyword_interactions", _noop_keywords)
    monkeypatch.setattr(editorial_route, "extract_keywords", lambda _text: [])

    response = await editorial_route.handoff_to_scribe(
        article_id=101,
        db=db,
        current_user=_journalist(),
    )

    assert response["draft_id"] == 91
    assert article.status == NewsStatus.APPROVED_HANDOFF


@pytest.mark.asyncio
async def test_handoff_rejected_reopen_is_blocked_without_passing_gates(monkeypatch):
    article = _article(NewsStatus.REJECTED)
    db = _DbStub(article)

    async def _deny_gate(*_args, **_kwargs):
        raise HTTPException(
            status_code=412,
            detail={
                "code": "quality_gate_blocked",
                "message": "blocked",
                "blockers": ["reopen blocker"],
            },
        )

    async def _should_not_run(*_args, **_kwargs):
        raise AssertionError("transition/scribe should not run when reopen gate fails")

    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _deny_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _should_not_run)
    monkeypatch.setattr(editorial_route.scribe_agent, "write_article", _should_not_run)

    with pytest.raises(HTTPException) as exc_info:
        await editorial_route.handoff_to_scribe(
            article_id=101,
            db=db,
            current_user=_journalist(),
        )

    assert exc_info.value.status_code == 412
    assert exc_info.value.detail["blockers"] == ["reopen blocker"]
    assert article.status == NewsStatus.REJECTED


@pytest.mark.asyncio
async def test_regenerate_from_candidate_uses_shared_handoff_gate(monkeypatch):
    article = _article(NewsStatus.CANDIDATE)
    db = _DbStub(article)
    draft = _draft()
    seen: list[str] = []

    async def _fake_get_latest(*_args, **_kwargs):
        return draft

    async def _fake_gate(db_arg, article_arg, user_arg, *, source):
        assert db_arg is db
        assert article_arg is article
        assert user_arg.role == UserRole.journalist
        seen.append(source)

    async def _fake_transition(*, article, target_status, **_kwargs):
        article.status = target_status

    async def _fake_write(*_args, **_kwargs):
        return {"draft_id": 55, "version": 2}

    monkeypatch.setattr(editorial_route, "_get_latest_draft_or_404", _fake_get_latest)
    monkeypatch.setattr(editorial_route, "assert_article_can_enter_approved_handoff", _fake_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _fake_transition)
    monkeypatch.setattr(editorial_route.scribe_agent, "write_article", _fake_write)

    response = await editorial_route.regenerate_draft_by_work_id(
        work_id="WRK-1",
        db=db,
        current_user=_journalist(),
    )

    assert seen == ["regenerate_draft"]
    assert response["regenerated"] is True
    assert article.status == NewsStatus.APPROVED_HANDOFF


@pytest.mark.asyncio
async def test_publish_now_requires_ready_for_manual_publish(monkeypatch):
    article = _article(NewsStatus.DRAFT_GENERATED)
    db = _DbStub(article)
    payload = editorial_route.ArticleProcessRequest(action="publish_now")

    with pytest.raises(HTTPException) as exc_info:
        await editorial_route.process_article(
            article_id=101,
            payload=payload,
            db=db,
            current_user=_journalist(),
        )

    assert exc_info.value.status_code == 409
    assert "ready_for_manual_publish" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_self_approve_submits_for_chief_instead_of_direct_publish(monkeypatch):
    db = _DbStub(None)
    draft = _draft()
    calls: list[dict] = []

    async def _fake_get_latest(*_args, **_kwargs):
        return draft

    async def _fake_submit(**kwargs):
        calls.append(kwargs)
        return {
            "article_id": 101,
            "status": NewsStatus.READY_FOR_CHIEF_APPROVAL.value,
            "submitted_for_chief_approval": True,
        }

    monkeypatch.setattr(editorial_route, "_get_latest_draft_or_404", _fake_get_latest)
    monkeypatch.setattr(editorial_route, "_submit_draft_for_chief_approval", _fake_submit)

    response = await editorial_route.self_approve_workspace_draft(
        work_id="WRK-1",
        db=db,
        current_user=_journalist(),
    )

    assert "force_direct_publish" not in calls[0]
    assert response["submitted_for_chief_approval"] is True
    assert "رئيس التحرير" in response["message"]


@pytest.mark.asyncio
async def test_self_approve_disabled_by_default(monkeypatch):
    db = _DbStub(None)

    monkeypatch.setattr(editorial_route.settings, "editorial_direct_publish_enabled", False)

    with pytest.raises(HTTPException) as exc_info:
        await editorial_route.self_approve_workspace_draft(
            work_id="WRK-1",
            db=db,
            current_user=_journalist(),
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_chief_approve_still_reaches_ready_for_manual_publish(monkeypatch):
    article = _article(NewsStatus.READY_FOR_CHIEF_APPROVAL)
    db = _DbStub(article)
    payload = editorial_route.ChiefFinalDecisionRequest(decision="approve", notes=None)

    async def _noop_gate(*_args, **_kwargs):
        return None

    async def _fake_transition(*, article, target_status, **_kwargs):
        article.status = target_status

    monkeypatch.setattr(editorial_route, "_assert_publish_gate_and_constitution", _noop_gate)
    monkeypatch.setattr(editorial_route, "_transition_article_status", _fake_transition)

    response = await editorial_route.chief_final_decision(
        article_id=101,
        payload=payload,
        db=db,
        current_user=_chief(),
    )

    assert response["status"] == NewsStatus.READY_FOR_MANUAL_PUBLISH.value
