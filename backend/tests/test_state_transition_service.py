from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import app.services.state_transition_service as state_transition_module
from app.models.news import NewsStatus
from app.services.state_transition_service import state_transition_service


@dataclass
class _ArticleRow:
    id: int
    status: NewsStatus
    importance_score: int = 0
    is_breaking: bool = False


class _Result:
    def __init__(self, article):
        self._article = article

    def scalar_one_or_none(self):
        return self._article


class _DbSessionStub:
    def __init__(self, article):
        self._article = article

    async def execute(self, _stmt):
        return _Result(self._article)


@pytest.mark.asyncio
async def test_transition_article_updates_status_when_current_matches() -> None:
    article = _ArticleRow(id=77, status=NewsStatus.CANDIDATE)
    db = _DbSessionStub(article)

    locked_article, previous = await state_transition_service.transition_article(
        db=db,
        article_id=article.id,
        target=NewsStatus.APPROVED_HANDOFF,
        expected_current=NewsStatus.CANDIDATE,
    )

    assert previous == NewsStatus.CANDIDATE
    assert locked_article.status == NewsStatus.APPROVED_HANDOFF


@pytest.mark.asyncio
async def test_transition_article_returns_409_when_state_already_changed() -> None:
    article = _ArticleRow(id=78, status=NewsStatus.APPROVED)
    db = _DbSessionStub(article)

    with pytest.raises(HTTPException) as exc_info:
        await state_transition_service.transition_article(
            db=db,
            article_id=article.id,
            target=NewsStatus.APPROVED_HANDOFF,
            expected_current=NewsStatus.CANDIDATE,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["code"] == "transition_conflict"


@pytest.mark.asyncio
async def test_transition_article_does_not_enqueue_social_package_when_flag_disabled(monkeypatch) -> None:
    article = _ArticleRow(id=79, status=NewsStatus.READY_FOR_MANUAL_PUBLISH, importance_score=9)
    db = _DbSessionStub(article)
    enqueue_calls: list[str] = []

    monkeypatch.setattr(state_transition_module.settings, "social_package_enabled", False)

    async def _fake_find_active_job(*args, **kwargs):
        return None

    async def _fake_create_job(*args, **kwargs):
        enqueue_calls.append("create")
        return SimpleNamespace(id="job-1")

    monkeypatch.setattr(state_transition_module.job_queue_service, "find_active_job", _fake_find_active_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "create_job", _fake_create_job)

    locked_article, previous = await state_transition_service.transition_article(
        db=db,
        article_id=article.id,
        target=NewsStatus.PUBLISHED,
        expected_current=NewsStatus.READY_FOR_MANUAL_PUBLISH,
    )

    assert previous == NewsStatus.READY_FOR_MANUAL_PUBLISH
    assert locked_article.status == NewsStatus.PUBLISHED
    assert enqueue_calls == []


@pytest.mark.asyncio
async def test_transition_article_skips_social_package_for_low_importance(monkeypatch) -> None:
    article = _ArticleRow(id=80, status=NewsStatus.READY_FOR_MANUAL_PUBLISH, importance_score=4, is_breaking=False)
    db = _DbSessionStub(article)
    enqueue_calls: list[str] = []

    monkeypatch.setattr(state_transition_module.settings, "social_package_enabled", True)

    async def _fake_find_active_job(*args, **kwargs):
        return None

    async def _fake_create_job(*args, **kwargs):
        enqueue_calls.append("create")
        return SimpleNamespace(id="job-2")

    monkeypatch.setattr(state_transition_module.job_queue_service, "find_active_job", _fake_find_active_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "create_job", _fake_create_job)

    locked_article, _previous = await state_transition_service.transition_article(
        db=db,
        article_id=article.id,
        target=NewsStatus.PUBLISHED,
        expected_current=NewsStatus.READY_FOR_MANUAL_PUBLISH,
    )

    assert locked_article.status == NewsStatus.PUBLISHED
    assert enqueue_calls == []


@pytest.mark.asyncio
async def test_transition_article_enqueues_social_package_for_high_importance(monkeypatch) -> None:
    article = _ArticleRow(id=81, status=NewsStatus.READY_FOR_MANUAL_PUBLISH, importance_score=7, is_breaking=False)
    db = _DbSessionStub(article)
    calls: list[str] = []

    monkeypatch.setattr(state_transition_module.settings, "social_package_enabled", True)

    async def _fake_find_active_job(*args, **kwargs):
        calls.append("find")
        return None

    async def _fake_create_job(*args, **kwargs):
        calls.append("create")
        return SimpleNamespace(id="job-3")

    async def _fake_enqueue_by_job_type(*args, **kwargs):
        calls.append("enqueue")

    monkeypatch.setattr(state_transition_module.job_queue_service, "find_active_job", _fake_find_active_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "create_job", _fake_create_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "enqueue_by_job_type", _fake_enqueue_by_job_type)

    locked_article, _previous = await state_transition_service.transition_article(
        db=db,
        article_id=article.id,
        target=NewsStatus.PUBLISHED,
        expected_current=NewsStatus.READY_FOR_MANUAL_PUBLISH,
    )

    assert locked_article.status == NewsStatus.PUBLISHED
    assert calls == ["find", "create", "enqueue"]


@pytest.mark.asyncio
async def test_transition_article_does_not_fail_when_social_package_enqueue_fails(monkeypatch) -> None:
    article = _ArticleRow(id=82, status=NewsStatus.READY_FOR_MANUAL_PUBLISH, importance_score=8, is_breaking=False)
    db = _DbSessionStub(article)
    calls: list[str] = []
    fake_job = SimpleNamespace(id="job-4")

    monkeypatch.setattr(state_transition_module.settings, "social_package_enabled", True)

    async def _fake_find_active_job(*args, **kwargs):
        calls.append("find")
        return None

    async def _fake_create_job(*args, **kwargs):
        calls.append("create")
        return fake_job

    async def _fake_enqueue_by_job_type(*args, **kwargs):
        calls.append("enqueue")
        raise RuntimeError("queue down")

    async def _fake_mark_failed(*args, **kwargs):
        calls.append("mark_failed")

    monkeypatch.setattr(state_transition_module.job_queue_service, "find_active_job", _fake_find_active_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "create_job", _fake_create_job)
    monkeypatch.setattr(state_transition_module.job_queue_service, "enqueue_by_job_type", _fake_enqueue_by_job_type)
    monkeypatch.setattr(state_transition_module.job_queue_service, "mark_failed", _fake_mark_failed)

    locked_article, previous = await state_transition_service.transition_article(
        db=db,
        article_id=article.id,
        target=NewsStatus.PUBLISHED,
        expected_current=NewsStatus.READY_FOR_MANUAL_PUBLISH,
    )

    assert previous == NewsStatus.READY_FOR_MANUAL_PUBLISH
    assert locked_article.status == NewsStatus.PUBLISHED
    assert calls == ["find", "create", "enqueue", "mark_failed"]
