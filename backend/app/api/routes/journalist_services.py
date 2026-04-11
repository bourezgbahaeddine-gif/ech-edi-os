"""
Echorouk Editorial OS — Journalist Services
=======================================
Editor/Fact-check/SEO/Multimedia tools for journalists.
"""

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.rbac import require_roles
from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User, UserRole
from app.services.ai_service import ai_service
from app.services.fact_check_tools_service import fact_check_tools_service

NEWSROOM_SERVICE_ROLES = (
    UserRole.director,
    UserRole.editor_chief,
    UserRole.journalist,
    UserRole.social_media,
    UserRole.print_editor,
)

router = APIRouter(
    prefix="/services",
    tags=["Journalist Services"],
    dependencies=[Depends(require_roles(*NEWSROOM_SERVICE_ROLES))],
)

CONSTITUTION_BASE = (
    "التزم بدستور الشروق التحريري: دقة، توازن، حياد، وضوح، عدم الإثارة، "
    "صياغة مهنية قابلة للنشر، ومنع الحشو أو التعليقات خارج النص المطلوب."
)


class _StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _LanguagePayload(_StrictPayload):
    language: str | None = Field(default="ar", max_length=8)


class EditorTonalityRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class EditorInvertedPyramidRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class EditorProofreadRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class EditorSocialSummaryRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)
    platform: str = Field(default="general", max_length=64)


class FactcheckVisionRequest(_StrictPayload):
    image_url: str = Field(..., min_length=5, max_length=4096)
    question: str = Field(
        default="تحقق من صحة الصورة وسياقها وما إذا كانت معدلة أو خارج السياق.",
        max_length=1000,
    )


class FactcheckConsistencyRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)
    reference: str = Field(default="", max_length=20000)


class FactcheckExtractRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class FactcheckGoogleRequest(_LanguagePayload):
    query: str | None = Field(default=None, max_length=2000)
    text: str | None = Field(default=None, max_length=2000)
    page_size: int = Field(default=4, ge=1, le=10)

    @model_validator(mode="after")
    def validate_query_or_text(self):
        if not (self.query or self.text):
            raise ValueError("Either query or text is required")
        return self


class SeoKeywordsRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class SeoInternalLinksRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)
    archive_titles: list[str] = Field(default_factory=list, max_length=50)


class SeoMetadataRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class MultimediaVideoScriptRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class MultimediaSentimentRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)


class MultimediaTranslateRequest(_LanguagePayload):
    text: str = Field(..., min_length=1)
    source_lang: str = Field(default="auto", max_length=32)


class MultimediaImagePromptRequest(_StrictPayload):
    text: str = Field(..., min_length=1)
    style: str = Field(default="cinematic", max_length=128)
    model: str | None = Field(default="nanobanana2", max_length=128)
    language: str | None = Field(default="ar", max_length=8)
    article_id: int | None = None


class InfographicAnalyzeRequest(_StrictPayload):
    text: str = Field(..., min_length=1)
    language: str | None = Field(default="ar", max_length=8)
    article_id: int | None = None


class InfographicPromptRequest(_StrictPayload):
    data: dict = Field(default_factory=dict)
    model: str | None = Field(default="nanobanana2", max_length=128)
    language: str | None = Field(default="ar", max_length=8)
    article_id: int | None = None


class InfographicRenderRequest(_StrictPayload):
    prompt: str = Field(..., min_length=1)


