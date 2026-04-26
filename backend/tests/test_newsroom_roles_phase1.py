from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.agents.social_package_agent import settings as social_package_settings
from app.api.deps.rbac import enforce_roles
from app.api.routes import journalist_services as journalist_services_route
from app.models.user import UserRole


def _user(role: UserRole):
    return SimpleNamespace(role=role)


def test_user_roles_presenter_show_host_journalist_equivalent():
    enforce_roles(_user(UserRole.presenter), {UserRole.journalist})
    enforce_roles(_user(UserRole.show_host), {UserRole.journalist})

    with pytest.raises(HTTPException) as presenter_exc:
        enforce_roles(_user(UserRole.presenter), {UserRole.editor_chief})
    assert presenter_exc.value.status_code == 403


@pytest.mark.asyncio
async def test_broadcast_rewrite_endpoint_contract(monkeypatch):
    async def _fake_generate_json(_prompt: str):
        return {
            "broadcast_text": "نص بثي واضح وقصير.",
            "changes_summary": ["تقصير الجمل", "تبسيط الإيقاع"],
        }

    monkeypatch.setattr(journalist_services_route.ai_service, "generate_json", _fake_generate_json)

    payload = journalist_services_route.EditorBroadcastRewriteRequest(
        text="هذا نص طويل نسبيًا يحتاج إلى تهيئة للبث.",
        duration_target_seconds=45,
        language="ar",
    )
    result = await journalist_services_route.editor_broadcast_rewrite(payload)

    assert result["broadcast_text"] == "نص بثي واضح وقصير."
    assert result["word_count"] > 0
    assert result["estimated_read_seconds"] > 0
    assert result["changes_summary"] == ["تقصير الجمل", "تبسيط الإيقاع"]


def test_social_package_feature_flag_disabled_by_default():
    assert social_package_settings.social_package_enabled is False
