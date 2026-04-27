"""
Echorouk Editorial OS — News API Routes
=====================================
CRUD operations for articles with filtering & pagination.
"""

from datetime import datetime, timedelta
import math
import re
import unicodedata
from urllib.parse import urlparse, urlunparse
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, select, func, desc, and_, or_, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import (
    Article,
    ArticleRelation,
    ArticleVector,
    CompetitorXrayItem,
    NewsCategory,
    NewsStatus,
    StoryCluster,
    StoryClusterMember,
    UrgencyLevel,
)
from app.schemas import ArticleResponse, ArticleBrief, PaginatedResponse
from app.services.embedding_service import embedding_service
from app.services.trend_signal_service import bump_keyword_interactions, extract_keywords
from app.utils.status_filters import article_status_is_social_packaged

router = APIRouter(prefix="/news", tags=["News"])
settings = get_settings()
TOKEN_RE = re.compile(r"[\u0600-\u06FFA-Za-z\u00C0-\u024F0-9]{2,}")
SPACE_RE = re.compile(r"\s+")
STOPWORDS = {
    # Arabic
    "في", "من", "على", "الى", "إلى", "عن", "مع", "هذا", "هذه", "ذلك", "تلك",
    "بعد", "قبل", "بين", "حول", "حتى", "أو", "و", "التي", "الذي", "الذين",
    # French
    "les", "des", "dans", "avec", "pour", "sur", "une", "un", "du", "de", "et",
    # English
    "the", "and", "for", "with", "from", "into", "over", "under", "that", "this",
}
SYNONYMS = {
    # Arabic <-> French/English newsroom concepts
    "الطاقة": {"طاقة", "الطاقوية", "الطاقي", "energie", "énergie", "energetique", "énergétique", "energy"},
    "طاقة": {"الطاقة", "الطاقوية", "الطاقي", "energie", "énergie", "energetique", "énergétique", "energy"},
    "الجزائر": {"جزائر", "algerie", "algérie", "algeria", "algérien", "algerien"},
    "جزائر": {"الجزائر", "algerie", "algérie", "algeria", "algérien", "algerien"},
}

LOCAL_PRIORITY_TERMS = [
    "الجزائر",
    "جزائري",
    "جزائرية",
    "algeria",
    "algerie",
    "algérie",
    "dz",
    "رئاسة الجمهورية",
    "الوزير الأول",
    "سوناطراك",
    "وزارة",
]

LOCAL_PRIORITY_SOURCES = [
    "echorouk",
    "الشروق",
    "aps",
    "tsa",
    "el khabar",
    "الخبر",
    "النهار",
]
EDITORIAL_PRIORITY_BASE_STATUSES = [
    NewsStatus.CANDIDATE,
    NewsStatus.APPROVED,
    NewsStatus.APPROVED_HANDOFF,
    NewsStatus.DRAFT_GENERATED,
    NewsStatus.READY_FOR_CHIEF_APPROVAL,
    NewsStatus.READY_FOR_MANUAL_PUBLISH,
]
EDITORIAL_PRIORITY_PUBLISHED_STATUSES = [
    NewsStatus.PUBLISHED.value,
    NewsStatus.SOCIAL_PACKAGED.value,
]
EDITORIAL_URGENCY_BONUS = {
    UrgencyLevel.LOW.value: 0.0,
    UrgencyLevel.MEDIUM.value: 0.8,
    UrgencyLevel.HIGH.value: 1.4,
    UrgencyLevel.BREAKING.value: 2.0,
}


def _tokenize(text: str) -> set[str]:
    return {m.group(0).lower() for m in TOKEN_RE.finditer(text or "")}


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""
    t = (text or "").strip().lower()
    # Fold accents so "énergie" and "energie" match consistently.
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return SPACE_RE.sub(" ", t)


def _token_forms(token: str) -> set[str]:
    token_norm = _normalize_text(token)
    forms = {token_norm}
    # Arabic definite article normalization: "الطاقة" -> "طاقة"
    if token_norm.startswith("ال") and len(token_norm) > 4:
        forms.add(token_norm[2:])
    forms |= {_normalize_text(x) for x in SYNONYMS.get(token_norm, set())}
    return {f for f in forms if f}