def _sanitize_ai_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?im)^\s*(note|notes|explanation|comment)\s*:.*$", "", cleaned)
    cleaned = re.sub(r"(?im)^\s*(ملاحظة|شرح|تعليق)\s*:.*$", "", cleaned)
    cleaned = re.sub(r"(?im)^\s*(حسنًا|حسنا|يمكنني|آمل).*$", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _target_language(language: str | None) -> str:
    lang = (language or "ar").lower().strip()
    if lang not in {"ar", "fr", "en"}:
        return "ar"
    return lang


def _lang_name(lang: str) -> str:
    return {"ar": "العربية الفصحى", "fr": "الفرنسية", "en": "الإنجليزية"}[lang]


@router.post("/editor/tonality")
async def editor_tonality(payload: EditorTonalityRequest):
    """Rewrite text in a newsroom-safe tone. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"أعد صياغة النص التالي بلغة {_lang_name(lang)} بنبرة مهنية غير مثيرة.\n"
        "أعط 3 بدائل قصيرة صالحة للنشر فقط، بدون شرح إضافي أو عناوين تقنية."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/editor/inverted-pyramid")
async def editor_inverted_pyramid(payload: EditorInvertedPyramidRequest):
    """Rewrite text in inverted-pyramid form. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"أعد كتابة الخبر التالي بلغة {_lang_name(lang)} وفق أسلوب الهرم المقلوب.\n"
        "ابدأ بفقرة تمهيدية تجيب من/ماذا/أين/متى/لماذا/كيف، ثم التفاصيل حسب الأهمية.\n"
        "أعد النص النهائي فقط."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/editor/proofread")
async def editor_proofread(payload: EditorProofreadRequest):
    """Proofread newsroom text. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"دقق النص التالي بلغة {_lang_name(lang)}.\n"
        "صحح الأخطاء الإملائية والنحوية وعلامات الترقيم فقط دون تغيير المعنى.\n"
        "أعد النص المصحح فقط."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/editor/social-summary")
async def editor_social_summary(payload: EditorSocialSummaryRequest):
    """Generate short social-ready summaries. Input: text, platform, optional language."""
    text = payload.text
    platform = payload.platform
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"لخّص الخبر التالي بلغة {_lang_name(lang)} لمنصة {platform} دون تهويل أو clickbait.\n"
        "أعط بديلين قصيرين (1-2 جملة) جاهزين للنشر."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/factcheck/vision")
async def factcheck_vision(payload: FactcheckVisionRequest):
    """Run image fact-checking. Input: image_url and optional question."""
    image_url = payload.image_url
    question = payload.question
    result = await ai_service.analyze_image_url(image_url, question)
    return {"result": _sanitize_ai_text(result)}


@router.post("/factcheck/consistency")
async def factcheck_consistency(payload: FactcheckConsistencyRequest):
    """Check consistency against optional reference text."""
    text = payload.text
    reference = payload.reference
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"تحقق من اتساق النص التالي بلغة {_lang_name(lang)} واكتشف التناقضات أو الأخطاء المحتملة.\n"
        "إذا وُجد مرجع فقارن معه بدقة، ثم اقترح تصحيحات قصيرة قابلة للنشر.\n\n"
        f"Reference:\n{reference}\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/factcheck/extract")
async def factcheck_extract(payload: FactcheckExtractRequest):
    """Extract fact-checking points from article text."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"استخرج أهم النقاط من النص التالي بلغة {_lang_name(lang)}.\n"
        "أعد نقاطًا مرتبة + خلاصة تنفيذية من 3 جمل."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/factcheck/google")
async def factcheck_google(payload: FactcheckGoogleRequest):
    """Search fact-check sources. Input: query or text, optional language, validated page_size."""
    query = payload.query or payload.text or ""
    language = _target_language(payload.language)
    page_size = payload.page_size

    async def translate_to_english(text: str) -> str:
        if not ai_service:
            return ""
        prompt = (
            "Translate this claim into concise English (single sentence). "
            "Return only the translated sentence without quotes or explanation.\n\n"
            f"Claim:\n{text}"
        )
        result = await ai_service.generate_text(prompt)
        return _sanitize_ai_text(result).splitlines()[0].strip()

    matches, queries = await fact_check_tools_service.search_claims_with_fallbacks(
        query,
        language=language,
        page_size=page_size,
        translate_fn=translate_to_english if language == "ar" else None,
    )
    summary = fact_check_tools_service.summarize_matches(matches)
    return {"matches": matches, "summary": summary, "queries": queries}


@router.post("/seo/keywords")
async def seo_keywords(payload: SeoKeywordsRequest):
    """Generate SEO keywords. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"ولّد 10 كلمات مفتاحية SEO طويلة الذيل بلغة {_lang_name(lang)} مرتبطة بالخبر التالي.\n"
        "أعدها كسطر واحد مفصول بفواصل."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/seo/internal-links")
async def seo_internal_links(payload: SeoInternalLinksRequest):
    """Suggest internal links. Input: text, archive_titles, optional language."""
    text = payload.text
    archive_titles = payload.archive_titles
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"اقترح 5 روابط داخلية مناسبة من الأرشيف بلغة {_lang_name(lang)}.\n"
        "أعد عناوين المقالات فقط.\n\n"
        f"News:\n{text}\n\nArchive Titles:\n{archive_titles}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/seo/metadata")
async def seo_metadata(payload: SeoMetadataRequest):
    """Generate SEO metadata. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"اكتب بيانات SEO بلغة {_lang_name(lang)} لهذا الخبر:\n"
        "1) SEO Title (<=60)\n"
        "2) Meta Description (<=160)\n"
        "3) Slug (latin kebab-case).\n"
        "أعد فقط JSON بالمفاتيح: seo_title, meta_description, slug.\n\n"
        f"Text:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/multimedia/video-script")
