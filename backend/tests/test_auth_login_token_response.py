from types import SimpleNamespace

from fastapi import Response

from app.api.routes import auth as auth_route
from app.core.security import hash_password
from app.models.user import UserRole
from app.schemas.auth import LoginRequest


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _FakeDB:
    def __init__(self, user):
        self._user = user
        self.execute_calls = 0
        self.committed = False

    async def execute(self, _query):
        self.execute_calls += 1
        if self.execute_calls == 1:
            return _ScalarResult(self._user)
        return _ScalarResult(None)

    async def commit(self):
        self.committed = True


async def _noop(*_args, **_kwargs):
    return None


async def test_login_returns_access_token(monkeypatch):
    user = SimpleNamespace(
        id=1,
        full_name_ar="مستخدم اختبار",
        username="editor",
        hashed_password=hash_password("secret123"),
        role=UserRole.journalist,
        departments=["newsroom"],
        specialization=None,
        is_active=True,
        last_login_at=None,
    )
    db = _FakeDB(user)
    response = Response()

    monkeypatch.setattr(auth_route, "_check_login_rate", _noop)
    monkeypatch.setattr(auth_route, "_log_activity", _noop)
    monkeypatch.setattr(auth_route.cache_service, "delete", _noop)

    result = await auth_route.login(
        LoginRequest(username="editor", password="secret123"),
        response,
        db=db,
    )

    assert isinstance(result.access_token, str)
    assert result.access_token
    assert result.token_type == "bearer"
    assert result.user.username == "editor"