def _matched_query_tokens(query_tokens: set[str], text_tokens: set[str], text_norm: str) -> set[str]:
    matched: set[str] = set()
    for token in query_tokens:
        forms = _token_forms(token)
        if any(f in text_tokens for f in forms):
            matched.add(token)
            continue
        # Fallback for derivations (e.g., طاقة / الطاقوية)
        if any(len(f) >= 4 and f in text_norm for f in forms):
            matched.add(token)
    return matched


def _is_geo_token(token: str) -> bool:
    t = _normalize_text(token)
    return t in {"الجزائر", "جزائر", "algerie", "algeria"}


def _canonical_url(url: str | None) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        return urlunparse(parsed._replace(query="", fragment=""))
    except Exception:
        return url


def _source_trust(source_name: str | None) -> float:
    s = (source_name or "").lower()
    if not s:
        return 0.4
    trusted = [
        "aps", "reuters", "bbc", "france24", "le monde", "guardian", "echorouk", "el khabar",
    ]
    low = ["news.google.com", "google news", "aggregator", "reddit"]
    if any(k in s for k in trusted):
        return 1.0
    if any(k in s for k in low):
        return 0.25
    return 0.6


def _is_aggregator_source(source_name: str | None) -> bool:
    s = (source_name or "").lower()
    return "news.google.com" in s or "google news" in s or "aggregator" in s


def _local_priority_expression():
    title_match = or_(*[Article.original_title.ilike(f"%{term}%") for term in LOCAL_PRIORITY_TERMS])
    arabic_title_match = or_(*[Article.title_ar.ilike(f"%{term}%") for term in LOCAL_PRIORITY_TERMS])
    summary_match = or_(*[Article.summary.ilike(f"%{term}%") for term in LOCAL_PRIORITY_TERMS])
    source_match = or_(*[Article.source_name.ilike(f"%{term}%") for term in LOCAL_PRIORITY_SOURCES])
    category_local = Article.category == NewsCategory.LOCAL_ALGERIA
    return case(
        (category_local, 4),
        (source_match, 3),
        (title_match, 2),
        (arabic_title_match, 2),
        (summary_match, 1),
        else_=0,
    )


async def _expire_stale_breaking_flags(db: AsyncSession) -> None:
    cutoff = datetime.utcnow() - timedelta(minutes=settings.breaking_news_ttl_minutes)
    await db.execute(
        update(Article)
        .where(
            and_(
                Article.is_breaking == True,
                func.coalesce(Article.published_at, Article.crawled_at) < cutoff,
            )
        )
        .values(
            is_breaking=False,
            urgency=UrgencyLevel.HIGH,
            updated_at=datetime.utcnow(),
        )
    )
    await db.commit()


def _priority_queue_statuses(include_published: bool) -> list[NewsStatus | str]:
    statuses = list(EDITORIAL_PRIORITY_BASE_STATUSES)
    if include_published:
        statuses.extend(EDITORIAL_PRIORITY_PUBLISHED_STATUSES)
    return statuses


def _db_news_status_value(status: NewsStatus | str) -> NewsStatus | str:
    if isinstance(status, NewsStatus):
        return status.value if status == NewsStatus.SOCIAL_PACKAGED else status
    return status


def _article_status_is_social_packaged():
    return article_status_is_social_packaged(Article.status)


def _article_status_in(statuses: list[NewsStatus | str]):
    regular_statuses = []
    includes_social_packaged = False
    for status in statuses:
        if status == NewsStatus.SOCIAL_PACKAGED or status == NewsStatus.SOCIAL_PACKAGED.value:
            includes_social_packaged = True
        else:
            regular_statuses.append(status)

    if includes_social_packaged and regular_statuses:
        return or_(Article.status.in_(regular_statuses), _article_status_is_social_packaged())
    if includes_social_packaged:
        return _article_status_is_social_packaged()
    return Article.status.in_(regular_statuses)


def _parse_news_status_query(status: str) -> NewsStatus:
    raw = (status or "").strip()
    if not raw:
        raise ValueError("empty status")

    normalized = raw.replace(" ", "_")
    try:
        return NewsStatus(normalized.lower())
    except ValueError:
        pass

    try:
        return NewsStatus[normalized.upper()]
    except KeyError as exc:
        raise ValueError(raw) from exc