async def multimedia_video_script(payload: MultimediaVideoScriptRequest):
    """Generate a short video script. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"أنشئ سكريبت فيديو قصير (60-90 ثانية) بلغة {_lang_name(lang)} من هذا الخبر.\n"
        "ضمّن المشاهد المقترحة والنص الظاهر على الشاشة."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/multimedia/sentiment")
async def multimedia_sentiment(payload: MultimediaSentimentRequest):
    """Analyze sentiment and topics. Input: text, optional language."""
    text = payload.text
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"حلّل الانطباع العام للنص التالي بلغة {_lang_name(lang)}.\n"
        "أعد تقريرًا مختصرًا: الاتجاه العام + أهم الموضوعات."
        f"\n\nText:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/multimedia/translate")
async def multimedia_translate(payload: MultimediaTranslateRequest):
    """Translate newsroom text. Input: text, source_lang, optional target language."""
    text = payload.text
    source_lang = payload.source_lang
    lang = _target_language(payload.language)
    prompt = (
        f"{CONSTITUTION_BASE}\n"
        f"ترجم النص التالي من {source_lang} إلى {_lang_name(lang)} مع الحفاظ الكامل على المعنى والسياق الصحفي.\n"
        "أعد النص النهائي فقط دون ملاحظات.\n\n"
        f"Text:\n{text}"
    )
    result = await ai_service.generate_text(prompt)
    return {"result": _sanitize_ai_text(result)}


@router.post("/multimedia/image-prompt")
async def multimedia_image_prompt(
    payload: MultimediaImagePromptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text = payload.text
    style = payload.style
    model = (payload.model or "nanobanana2").strip().lower()
    lang = _target_language(payload.language)
    article_id = payload.article_id

    prompt = f"""
{CONSTITUTION_BASE}
You are a senior newsroom visual prompt engineer.
Target model: {model} (NanoBanana 2 compatible).
Language for final prompts: {_lang_name(lang)}.

Return exactly 3 prompts only (numbered 1/2/3), no commentary.
Each prompt must be production-ready and include sections in this exact order:
[SUBJECT]
[EDITORIAL_ANGLE]
[SCENE_DETAILS]
[CAMERA]
[LIGHTING]
[COMPOSITION]
[COLOR_GRADE]
[NEGATIVE_PROMPT]
[OUTPUT_SPEC]

