import asyncio

from app.services.smart_editor_service import smart_editor_service


def test_sanitize_html_removes_script_and_javascript_href():
    dirty = '<h1>Title</h1><script>alert(1)</script><a href="javascript:alert(1)">x</a><p>ok</p>'
    clean = smart_editor_service.sanitize_html(dirty)
    assert '<script' not in clean.lower()
    assert 'javascript:' not in clean.lower()
    assert '<h1>' in clean
    assert '<p>ok</p>' in clean


def test_build_diff_returns_add_remove_counts():
    diff = smart_editor_service.build_diff('line1\nline2', 'line1\nline3')
    assert isinstance(diff.diff, str)
    assert diff.added >= 1
    assert diff.removed >= 1


def test_fact_check_report_blocks_low_confidence_claims():
    text = 'Official source said the number reached 3 in 2026.'
    report = asyncio.run(smart_editor_service.fact_check_report(text=text, source_url=None, threshold=0.95))
    assert report['passed'] is False
    assert report['blocking_reasons']
    assert report['claims']
    assert all('risk_level' in claim for claim in report['claims'])


def test_quality_score_has_required_metrics():
    html = '<h1>Headline</h1><p>The ministry said the number reached 50 today in Algeria.</p>'
    report = smart_editor_service.quality_score(title='Headline', html=html, source_text='source')
    assert 'score' in report
    assert 'metrics' in report
    assert 'clarity' in report['metrics']
    assert 'sources_attribution' in report['metrics']


def test_editorial_policy_review_returns_reservations_on_blockers():
    async def _run():
        return await smart_editor_service.editorial_policy_review(
            title='Test headline',
            body_html='<h1>Headline</h1><p>Text with [template] noise.</p>',
            source_text='source excerpt',
            fact_report={'blocking_reasons': ['unresolved claims']},
            quality_report={'blocking_reasons': []},
            readability_report={'blocking_reasons': []},
        )

    report = asyncio.run(_run())
    assert report['decision'] == 'reservations'
    assert report['passed'] is False
    assert report['blocking_reasons']


def test_social_variants_include_instagram_tiktok(monkeypatch):
    class _FakeAi:
        async def generate_json(self, _prompt):
            return {
                "facebook": "fb copy",
                "x": "x copy",
                "push": "push copy",
                "summary_120": "summary copy",
                "breaking_alert": "breaking copy",
                "instagram": "instagram caption",
                "tiktok_hook_3s": "hook",
                "tiktok_main_point_10s": "main point",
                "tiktok_cta_3s": "cta",
                "tiktok_hashtags": "#one #two",
                "tiktok_visual_direction": "vertical shots",
                "tiktok_sound_or_trend_suggestion": "calm newsroom beat",
            }

    monkeypatch.setattr(smart_editor_service, "_get_ai_service", lambda: _FakeAi())

    variants = asyncio.run(
        smart_editor_service.social_variants(
            source_text="source",
            draft_title="title",
            draft_html="<p>body</p>",
        )
    )

    assert variants["facebook"] == "fb copy"
    assert variants["instagram"] == "instagram caption"
    assert variants["tiktok_hook_3s"] == "hook"
    assert "main point" in variants["tiktok"]