def _safe_article_display_title(article: Article) -> str:
    for candidate in (article.title_ar, article.original_title, article.original_url):
        if candidate and str(candidate).strip():
            return str(candidate).strip()
    return "بدون عنوان"


def _priority_recommended_action(status: str) -> str:
    value = (status or "").lower()
    if value == NewsStatus.CANDIDATE.value:
        return "ابدأ التغطية الآن"
    if value in {NewsStatus.APPROVED.value, NewsStatus.APPROVED_HANDOFF.value}:
        return "ابدأ التحرير الآن"
    if value == NewsStatus.DRAFT_GENERATED.value:
        return "أكمل المسودة الآن"
    if value == NewsStatus.READY_FOR_CHIEF_APPROVAL.value:
        return "احسم الاعتماد الآن"
    if value == NewsStatus.READY_FOR_MANUAL_PUBLISH.value:
        return "راجع الجاهز للنشر الآن"
    if value in {NewsStatus.PUBLISHED.value, NewsStatus.SOCIAL_PACKAGED.value}:
        return "تابع التغطية أو التحديث التحريري"
    return "راجع المادة الآن"


def _priority_freshness_score(*, reference_time: datetime | None, now: datetime, window_hours: int) -> tuple[float, float]:
    if reference_time is None:
        return 0.0, float(window_hours)
    age_hours = max((now - reference_time).total_seconds() / 3600.0, 0.0)
    ratio = max(0.0, 1.0 - min(age_hours / max(window_hours, 1), 1.0))
    return round(ratio * 2.0, 2), age_hours


def _priority_competitor_pressure(payload: dict[str, Any] | None) -> float:
    if not payload:
        return 0.0
    count = int(payload.get("count") or 0)
    max_priority = float(payload.get("max_priority") or 0.0)
    return round(min((count * 0.55) + (max_priority * 0.08), 2.2), 2)


def _priority_cluster_velocity(cluster_size: int | float | None) -> float:
    size = max(int(cluster_size or 0), 0)
    if size <= 1:
        return 0.0
    return round(min((size - 1) * 0.35, 1.6), 2)