Quality requirements:
- Photorealistic editorial style, no fantasy/cartoon look.
- Include concrete details: place, actors, action, mood, depth cues.
- Keep visual truthfulness and avoid exaggeration or manipulation.
- No text overlays, no watermark, no logos, no deformed anatomy.
- Respect cultural sensitivity and avoid shocking/gory visuals.
- Reserve clean safe-space for headline placement.

News content:
{text}

Requested style:
{style}
"""
    result = _sanitize_ai_text(await ai_service.generate_text(prompt))
    if result:
        from app.models.constitution import ImagePrompt
        # Audit identity is derived from the authenticated user, never from client payload.
        db.add(ImagePrompt(
            article_id=article_id,
            prompt_text=result,
            style=style,
            created_by=current_user.username,
        ))
        await db.commit()
    return {"result": result}


@router.post("/multimedia/infographic/analyze")
async def infographic_analyze(
    payload: InfographicAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text = payload.text
    lang = _target_language(payload.language)
    article_id = payload.article_id

    prompt = f"""
{CONSTITUTION_BASE}
حلّل الخبر التالي وأخرج بيانات منظمة لإنفوغرافيا باللغة {_lang_name(lang)}.
أعد JSON فقط بهذا المخطط:
{{
  "title": "عنوان قصير",
  "items": [{{"id": "1", "label": "اسم البند", "value": "القيمة"}}],
  "type": "timeline|ranking|comparison|numbers|map|steps|profile|stats|quote|impact",
  "theme": "dark|light|orange|mono",
  "aspect_ratio": "1:1|4:5|16:9|9:16"
}}

لا تضف أي شرح خارج JSON.

النص:
{text}
"""
    data = await ai_service.generate_json(prompt)
    if data:
        from app.models.constitution import InfographicData
        import json
        # Audit identity is derived from the authenticated user, never from client payload.
        db.add(InfographicData(
            article_id=article_id,
            data_json=json.dumps(data, ensure_ascii=False),
            created_by=current_user.username,
        ))
        await db.commit()
    return {"data": data}


@router.post("/multimedia/infographic/prompt")
async def infographic_prompt(
    payload: InfographicPromptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.data
    model = (payload.model or "nanobanana2").strip().lower()
    lang = _target_language(payload.language)
    article_id = payload.article_id
    if not data:
        raise HTTPException(400, "Missing data")
    prompt = f"""
{CONSTITUTION_BASE}
You are a senior infographic prompt engineer for newsroom publishing.
Target model: {model} (NanoBanana 2 compatible).
Create one final infographic prompt in {_lang_name(lang)} from this structured data:
{data}

Return the final prompt only (no notes), with these sections:
[NARRATIVE_OBJECTIVE]
[LAYOUT_GRID]
[VISUAL_HIERARCHY]
[DATA_BINDING]
[TYPOGRAPHY]
[ICONOGRAPHY]
[COLOR_SYSTEM]
[NEGATIVE_PROMPT]
[ASPECT_RATIO]
[EXPORT_NOTES]

Rules:
- Journalistic clarity over decoration.
- High readability in Arabic (clear labels and number formatting).
- Strong contrast and spacing discipline.
- Prioritize key numbers and comparisons.
- No clutter, no tiny illegible text, no random decorative icons.
"""
    result = _sanitize_ai_text(await ai_service.generate_text(prompt))
    if result:
        from app.models.constitution import InfographicData
        import json
        # Audit identity is derived from the authenticated user, never from client payload.
        db.add(InfographicData(
            article_id=article_id,
            data_json=json.dumps(data, ensure_ascii=False),
            prompt_text=result,
            created_by=current_user.username,
        ))
        await db.commit()
    return {"result": result}


@router.post("/multimedia/infographic/render")
async def infographic_render(payload: InfographicRenderRequest):
    """Render entrypoint for infographic prompt output. Input: prompt."""
    prompt = payload.prompt
    return {"image_url": "", "prompt": prompt}
