import pytest
from fastapi import HTTPException

from app.api.routes import auth as auth_routes
from app.api.routes.editorial import assert_draft_access
from app.api.routes.memory import _assert_item_write_access
from app.api.routes.simulator import _assert_run_access
from app.models.news import EditorialDraft
from app.models.project_memory import ProjectMemoryItem
from app.models.user import User, UserRole


def _user(
    *,
    user_id: int,
    username: str,
    role: UserRole,
    full_name_ar: str | None = None,
) -> User:
    return User(
        id=user_id,
        username=username,
        full_name_ar=full_name_ar or username,
        role=role,
        hashed_password="x",
        departments=[],
        is_active=True,
    )


def _draft(*, created_by: str, status: str = "draft") -> EditorialDraft:
    return EditorialDraft(
        id=1,
        article_id=10,
        work_id="WRK-SECURITY",
        source_action="manual",
        body="body",
        status=status,
        version=1,
        created_by=created_by,
    )


class _SimRun:
    def __init__(self, *, created_by_user_id: int | None, created_by_username: str | None):
        self.created_by_user_id = created_by_user_id
        self.created_by_username = created_by_username


def test_journalist_can_access_own_draft() -> None:
    journalist = _user(user_id=1, username="journalist_a", role=UserRole.journalist)
    draft = _draft(created_by="journalist_a")

    assert_draft_access(draft, journalist, action="write")


def test_journalist_cannot_access_other_users_draft() -> None:
    journalist = _user(user_id=1, username="journalist_a", role=UserRole.journalist)
    draft = _draft(created_by="journalist_b")

    with pytest.raises(HTTPException) as exc:
        assert_draft_access(draft, journalist, action="read")

    assert exc.value.status_code == 404


def test_editor_chief_can_access_pending_draft() -> None:
    chief = _user(user_id=2, username="chief", role=UserRole.editor_chief)
    draft = _draft(created_by="journalist_b", status="draft")

    assert_draft_access(draft, chief, action="approve")


def test_director_has_admin_access_to_draft() -> None:
    director = _user(user_id=3, username="director", role=UserRole.director)
    draft = _draft(created_by="journalist_b")

    assert_draft_access(draft, director, action="admin")


def test_memory_item_write_requires_creator_for_low_privilege_user() -> None:
    journalist = _user(user_id=7, username="journalist_a", role=UserRole.journalist)
    item = ProjectMemoryItem(id=1, title="t", content="c", created_by_user_id=8)

    with pytest.raises(HTTPException) as exc:
        _assert_item_write_access(journalist, item)

    assert exc.value.status_code == 403


def test_memory_item_write_allows_director_override() -> None:
    director = _user(user_id=9, username="director", role=UserRole.director)
    item = ProjectMemoryItem(id=1, title="t", content="c", created_by_user_id=8)

    _assert_item_write_access(director, item)


def test_simulator_run_access_blocks_cross_user_reads() -> None:
    journalist = _user(user_id=1, username="journalist_a", role=UserRole.journalist)
    run = _SimRun(created_by_user_id=2, created_by_username="journalist_b")

    with pytest.raises(HTTPException) as exc:
        _assert_run_access(journalist, run)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_director_role_creation_blocked_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    actor = _user(user_id=1, username="director_a", role=UserRole.director)
    recorded: list[dict] = []

    async def fake_log_activity(db, **kwargs):  # noqa: ANN001
        recorded.append(kwargs)

    monkeypatch.setattr(auth_routes, "_log_activity", fake_log_activity)
    monkeypatch.setattr(auth_routes.settings, "allow_director_self_management", False)

    with pytest.raises(HTTPException) as exc:
        await auth_routes._assert_director_role_assignment_allowed(
            db=object(),
            actor=actor,
            target=None,
            requested_role=UserRole.director,
            action="membership_create_user",
        )

    assert exc.value.status_code == 403
    assert recorded


@pytest.mark.asyncio
async def test_director_role_creation_allowed_with_override(monkeypatch: pytest.MonkeyPatch) -> None:
    actor = _user(user_id=1, username="director_a", role=UserRole.director)
    monkeypatch.setattr(auth_routes.settings, "allow_director_self_management", True)

    await auth_routes._assert_director_role_assignment_allowed(
        db=object(),
        actor=actor,
        target=None,
        requested_role=UserRole.director,
        action="membership_create_user",
    )