def _build_priority_queue_items(
    articles: list[Article],
    *,
    now: datetime | None = None,
    window_hours: int = 24,
    include_published: bool = False,
    competitor_map: dict[int, dict[str, Any]] | None = None,
    cluster_map: dict[int, int] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    current_time = now or datetime.utcnow()
    allowed_statuses = {
        status.value if isinstance(status, NewsStatus) else str(status)
        for status in _priority_queue_statuses(include_published)
    }
    competitor_map = competitor_map or {}
    cluster_map = cluster_map or {}
    items: list[dict[str, Any]] = []

    for article in articles:
        status_value = (article.status.value if isinstance(article.status, NewsStatus) else str(article.status or "")).lower()
        if status_value == NewsStatus.ARCHIVED.value:
            continue
        if status_value not in allowed_statuses:
            continue

        reference_time = article.created_at or article.crawled_at or article.updated_at
        freshness_score, age_hours = _priority_freshness_score(
            reference_time=reference_time,
            now=current_time,
            window_hours=window_hours,
        )
        urgency_value = (article.urgency.value if isinstance(article.urgency, UrgencyLevel) else str(article.urgency or "")).lower()
        urgency_bonus = float(EDITORIAL_URGENCY_BONUS.get(urgency_value, 0.0))
        breaking_bonus = 2.0 if bool(article.is_breaking) else 0.0
        competitor_pressure = _priority_competitor_pressure(competitor_map.get(int(article.id)))
        cluster_velocity = _priority_cluster_velocity(cluster_map.get(int(article.id)))
        priority_score = round(
            (float(article.importance_score or 0) * 0.35)
            + breaking_bonus
            + freshness_score
            + urgency_bonus
            + competitor_pressure
            + cluster_velocity,
            2,
        )

        reasons: list[str] = []
        if bool(article.is_breaking):
            reasons.append("خبر عاجل")
        if int(article.importance_score or 0) >= 8:
            reasons.append("أهمية مرتفعة")
        elif int(article.importance_score or 0) >= 6:
            reasons.append("أهمية جيدة")
        if freshness_score >= 1.4:
            reasons.append("حديث جدًا")
        elif freshness_score >= 0.8:
            reasons.append("حديث")
        if urgency_bonus >= 1.4:
            reasons.append("أولوية زمنية مرتفعة")
        if competitor_pressure >= 0.8:
            reasons.append("ضغط تنافسي")
        if cluster_velocity >= 0.7:
            reasons.append("زخم قصصي متصاعد")
        if not reasons:
            reasons.append("يحتاج متابعة تحريرية")

        items.append(
            {
                "article_id": int(article.id),
                "title": _safe_article_display_title(article),
                "status": status_value,
                "category": article.category.value if isinstance(article.category, NewsCategory) else article.category,
                "source_name": article.source_name,
                "created_at": article.created_at.isoformat() if article.created_at else None,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "importance_score": int(article.importance_score or 0),
                "is_breaking": bool(article.is_breaking),
                "urgency": urgency_value or None,
                "priority_score": priority_score,
                "reason": reasons,
                "recommended_action": _priority_recommended_action(status_value),
                "freshness_score": freshness_score,
                "competitor_pressure": competitor_pressure,
                "cluster_velocity": cluster_velocity,
                "age_hours": round(age_hours, 2),
            }
        )

    items.sort(
        key=lambda item: (
            float(item["priority_score"]),
            float(item["competitor_pressure"]),
            float(item["cluster_velocity"]),
            item["created_at"] or "",
        ),
        reverse=True,
    )
    if limit is not None:
        return items[: max(1, int(limit))]
    return items


async def _load_competitor_pressure_map(
    db: AsyncSession,
    *,
    article_ids: list[int],
    cutoff: datetime,
) -> dict[int, dict[str, Any]]:
    if not article_ids:
        return {}
    try:
        rows = await db.execute(
            select(
                CompetitorXrayItem.matched_article_id,
                func.count(CompetitorXrayItem.id).label("gap_count"),
                func.max(CompetitorXrayItem.priority_score).label("max_priority_score"),
            )
            .where(
                and_(
                    CompetitorXrayItem.matched_article_id.in_(article_ids),
                    CompetitorXrayItem.status == "new",
                    CompetitorXrayItem.created_at >= cutoff,
                )
            )
            .group_by(CompetitorXrayItem.matched_article_id)
        )
    except SQLAlchemyError:
        await db.rollback()
        return {}

    out: dict[int, dict[str, Any]] = {}
    for article_id, gap_count, max_priority_score in rows.all():
        if article_id is None:
            continue
        out[int(article_id)] = {
            "count": int(gap_count or 0),
            "max_priority": float(max_priority_score or 0.0),
        }
    return out


async def _load_cluster_velocity_map(
    db: AsyncSession,
    *,
    article_ids: list[int],
) -> dict[int, int]:
    if not article_ids:
        return {}
    sm_self = StoryClusterMember.__table__.alias("pq_sm_self")
    sm_all = StoryClusterMember.__table__.alias("pq_sm_all")
    try:
        rows = await db.execute(
            select(
                sm_self.c.article_id.label("article_id"),
                func.count(sm_all.c.article_id).label("cluster_size"),
            )
            .select_from(
                sm_self.join(sm_all, sm_all.c.cluster_id == sm_self.c.cluster_id)
            )
            .where(sm_self.c.article_id.in_(article_ids))
            .group_by(sm_self.c.article_id)
        )
    except SQLAlchemyError:
        await db.rollback()
        return {}

    return {
        int(article_id): int(cluster_size or 0)
        for article_id, cluster_size in rows.all()
        if article_id is not None
    }


@router.get("/", response_model=PaginatedResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    is_breaking: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|crawled_at|importance_score|published_at)$"),
    local_first: bool = Query(True),
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List articles with filtering and pagination."""
    if is_breaking:
        await _expire_stale_breaking_flags(db)

    query = select(Article)
    count_query = select(func.count(Article.id))
    breaking_cutoff = datetime.utcnow() - timedelta(minutes=settings.breaking_news_ttl_minutes)
    freshness_cutoff = datetime.utcnow() - timedelta(hours=settings.scout_max_article_age_hours)
    actionable_breaking_statuses = [NewsStatus.NEW, NewsStatus.CLASSIFIED, NewsStatus.CANDIDATE]

    # Apply filters
    filters = []
    if status:
        try:
            selected_status = _parse_news_status_query(status)
            if selected_status == NewsStatus.SOCIAL_PACKAGED:
                filters.append(_article_status_is_social_packaged())
            else:
                filters.append(Article.status == selected_status)
            if selected_status not in {
                NewsStatus.PUBLISHED,
                NewsStatus.SOCIAL_PACKAGED,
                NewsStatus.ARCHIVED,
            }:
                filters.append(func.coalesce(Article.published_at, Article.crawled_at) >= freshness_cutoff)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    else:
        # Keep newsroom list focused by hiding archived noise and stale non-published items.
        filters.append(Article.status != NewsStatus.ARCHIVED)
        filters.append(
            or_(
                Article.status == NewsStatus.PUBLISHED,
                _article_status_is_social_packaged(),
                func.coalesce(Article.published_at, Article.crawled_at) >= freshness_cutoff,
            )
        )
    if category:
        try:
            filters.append(Article.category == NewsCategory(category))
        except ValueError:
            raise HTTPException(400, f"Invalid category: {category}")
    if is_breaking is not None:
        filters.append(Article.is_breaking == is_breaking)
        if is_breaking:
            filters.append(func.coalesce(Article.published_at, Article.crawled_at) >= breaking_cutoff)
            if not status:
                filters.append(Article.status.in_(actionable_breaking_statuses))
    if search:
        search_filter = Article.original_title.ilike(f"%{search}%")
        if Article.title_ar:
            search_filter = search_filter | Article.title_ar.ilike(f"%{search}%")
        filters.append(search_filter)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sort and paginate
    sort_column = getattr(Article, sort_by)
    if local_first and not status:
        local_priority = _local_priority_expression()
        query = query.order_by(desc(local_priority), desc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    articles = result.scalars().all()

    return PaginatedResponse(
        items=[ArticleBrief.model_validate(a) for a in articles],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/priority-queue")
async def priority_queue(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    include_published: bool = False,
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return editorial priority queue ranked by urgency, freshness, and available signals."""
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=hours)
    allowed_statuses = [_db_news_status_value(item) for item in _priority_queue_statuses(include_published)]

    filters = [
        _article_status_in(allowed_statuses),
        Article.status != NewsStatus.ARCHIVED,
        func.coalesce(Article.created_at, Article.crawled_at) >= cutoff,
    ]
    if category:
        try:
            selected_category = NewsCategory(category)
        except ValueError:
            raise HTTPException(400, f"Invalid category: {category}")
        filters.append(Article.category == selected_category)

    rows = await db.execute(
        select(Article)
        .where(and_(*filters))
        .order_by(desc(Article.importance_score), desc(Article.created_at), desc(Article.crawled_at))
        .limit(max(limit * 4, 40))
    )
    articles = list(rows.scalars().all())
    article_ids = [int(article.id) for article in articles]
    competitor_map = await _load_competitor_pressure_map(db, article_ids=article_ids, cutoff=cutoff)
    cluster_map = await _load_cluster_velocity_map(db, article_ids=article_ids)
    items = _build_priority_queue_items(
        articles,
        now=now,
        window_hours=hours,
        include_published=include_published,
        competitor_map=competitor_map,
        cluster_map=cluster_map,
        limit=limit,
    )
    return {
        "generated_at": now.isoformat(),
        "window_hours": hours,
        "count": len(items),
        "items": items,
    }


