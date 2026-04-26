from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.api.routes.auth import get_current_user
from app.models.user import User, UserRole


JOURNALIST_EQUIVALENT_ROLES = {UserRole.journalist, UserRole.presenter, UserRole.show_host}


def enforce_roles(
    user: User,
    allowed: Iterable[UserRole],
    *,
    message: str = "Not authorized for this action",
) -> None:
    allowed_set = set(allowed)
    if UserRole.journalist in allowed_set and user.role in JOURNALIST_EQUIVALENT_ROLES:
        return
    if user.role not in allowed_set:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def require_roles(*allowed: UserRole):
    async def _dependency(current_user: User = Depends(get_current_user)) -> User:
        enforce_roles(current_user, allowed)
        return current_user

    return _dependency