@router.get("/breaking/latest")
async def get_breaking_news(
    limit: int = Query(5, ge=1, le=20),
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get actionable breaking news for dashboard newsroom workflow."""
    await _expire_stale_breaking_flags(db)
    cutoff = datetime.utcnow() - timedelta(minutes=settings.breaking_news_ttl_minutes)
    actionable_breaking_statuses = [NewsStatus.NEW, NewsStatus.CLASSIFIED, NewsStatus.CANDIDATE]
    result = await db.execute(
        select(Article)
        .where(
            and_(
                Article.is_breaking == True,
                func.coalesce(Article.published_at, Article.crawled_at) >= cutoff,
                Article.status.in_(actionable_breaking_statuses),
            )
        )
        .order_by(desc(Article.crawled_at))
        .limit(limit)
    )
    articles = result.scalars().all()
    return [ArticleBrief.model_validate(a) for a in articles]


@router.get("/candidates/pending")
async def get_pending_candidates(
    limit: int = Query(20, ge=1, le=100),
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get articles pending editorial review."""
    freshness_cutoff = datetime.utcnow() - timedelta(hours=settings.scout_max_article_age_hours)
    pending_statuses = [NewsStatus.CANDIDATE]
    if settings.editorial_desk_include_pre_candidate:
        pending_statuses = [
            NewsStatus.NEW,
            NewsStatus.CLEANED,
            NewsStatus.DEDUPED,
            NewsStatus.CLASSIFIED,
            NewsStatus.CANDIDATE,
        ]
    result = await db.execute(
        select(Article)
        .where(
            and_(
                Article.status.in_(pending_statuses),
                func.coalesce(Article.published_at, Article.crawled_at) >= freshness_cutoff,
            )
        )
        .order_by(desc(Article.importance_score), desc(Article.created_at))
        .limit(limit)
    )
    articles = result.scalars().all()
    return [ArticleBrief.model_validate(a) for a in articles]


@router.get("/insights")
async def news_insights(
    article_ids: list[int] = Query(default=[]),
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return lightweight per-article insights for newsroom cards:
    - cluster_size: number of members in the same story cluster
    - relation_count: number of explicit outgoing relations
    """
    ids = [int(x) for x in article_ids if int(x) > 0]
    if not ids:
        return []

    sm_self = StoryClusterMember.__table__.alias("sm_self")
    sm_all = StoryClusterMember.__table__.alias("sm_all")

    cluster_rows = await db.execute(
        select(
            sm_self.c.article_id.label("article_id"),
            sm_self.c.cluster_id.label("cluster_id"),
            func.count(sm_all.c.article_id).label("cluster_size"),
        )
        .select_from(sm_self.join(sm_all, sm_self.c.cluster_id == sm_all.c.cluster_id))
        .where(sm_self.c.article_id.in_(ids))
        .group_by(sm_self.c.article_id, sm_self.c.cluster_id)
    )
    cluster_map: dict[int, dict[str, int]] = {}
    for r in cluster_rows:
        aid = int(r.article_id)
        payload = {"cluster_size": int(r.cluster_size), "cluster_id": int(r.cluster_id)}
        prev = cluster_map.get(aid)
        if prev is None or payload["cluster_size"] > prev["cluster_size"]:
            cluster_map[aid] = payload

    relation_rows = await db.execute(
        select(
            ArticleRelation.from_article_id.label("article_id"),
            func.count(ArticleRelation.id).label("relation_count"),
        )
        .where(ArticleRelation.from_article_id.in_(ids))
        .group_by(ArticleRelation.from_article_id)
    )
    relation_map = {int(r.article_id): int(r.relation_count) for r in relation_rows}

    return [
        {
            "article_id": aid,
            "cluster_size": cluster_map.get(aid, {}).get("cluster_size", 0),
            "cluster_id": cluster_map.get(aid, {}).get("cluster_id"),
            "relation_count": relation_map.get(aid, 0),
        }
        for aid in ids
    ]


@router.get("/search/semantic")
async def semantic_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    mode: str = Query("editorial", pattern="^(editorial|semantic)$"),
    include_aggregators: bool = Query(False),
    strict_tokens: bool = Query(True),
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Hybrid retrieval on vectorized title/summary with editorial ranking.
    """
    query_vec, _ = await embedding_service.embed_query(q)
    query_tokens_raw = _tokenize(q)
    query_tokens = {t for t in query_tokens_raw if t not in STOPWORDS} or query_tokens_raw
    query_norm = _normalize_text(q)
    pool_size = max(limit * 25, 120)

    stmt = (
        select(
            Article,
            ArticleVector.embedding.cosine_distance(query_vec).label("dist"),
        )
        .join(ArticleVector, ArticleVector.article_id == Article.id)
        .where(ArticleVector.vector_type.in_(["title", "summary"]))
        .order_by(ArticleVector.embedding.cosine_distance(query_vec))
        .limit(pool_size)
    )
    if status:
        try:
            selected_status = _parse_news_status_query(status)
            if selected_status == NewsStatus.SOCIAL_PACKAGED:
                stmt = stmt.where(_article_status_is_social_packaged())
            else:
                stmt = stmt.where(Article.status == selected_status)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    else:
        stmt = stmt.where(Article.status != NewsStatus.ARCHIVED)

    rows = await db.execute(stmt)
    raw_items = rows.all()

    # Keep best distance per article first (title+summary can duplicate article rows)
    best_by_article: dict[int, tuple[Article, float]] = {}
    for article, dist in raw_items:
        prev = best_by_article.get(article.id)
        if prev is None or dist < prev[1]:
            best_by_article[article.id] = (article, float(dist))

    now = datetime.utcnow()
    ranked: list[tuple[float, Article]] = []
    required_overlap = 0
    if mode == "editorial" and strict_tokens and len(query_tokens) >= 2:
        if len(query_tokens) <= 3:
            required_overlap = len(query_tokens)
        else:
            required_overlap = max(2, math.ceil(len(query_tokens) * 0.75))
    core_tokens = {t for t in query_tokens if not _is_geo_token(t)}

    def _build_ranked(min_overlap: int, require_title_overlap: bool, require_core_match: bool) -> list[tuple[float, Article]]:
        local_ranked: list[tuple[float, Article]] = []
        for article, dist in best_by_article.values():
            if mode == "editorial" and not include_aggregators and _is_aggregator_source(article.source_name):
                continue

            semantic = 1.0 - max(0.0, min(dist, 2.0)) / 2.0

            combined_text = " ".join([
                article.title_ar or "",
                article.original_title or "",
                article.summary or "",
            ])
            title_text = " ".join([article.title_ar or "", article.original_title or ""])
            text_tokens = _tokenize(combined_text)
            text_norm = _normalize_text(combined_text)
            matched_tokens = _matched_query_tokens(query_tokens, text_tokens, text_norm)
            overlap_count = len(matched_tokens)
            overlap = (overlap_count / max(1, len(query_tokens))) if query_tokens else 0.0
            phrase_hit = 1.0 if query_norm and query_norm in text_norm else 0.0

            if min_overlap and overlap_count < min_overlap:
                continue
            if require_core_match and core_tokens:
                core_matched = _matched_query_tokens(core_tokens, text_tokens, text_norm)
                if not core_matched:
                    continue

            title_tokens = _tokenize(title_text)
            title_norm = _normalize_text(title_text)
            title_overlap_count = len(_matched_query_tokens(query_tokens, title_tokens, title_norm))
            title_overlap = (title_overlap_count / max(1, len(query_tokens))) if query_tokens else 0.0
            if require_title_overlap and title_overlap_count == 0:
                continue

            trust = _source_trust(article.source_name)
            recency_hours = max(0.0, (now - (article.created_at or article.crawled_at or now)).total_seconds() / 3600.0)
            recency = math.exp(-recency_hours / 72.0)
            importance = max(0.0, min(1.0, (article.importance_score or 0) / 10.0))
            breaking = 1.0 if article.is_breaking else 0.0

            if mode == "editorial":
                score = (
                    0.15 * semantic
                    + 0.45 * overlap
                    + 0.10 * title_overlap
                    + 0.12 * phrase_hit
                    + 0.08 * recency
                    + 0.05 * trust
                    + 0.03 * importance
                    + 0.02 * breaking
                )
            else:
                score = (
                    0.70 * semantic
                    + 0.15 * overlap
                    + 0.10 * recency
                    + 0.05 * trust
                )
            local_ranked.append((score, article))
        local_ranked.sort(key=lambda x: x[0], reverse=True)
        return local_ranked

    ranked = _build_ranked(
        min_overlap=required_overlap,
        require_title_overlap=(mode == "editorial" and strict_tokens and len(query_tokens) >= 2),
        require_core_match=(mode == "editorial" and strict_tokens),
    )
    # Progressive fallback: avoid empty UX while preserving relevance.
    if not ranked and mode == "editorial" and strict_tokens:
        ranked = _build_ranked(min_overlap=1, require_title_overlap=False, require_core_match=True)
    if not ranked and mode == "editorial":
        ranked = _build_ranked(min_overlap=1, require_title_overlap=False, require_core_match=False)

    # Canonical URL de-dup on final list.
    final: list[Article] = []
    seen_urls: set[str] = set()
    seen_ids: set[int] = set()
    for _, article in ranked:
        if article.id in seen_ids:
            continue
        url_key = _canonical_url(article.original_url)
        if url_key and url_key in seen_urls:
            continue
        seen_ids.add(article.id)
        if url_key:
            seen_urls.add(url_key)
        final.append(article)
        if len(final) >= limit:
            break

    return [ArticleBrief.model_validate(a) for a in final]


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single article by ID."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article not found")
    await bump_keyword_interactions(extract_keywords(article.title_ar or article.original_title), weight=1)
    return ArticleResponse.model_validate(article)


@router.get("/{article_id}/related")
async def related_articles(
    article_id: int,
    limit: int = Query(8, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve related articles via summary vectors.
    """
    src_vec_result = await db.execute(
        select(ArticleVector)
        .where(
            and_(
                ArticleVector.article_id == article_id,
                ArticleVector.vector_type == "summary",
            )
        )
        .limit(1)
    )
    src_vec = src_vec_result.scalar_one_or_none()
    if not src_vec:
        return []

    stmt = (
        select(Article)
        .join(ArticleVector, ArticleVector.article_id == Article.id)
        .where(
            and_(
                Article.id != article_id,
                ArticleVector.vector_type == "summary",
                Article.status != NewsStatus.ARCHIVED,
            )
        )
        .order_by(ArticleVector.embedding.cosine_distance(src_vec.embedding))
        .limit(limit)
    )
    rows = await db.execute(stmt)
    return [ArticleBrief.model_validate(a) for a in rows.scalars().all()]


@router.get("/{article_id}/cluster")
async def article_cluster(
    article_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Return cluster members for the article (event card view).
    """
    cluster_sizes = (
        select(
            StoryClusterMember.cluster_id.label("cluster_id"),
            func.count(StoryClusterMember.article_id).label("members"),
        )
        .group_by(StoryClusterMember.cluster_id)
        .subquery()
    )
    member_row = await db.execute(
        select(StoryClusterMember)
        .join(cluster_sizes, cluster_sizes.c.cluster_id == StoryClusterMember.cluster_id)
        .where(StoryClusterMember.article_id == article_id)
        .order_by(desc(cluster_sizes.c.members), desc(StoryClusterMember.score), StoryClusterMember.id.asc())
        .limit(1)
    )
    member = member_row.scalar_one_or_none()
    if not member:
        return {"cluster": None, "members": []}

    cluster_row = await db.execute(select(StoryCluster).where(StoryCluster.id == member.cluster_id))
    cluster = cluster_row.scalar_one_or_none()
    if not cluster:
        return {"cluster": None, "members": []}

    rows = await db.execute(
        select(Article)
        .join(StoryClusterMember, StoryClusterMember.article_id == Article.id)
        .where(StoryClusterMember.cluster_id == cluster.id)
        .order_by(desc(StoryClusterMember.score), desc(Article.crawled_at))
        .limit(limit)
    )
    members = [ArticleBrief.model_validate(a) for a in rows.scalars().all()]
    return {
        "cluster": {
            "id": cluster.id,
            "cluster_key": cluster.cluster_key,
            "label": cluster.label,
            "category": cluster.category,
            "geography": cluster.geography,
        },
        "members": members,
    }


@router.get("/{article_id}/relations")
async def article_relations(
    article_id: int,
    relation_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Return explicit relation edges (sequence/impact/contrast/duplicate/related).
    """
    stmt = (
        select(ArticleRelation, Article)
        .join(Article, Article.id == ArticleRelation.to_article_id)
        .where(ArticleRelation.from_article_id == article_id)
        .order_by(desc(ArticleRelation.score), desc(Article.created_at))
        .limit(limit)
    )
    if relation_type:
        stmt = stmt.where(ArticleRelation.relation_type == relation_type)

    rows = await db.execute(stmt)
    items = []
    for rel, target in rows.all():
        items.append(
            {
                "relation_type": rel.relation_type,
                "score": rel.score,
                "metadata": rel.metadata_json or {},
                "article": ArticleBrief.model_validate(target),
            }
        )
    return items
