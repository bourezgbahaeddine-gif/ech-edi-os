"""Media Intelligence Layer service.

Phase 1 focuses on explainable, rules-based signal generation:
- cluster recent articles into emerging editorial groupings
- normalize/persist entities and co-mention edges
- calculate source trust score foundations
- emit Suggest / Flag / Escalate signals
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import combinations
from statistics import mean
from typing import Any

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.domain.mil import (
    MILPriority,
    MILSignalStatus,
    MILSignalType,
    MILSupportKind,
    MILTargetSurface,
    MILTriageAction,
)
from app.models import (
    Article,
    ArticleEntity,
    ArticleRelation,
    ArticleTopic,
    CompetitorXrayItem,
    EditorialDraft,
    EventMemoItem,
    JobRun,
    MILCluster,
    MILClusterArticle,
    MILEntity,
    MILEntityEdge,
    MILSignal,
    MILSignalSource,
    MILSourceTrustScore,
    NewsStatus,
    ProjectMemoryItem,
    Source,
    Story,
    StoryItem,
)
from app.schemas.mil import (
    MILClusterSummary,
    MILDashboardListItem,
    MILDashboardMetric,
    MILDashboardResponse,
    MILEditorContext,
    MILEventInsights,
    MILEntitySummary,
    MILInsightItem,
    MILSignalDetail,
    MILSignalExplanation,
    MILSignalListItem,
    MILSignalPayload,
    MILSignalSupportItem,
    MILTodayCard,
    MILTodayFullResponse,
    MILTodaySection,
    MILStoryInsights,
)

logger = get_logger("services.mil")

_TOKEN_RE = re.compile(r"[^\w\u0600-\u06FF]+", re.UNICODE)
_STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "from",
    "into",
    "this",
    "على",
    "من",
    "في",
    "إلى",
    "عن",
    "بعد",
    "قبل",
    "بين",
    "حول",
    "هذا",
    "هذه",
    "ذلك",
    "التي",
    "الذي",
    "الى",
}
_USEFUL_STATUSES = {
    NewsStatus.CLASSIFIED.value,
    NewsStatus.CANDIDATE.value,
    NewsStatus.APPROVED.value,
    NewsStatus.APPROVED_HANDOFF.value,
    NewsStatus.DRAFT_GENERATED.value,
    NewsStatus.READY_FOR_CHIEF_APPROVAL.value,
    NewsStatus.APPROVAL_REQUEST_WITH_RESERVATIONS.value,
    NewsStatus.READY_FOR_MANUAL_PUBLISH.value,
    NewsStatus.PUBLISHED.value,
}
_MIL_ELIGIBLE_STATUSES = {
    NewsStatus.NEW.value,
    NewsStatus.CLASSIFIED.value,
    NewsStatus.CANDIDATE.value,
    NewsStatus.APPROVED.value,
    NewsStatus.APPROVED_HANDOFF.value,
    NewsStatus.DRAFT_GENERATED.value,
    NewsStatus.READY_FOR_CHIEF_APPROVAL.value,
    NewsStatus.APPROVAL_REQUEST_WITH_RESERVATIONS.value,
    NewsStatus.READY_FOR_MANUAL_PUBLISH.value,
}


@dataclass
class _EntityMention:
    name: str
    normalized_name: str
    entity_type: str


@dataclass
class _ClusterBucket:
    cluster_key: str
    label: str
    dominant_entity: str | None = None
    article_ids: list[int] = field(default_factory=list)
    source_ids: set[int] = field(default_factory=set)
    source_names: set[str] = field(default_factory=set)
    entity_names: Counter[str] = field(default_factory=Counter)
    local_boost: int = 0
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    representative_title: str | None = None
    confidence_score: float = 0.0
    velocity_score: float = 0.0
    triage_action: MILTriageAction = MILTriageAction.suggest
    priority: MILPriority = MILPriority.low
    target_surface: MILTargetSurface = MILTargetSurface.stories_workspace
    explanation: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    dominant_entity_id: int | None = None


@dataclass
class _SignalCandidate:
    signal_code: str
    signal_type: MILSignalType
    triage_action: MILTriageAction
    priority: MILPriority
    confidence_score: float
    explanation: dict[str, Any]
    payload: dict[str, Any]
    target_surface: MILTargetSurface
    related_entity_id: int | None = None
    related_story_id: int | None = None
    related_event_id: int | None = None
    related_cluster_id: int | None = None
    article_ids: list[int] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)
    competitor_item_ids: list[int] = field(default_factory=list)


class MediaIntelligenceService:
    async def analyze_recent(
        self,
        db: AsyncSession,
        *,
        hours: int = 6,
        max_articles: int = 300,
        include_competitors: bool = False,
        created_from_job_id: str | None = None,
    ) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(hours=max(1, min(hours, 48)))
        articles = await self._fetch_recent_articles(db, cutoff=cutoff, limit=max_articles)
        if not articles:
            return {
                "articles_scanned": 0,
                "clusters_created": 0,
                "signals_created": 0,
                "entities_updated": 0,
                "source_scores_updated": 0,
                "include_competitors": include_competitors,
            }

        article_ids = [article.id for article in articles]
        entities_by_article = await self._load_article_entities(db, article_ids=article_ids, articles=articles)
        source_scores = await self._recalculate_source_trust_scores(db, article_ids=article_ids)
        entity_lookup = await self._upsert_entities_and_edges(db, entities_by_article=entities_by_article)
        topics_by_article = await self._load_article_topics(db, article_ids=article_ids)
        clusters = self._build_clusters(
            articles=articles,
            entities_by_article=entities_by_article,
            source_scores=source_scores,
            entity_lookup=entity_lookup,
            cutoff=cutoff,
        )
        persisted_clusters = await self._upsert_clusters(db, clusters)
        signal_candidates = self._build_cluster_signal_candidates(persisted_clusters)
        signal_candidates.extend(
            await self._build_entity_signal_candidates(
                db,
                articles=articles,
                entities_by_article=entities_by_article,
                entity_lookup=entity_lookup,
                source_scores=source_scores,
                cutoff=cutoff,
            )
        )
        signal_candidates.extend(
            await self._build_story_signal_candidates(
                db,
                articles=articles,
                source_scores=source_scores,
                cutoff=cutoff,
            )
        )
        signal_candidates.extend(
            await self._build_event_signal_candidates(
                db,
                articles=articles,
                cutoff=cutoff,
            )
        )
        signal_candidates.extend(
            await self._build_archive_signal_candidates(
                db,
                articles=articles,
                cutoff=cutoff,
            )
        )
        signal_candidates.extend(
            self._build_risk_signal_candidates(
                articles=articles,
                source_scores=source_scores,
                topics_by_article=topics_by_article,
                cutoff=cutoff,
            )
        )
        if include_competitors:
            signal_candidates.extend(
                await self._build_competitor_signal_candidates(
                    db,
                    articles=articles,
                    cutoff=cutoff,
                )
            )
        signals = await self._upsert_signals(
            db,
            candidates=signal_candidates,
            created_from_job_id=created_from_job_id,
        )
        await db.commit()

        return {
            "articles_scanned": len(articles),
            "clusters_created": len(persisted_clusters),
            "signals_created": len(signals),
            "entities_updated": len(entity_lookup),
            "source_scores_updated": len(source_scores),
            "signal_families": sorted({candidate.signal_type.value for candidate in signal_candidates}),
            "include_competitors": include_competitors,
        }

    async def list_signals(
        self,
        db: AsyncSession,
        *,
        triage_action: str | None = None,
        status: str = MILSignalStatus.active.value,
        limit: int = 50,
    ) -> list[MILSignalListItem]:
        stmt = select(MILSignal).order_by(desc(MILSignal.created_at)).limit(max(1, min(limit, 100)))
        if triage_action:
            stmt = stmt.where(MILSignal.triage_action == triage_action)
        if status:
            stmt = stmt.where(MILSignal.status == status)
        rows = await db.execute(stmt)
        return [self._serialize_signal(signal) for signal in rows.scalars().all()]

    async def get_signal_detail(self, db: AsyncSession, signal_id: int) -> MILSignalDetail | None:
        row = await db.execute(select(MILSignal).where(MILSignal.id == signal_id))
        signal = row.scalar_one_or_none()
        if not signal:
            return None
        support_rows = await db.execute(
            select(MILSignalSource)
            .where(MILSignalSource.signal_id == signal_id)
            .order_by(desc(MILSignalSource.weight), desc(MILSignalSource.created_at))
        )
        return self._serialize_signal_detail(signal, support_rows.scalars().all())

    async def dismiss_signal(
        self,
        db: AsyncSession,
        *,
        signal_id: int,
        dismissed_by: int,
        note: str | None = None,
    ) -> MILSignal | None:
        row = await db.execute(select(MILSignal).where(MILSignal.id == signal_id))
        signal = row.scalar_one_or_none()
        if not signal:
            return None
        signal.status = MILSignalStatus.dismissed.value
        signal.dismissed_at = datetime.utcnow()
        signal.dismissed_by = dismissed_by
        explanation = dict(signal.explanation_json or {})
        if note:
            explanation["dismiss_note"] = note
        signal.explanation_json = explanation
        await db.commit()
        await db.refresh(signal)
        return signal

    async def mark_signal_useful(
        self,
        db: AsyncSession,
        *,
        signal_id: int,
        actor_user_id: int,
    ) -> MILSignal | None:
        row = await db.execute(select(MILSignal).where(MILSignal.id == signal_id))
        signal = row.scalar_one_or_none()
        if not signal:
            return None
        signal.useful_count = int(signal.useful_count or 0) + 1
        signal.useful_last_marked_at = datetime.utcnow()
        signal.useful_last_marked_by = actor_user_id
        await db.commit()
        await db.refresh(signal)
        return signal

    async def snooze_signal(
        self,
        db: AsyncSession,
        *,
        signal_id: int,
        hours: int,
    ) -> MILSignal | None:
        row = await db.execute(select(MILSignal).where(MILSignal.id == signal_id))
        signal = row.scalar_one_or_none()
        if not signal:
            return None
        signal.snoozed_until = datetime.utcnow() + timedelta(hours=max(1, min(hours, 72)))
        await db.commit()
        await db.refresh(signal)
        return signal

    async def list_today_escalations(self, db: AsyncSession, *, limit: int = 4) -> list[MILTodayCard]:
        rows = await db.execute(
            select(MILSignal)
            .where(
                MILSignal.status == MILSignalStatus.active.value,
                MILSignal.triage_action == MILTriageAction.escalate.value,
                MILSignal.target_surface == MILTargetSurface.today_orchestration.value,
                (MILSignal.snoozed_until.is_(None) | (MILSignal.snoozed_until < datetime.utcnow())),
            )
            .order_by(desc(MILSignal.confidence_score), desc(MILSignal.created_at))
            .limit(max(1, min(limit, 12)))
        )
        return [self._serialize_today_card(signal) for signal in rows.scalars().all()]

    async def get_today_full(self, db: AsyncSession, *, limit_per_section: int = 4) -> MILTodayFullResponse:
        limit_per_section = max(1, min(limit_per_section, 8))
        rows = await db.execute(
            select(MILSignal)
            .where(
                MILSignal.status == MILSignalStatus.active.value,
                (MILSignal.snoozed_until.is_(None) | (MILSignal.snoozed_until < datetime.utcnow())),
            )
            .order_by(desc(MILSignal.confidence_score), desc(MILSignal.created_at))
            .limit(limit_per_section * 8)
        )
        signals = rows.scalars().all()
        critical = [self._serialize_today_card(signal) for signal in signals if signal.triage_action == MILTriageAction.escalate.value][:limit_per_section]
        watch = [self._serialize_today_card(signal) for signal in signals if signal.triage_action == MILTriageAction.flag.value][:limit_per_section]
        opportunities = [self._serialize_today_card(signal) for signal in signals if signal.triage_action == MILTriageAction.suggest.value][:limit_per_section]
        return MILTodayFullResponse(
            generated_at=datetime.utcnow(),
            critical_now=MILTodaySection(
                key="critical_now",
                title="حرج الآن",
                hint="أقوى إشارات MIL التي تستحق فتح مسار تحريري أو تغطية فورية.",
                items=critical,
            ),
            watch_closely=MILTodaySection(
                key="watch_closely",
                title="تحت المراقبة",
                hint="إشارات قوية لم تصل بعد إلى مستوى التصعيد الكامل.",
                items=watch,
            ),
            opportunities=MILTodaySection(
                key="opportunities",
                title="فرص واعدة",
                hint="اقتراحات قابلة للتحول إلى زوايا أو قصص إذا التقطناها مبكرًا.",
                items=opportunities,
            ),
        )

    async def get_dashboard(self, db: AsyncSession) -> MILDashboardResponse:
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)
        signals_rows = await db.execute(
            select(MILSignal).where(MILSignal.created_at >= day_ago).order_by(desc(MILSignal.confidence_score), desc(MILSignal.created_at))
        )
        signals = signals_rows.scalars().all()
        clusters = await self.list_clusters(db, limit=10)
        trust_rows = await db.execute(
            select(MILSourceTrustScore, Source)
            .join(Source, Source.id == MILSourceTrustScore.source_id)
            .order_by(MILSourceTrustScore.score.asc(), desc(Source.priority))
            .limit(6)
        )
        competitor_rows = await db.execute(
            select(CompetitorXrayItem)
            .where(
                CompetitorXrayItem.created_at >= day_ago,
                CompetitorXrayItem.status == "new",
                CompetitorXrayItem.matched_article_id.is_(None),
            )
            .order_by(desc(CompetitorXrayItem.priority_score), desc(CompetitorXrayItem.created_at))
            .limit(8)
        )
        metrics = [
            MILDashboardMetric(key="signals_24h", label="إشارات اليوم", value=len(signals), hint="كل ما التقطه MIL خلال آخر 24 ساعة."),
            MILDashboardMetric(
                key="escalations_24h",
                label="تصعيدات حرجة",
                value=sum(1 for signal in signals if signal.triage_action == MILTriageAction.escalate.value),
                hint="الإشارات التي وصلت إلى مستوى التصعيد.",
                tone="danger",
            ),
            MILDashboardMetric(
                key="competitor_pressure",
                label="ضغط المنافسين",
                value=sum(1 for item in competitor_rows.scalars().all()),
                hint="عناصر منافسين جديدة لم تُطابق بعد مع تغطيتنا.",
                tone="warn",
            ),
        ]
        competitor_rows = await db.execute(
            select(CompetitorXrayItem)
            .where(
                CompetitorXrayItem.created_at >= day_ago,
                CompetitorXrayItem.status == "new",
                CompetitorXrayItem.matched_article_id.is_(None),
            )
            .order_by(desc(CompetitorXrayItem.priority_score), desc(CompetitorXrayItem.created_at))
            .limit(8)
        )
        return MILDashboardResponse(
            generated_at=now,
            metrics=metrics,
            rising_stories=[
                MILDashboardListItem(
                    title=cluster.label,
                    subtitle=cluster.dominant_entity,
                    hint=f"{cluster.article_count} مادة · {cluster.source_diversity_count} مصدر · سرعة {cluster.velocity_score:.1f}",
                    href=f"/stories",
                    confidence_score=cluster.confidence_score,
                )
                for cluster in clusters[:5]
            ],
            missed_opportunities=[
                MILDashboardListItem(
                    title=(signal.payload_json or {}).get("title") or signal.signal_code,
                    subtitle=signal.signal_type,
                    hint=(signal.explanation_json or {}).get("human_summary") or "",
                    href=self._resolve_signal_href(signal),
                    confidence_score=float(signal.confidence_score or 0.0),
                )
                for signal in signals
                if signal.triage_action in {MILTriageAction.flag.value, MILTriageAction.suggest.value}
            ][:5],
            competitor_pressure=[
                MILDashboardListItem(
                    title=item.competitor_title,
                    subtitle=f"ضغط منافس {item.priority_score:.2f}",
                    hint=item.angle_rationale or item.competitor_summary or "قصة منافس صاعدة بلا تطابق داخلي واضح.",
                    href="/competitor-xray",
                    confidence_score=float(item.priority_score or 0.0),
                )
                for item in competitor_rows.scalars().all()
            ],
            source_trust_watch=[
                MILDashboardListItem(
                    title=source.name,
                    subtitle=f"درجة الثقة {score.score:.2f}",
                    hint=f"عوائد مفيدة: {(score.score_components_json or {}).get('useful_yield_ratio', 0)}",
                    href="/sources",
                    confidence_score=float(score.score or 0.0),
                )
                for score, source in trust_rows.all()
            ],
        )

    async def list_entities(self, db: AsyncSession, *, limit: int = 50) -> list[MILEntitySummary]:
        rows = await db.execute(
            select(MILEntity)
            .order_by(desc(MILEntity.mention_count), desc(MILEntity.last_seen_at))
            .limit(max(1, min(limit, 100)))
        )
        return [MILEntitySummary.model_validate(entity) for entity in rows.scalars().all()]

    async def list_clusters(self, db: AsyncSession, *, limit: int = 30) -> list[MILClusterSummary]:
        rows = await db.execute(
            select(MILCluster)
            .order_by(desc(MILCluster.velocity_score), desc(MILCluster.last_seen_at))
            .limit(max(1, min(limit, 100)))
        )
        return [MILClusterSummary.model_validate(cluster) for cluster in rows.scalars().all()]

    async def get_story_insights(self, db: AsyncSession, *, story_id: int) -> MILStoryInsights | None:
        story_row = await db.execute(select(Story).where(Story.id == story_id))
        story = story_row.scalar_one_or_none()
        if not story:
            return None
        article_rows = await db.execute(
            select(Article)
            .join(StoryItem, StoryItem.article_id == Article.id)
            .where(StoryItem.story_id == story_id, StoryItem.article_id.is_not(None))
            .order_by(desc(func.coalesce(Article.published_at, Article.crawled_at, Article.created_at)))
        )
        articles = article_rows.scalars().all()
        now = datetime.utcnow()
        last_24 = [article for article in articles if (article.published_at or article.crawled_at or article.created_at) >= now - timedelta(hours=24)]
        prev_48 = [
            article
            for article in articles
            if now - timedelta(hours=72) <= (article.published_at or article.crawled_at or article.created_at) < now - timedelta(hours=24)
        ]
        momentum = "صاعدة" if len(last_24) > max(1, len(prev_48)) else "تتراجع" if len(last_24) == 0 and prev_48 else "مستقرة"

        story_tokens = set(self._tokenize(story.title))
        competitor_rows = await db.execute(
            select(CompetitorXrayItem)
            .where(CompetitorXrayItem.created_at >= now - timedelta(hours=72))
            .order_by(desc(CompetitorXrayItem.priority_score), desc(CompetitorXrayItem.created_at))
        )
        competitor_hits = [
            item
            for item in competitor_rows.scalars().all()
            if story_tokens.intersection(self._tokenize(item.competitor_title))
        ]

        article_ids = [article.id for article in articles]
        archive_rows = []
        entity_names: list[str] = []
        if article_ids:
            relations = await db.execute(
                select(ArticleRelation, Article)
                .join(Article, Article.id == ArticleRelation.to_article_id)
                .where(
                    ArticleRelation.from_article_id.in_(article_ids),
                    ArticleRelation.relation_type.in_(["related", "impact", "sequence"]),
                )
                .order_by(desc(ArticleRelation.score))
                .limit(6)
            )
            archive_rows = relations.all()
            entities = await db.execute(
                select(ArticleEntity.entity, func.count(ArticleEntity.id).label("c"))
                .where(ArticleEntity.article_id.in_(article_ids))
                .group_by(ArticleEntity.entity)
                .order_by(desc("c"))
                .limit(8)
            )
            entity_names = [row[0] for row in entities.all()]

        cards: list[MILInsightItem] = []
        if len(last_24) > max(1, len(prev_48)):
            cards.append(
                MILInsightItem(
                    title="قصة ترتفع زخمًا",
                    summary=f"سجّلنا {len(last_24)} مادة خلال آخر 24 ساعة مقابل {len(prev_48)} في النافذة السابقة.",
                    tone="success",
                    confidence_score=0.76,
                    href=f"/stories?story_id={story_id}",
                )
            )
        if competitor_hits:
            cards.append(
                MILInsightItem(
                    title="ضغط المنافسين",
                    summary=f"رُصد {len(competitor_hits)} تحرك منافس حول نفس المسار خلال 72 ساعة.",
                    tone="warn",
                    confidence_score=min(0.95, round(0.58 + min(len(competitor_hits), 4) * 0.08, 3)),
                    href="/competitor-xray",
                )
            )
        if archive_rows:
            cards.append(
                MILInsightItem(
                    title="زاوية أرشيفية جاهزة",
                    summary=f"يوجد {len(archive_rows)} رابط أرشيفي يمكن تحويله إلى خلفية أو سياق متقدم.",
                    tone="default",
                    confidence_score=0.71,
                    href=f"/archive",
                )
            )

        follow_up_angle = None
        if competitor_hits:
            follow_up_angle = "وسّع القصة بزوايا المتابعة التي ظهر أن المنافسين يختبرونها الآن."
        elif archive_rows:
            follow_up_angle = "حوّل الروابط الأرشيفية إلى خلفية تفسيرية أو زاوية متابعة."
        elif momentum == "تتراجع":
            follow_up_angle = "القصة فقدت الزخم؛ جرّب زاوية بشرية أو تفسيرية بدل المتابعة الإخبارية المباشرة."

        archive_angle = archive_rows[0][1].title_ar or archive_rows[0][1].original_title if archive_rows else None
        return MILStoryInsights(
            story_id=story.id,
            story_title=story.title,
            momentum=momentum,
            competitor_pressure="مرتفع" if len(competitor_hits) >= 3 else "متوسط" if competitor_hits else "منخفض",
            archive_angle=archive_angle,
            follow_up_angle=follow_up_angle,
            linked_entities=entity_names,
            cards=cards,
        )

    async def get_event_insights(self, db: AsyncSession, *, event_id: int) -> MILEventInsights | None:
        event_row = await db.execute(select(EventMemoItem).where(EventMemoItem.id == event_id))
        event = event_row.scalar_one_or_none()
        if not event:
            return None
        article_rows = await db.execute(
            select(Article)
            .where(func.coalesce(Article.published_at, Article.crawled_at, Article.created_at) >= datetime.utcnow() - timedelta(hours=72))
            .order_by(desc(func.coalesce(Article.published_at, Article.crawled_at, Article.created_at)))
            .limit(200)
        )
        tokens = set(self._tokenize(event.title) + [self._normalize_name(tag) for tag in (event.tags or []) if self._normalize_name(tag)])
        matched_articles = [
            article
            for article in article_rows.scalars().all()
            if tokens.intersection(self._tokenize(article.title_ar or article.original_title or ""))
        ]
        recent_24 = [article for article in matched_articles if (article.published_at or article.crawled_at or article.created_at) >= datetime.utcnow() - timedelta(hours=24)]
        prior_24 = [
            article
            for article in matched_articles
            if datetime.utcnow() - timedelta(hours=48) <= (article.published_at or article.crawled_at or article.created_at) < datetime.utcnow() - timedelta(hours=24)
        ]
        local_sources = {
            (article.source_name or "").strip()
            for article in matched_articles
            if (article.source_name or "").strip()
            and any(marker in (article.source_name or "").lower() for marker in ("alg", "dz", "ال", "echorouk"))
        }
        cards: list[MILInsightItem] = []
        if len(recent_24) > len(prior_24):
            cards.append(
                MILInsightItem(
                    title="تصاعد ما قبل الحدث",
                    summary=f"التغطية ارتفعت إلى {len(recent_24)} مادة خلال 24 ساعة.",
                    tone="warn",
                    confidence_score=min(0.95, round(0.55 + min(len(recent_24), 5) * 0.07, 3)),
                    href=f"/events?event_id={event.id}",
                )
            )
        if local_sources:
            cards.append(
                MILInsightItem(
                    title="انتشار محلي",
                    summary=f"بدأت {len(local_sources)} جهة/منصة محلية في الالتقاط المبكر للحدث.",
                    tone="default",
                    confidence_score=0.68,
                    href="/news",
                )
            )
        return MILEventInsights(
            event_id=event.id,
            event_title=event.title,
            attention_level="مرتفع" if len(recent_24) >= 4 else "متوسط" if len(recent_24) >= 2 else "منخفض",
            geographic_spread="محلي" if local_sources else "غير واضح",
            social_relevance="مرتفع" if len(recent_24) >= 4 else "قيد التشكل",
            coverage_risk="خطر تفويت" if len(recent_24) >= 3 and event.readiness_status in {"idea", "assigned"} else "تحت السيطرة",
            suggested_pack=[
                "خلفية سريعة",
                "سيرة الأطراف الرئيسية",
                "خط أسئلة المتابعة",
            ],
            cards=cards,
        )

    async def get_editor_context(
        self,
        db: AsyncSession,
        *,
        draft_id: int | None = None,
        work_id: str | None = None,
    ) -> MILEditorContext | None:
        stmt = select(EditorialDraft)
        if draft_id is not None:
            stmt = stmt.where(EditorialDraft.id == draft_id)
        elif work_id:
            stmt = stmt.where(EditorialDraft.work_id == work_id).order_by(desc(EditorialDraft.version))
        else:
            return None
        row = await db.execute(stmt.limit(1))
        draft = row.scalar_one_or_none()
        if not draft:
            return None

        related_signals: list[MILSignalListItem] = []
        if draft.article_id:
            signal_rows = await db.execute(
                select(MILSignal)
                .join(MILSignalSource, MILSignalSource.signal_id == MILSignal.id)
                .where(
                    MILSignal.status == MILSignalStatus.active.value,
                    MILSignalSource.article_id == draft.article_id,
                )
                .order_by(desc(MILSignal.confidence_score), desc(MILSignal.created_at))
                .limit(6)
            )
            related_signals = [self._serialize_signal(signal) for signal in signal_rows.scalars().unique().all()]

        archive_links: list[MILInsightItem] = []
        related_entities: list[str] = []
        if draft.article_id:
            rel_rows = await db.execute(
                select(ArticleRelation, Article)
                .join(Article, Article.id == ArticleRelation.to_article_id)
                .where(
                    ArticleRelation.from_article_id == draft.article_id,
                    ArticleRelation.relation_type.in_(["related", "impact", "sequence"]),
                )
                .order_by(desc(ArticleRelation.score))
                .limit(5)
            )
            archive_links = [
                MILInsightItem(
                    title=(article.title_ar or article.original_title or f"مادة #{article.id}")[:180],
                    summary=f"صلة أرشيفية ({relation.relation_type}) بدرجة {relation.score:.2f}.",
                    href=f"/news/{article.id}",
                    confidence_score=float(relation.score or 0.0),
                )
                for relation, article in rel_rows.all()
            ]
            entity_rows = await db.execute(
                select(ArticleEntity.entity)
                .where(ArticleEntity.article_id == draft.article_id)
                .order_by(ArticleEntity.confidence.desc())
                .limit(8)
            )
            related_entities = [value for value in entity_rows.scalars().all()]

        competitor_angles: list[MILInsightItem] = []
        if draft.title:
            tokens = set(self._tokenize(draft.title))
            competitor_rows = await db.execute(
                select(CompetitorXrayItem)
                .where(CompetitorXrayItem.created_at >= datetime.utcnow() - timedelta(hours=72))
                .order_by(desc(CompetitorXrayItem.priority_score), desc(CompetitorXrayItem.created_at))
                .limit(20)
            )
            competitor_angles = [
                MILInsightItem(
                    title=item.competitor_title[:180],
                    summary=item.angle_rationale or item.competitor_summary or "زاوية منافس يمكن استثمارها أو الرد عليها.",
                    href="/competitor-xray",
                    confidence_score=float(item.priority_score or 0.0),
                    tone="warn",
                )
                for item in competitor_rows.scalars().all()
                if tokens.intersection(self._tokenize(item.competitor_title))
            ][:4]

        missing_angles = []
        for signal in related_signals:
            if signal.signal_type in {MILSignalType.archive_relevance_found, MILSignalType.newsroom_missing_angle, MILSignalType.story_needs_followup}:
                missing_angles.append(
                    MILInsightItem(
                        title=signal.payload.title,
                        summary=signal.explanation.human_summary,
                        href=self._resolve_signal_href_from_item(signal),
                        confidence_score=signal.confidence_score,
                    )
                )

        return MILEditorContext(
            draft_id=draft.id,
            article_id=draft.article_id,
            work_id=draft.work_id,
            live_signals=related_signals,
            archive_links=archive_links,
            missing_angles=missing_angles,
            related_entities=related_entities,
            competitor_angles=competitor_angles,
        )

    async def _fetch_recent_articles(self, db: AsyncSession, *, cutoff: datetime, limit: int) -> list[Article]:
        rows = await db.execute(
            select(Article)
            .where(
                func.coalesce(Article.published_at, Article.crawled_at, Article.created_at) >= cutoff,
                Article.status.in_(_MIL_ELIGIBLE_STATUSES),
            )
            .order_by(desc(func.coalesce(Article.published_at, Article.crawled_at, Article.created_at)))
            .limit(max(25, min(limit, 1000)))
        )
        return list(rows.scalars().all())

    async def _load_article_entities(
        self,
        db: AsyncSession,
        *,
        article_ids: list[int],
        articles: list[Article],
    ) -> dict[int, list[_EntityMention]]:
        by_article: dict[int, list[_EntityMention]] = defaultdict(list)
        rows = await db.execute(select(ArticleEntity).where(ArticleEntity.article_id.in_(article_ids)))
        for row in rows.scalars().all():
            normalized = self._normalize_name(row.entity)
            if not normalized:
                continue
            by_article[row.article_id].append(
                _EntityMention(
                    name=row.entity.strip(),
                    normalized_name=normalized,
                    entity_type=(row.entity_type or "topic").strip().lower(),
                )
            )
        for article in articles:
            raw_entities = article.entities or []
            for raw in raw_entities:
                text = str(raw or "").strip()
                normalized = self._normalize_name(text)
                if not normalized:
                    continue
                if normalized in {entity.normalized_name for entity in by_article[article.id]}:
                    continue
                by_article[article.id].append(
                    _EntityMention(
                        name=text,
                        normalized_name=normalized,
                        entity_type="topic",
                    )
                )
        return by_article

    async def _load_article_topics(self, db: AsyncSession, *, article_ids: list[int]) -> dict[int, list[str]]:
        rows = await db.execute(select(ArticleTopic).where(ArticleTopic.article_id.in_(article_ids)))
        by_article: dict[int, list[str]] = defaultdict(list)
        for row in rows.scalars().all():
            topic = (row.topic or "").strip()
            if topic:
                by_article[row.article_id].append(topic)
        return by_article

    async def _recalculate_source_trust_scores(self, db: AsyncSession, *, article_ids: list[int]) -> dict[int, float]:
        source_ids_rows = await db.execute(
            select(Article.source_id).where(Article.id.in_(article_ids), Article.source_id.is_not(None))
        )
        source_ids = [int(source_id) for source_id in source_ids_rows.scalars().all() if source_id is not None]
        if not source_ids:
            return {}

        cutoff = datetime.utcnow() - timedelta(days=7)
        stats_rows = await db.execute(
            select(
                Article.source_id,
                func.count(Article.id).label("total_count"),
                func.sum(case((Article.status.in_(_USEFUL_STATUSES), 1), else_=0)).label("useful_count"),
                func.max(func.coalesce(Article.published_at, Article.crawled_at, Article.created_at)).label("last_seen_at"),
            )
            .where(
                Article.source_id.in_(source_ids),
                func.coalesce(Article.published_at, Article.crawled_at, Article.created_at) >= cutoff,
            )
            .group_by(Article.source_id)
        )
        source_rows = await db.execute(select(Source).where(Source.id.in_(source_ids)))
        source_lookup = {source.id: source for source in source_rows.scalars().all()}

        existing_rows = await db.execute(select(MILSourceTrustScore).where(MILSourceTrustScore.source_id.in_(source_ids)))
        existing_lookup = {row.source_id: row for row in existing_rows.scalars().all()}

        calculated: dict[int, float] = {}
        for source_id, total_count, useful_count, last_seen_at in stats_rows.all():
            if source_id is None:
                continue
            source = source_lookup.get(int(source_id))
            if not source:
                continue
            baseline = float(source.trust_score or 0.5)
            total = int(total_count or 0)
            useful = int(useful_count or 0)
            useful_ratio = useful / total if total else 0.0
            volume_score = min(1.0, total / 25.0)
            freshness_score = 1.0 if last_seen_at and (datetime.utcnow() - last_seen_at) <= timedelta(days=1) else 0.4
            score = round(
                min(
                    1.0,
                    max(
                        0.05,
                        (baseline * 0.45)
                        + (useful_ratio * 0.35)
                        + (volume_score * 0.1)
                        + (freshness_score * 0.1),
                    ),
                ),
                3,
            )
            payload = {
                "baseline_trust": round(baseline, 3),
                "recent_article_count": total,
                "useful_yield_ratio": round(useful_ratio, 3),
                "volume_score": round(volume_score, 3),
                "freshness_score": round(freshness_score, 3),
            }
            row = existing_lookup.get(int(source_id))
            if row:
                row.score = score
                row.score_components_json = payload
                row.last_calculated_at = datetime.utcnow()
            else:
                db.add(
                    MILSourceTrustScore(
                        source_id=int(source_id),
                        score=score,
                        score_components_json=payload,
                        last_calculated_at=datetime.utcnow(),
                    )
                )
            calculated[int(source_id)] = score
        await db.flush()
        return calculated

    async def _upsert_entities_and_edges(
        self,
        db: AsyncSession,
        *,
        entities_by_article: dict[int, list[_EntityMention]],
    ) -> dict[str, int]:
        mention_index: dict[tuple[str, str], dict[str, Any]] = {}
        for article_entities in entities_by_article.values():
            for entity in article_entities:
                key = (entity.normalized_name, entity.entity_type)
                bucket = mention_index.setdefault(
                    key,
                    {
                        "name": entity.name,
                        "normalized_name": entity.normalized_name,
                        "entity_type": entity.entity_type,
                        "count": 0,
                        "aliases": set(),
                    },
                )
                bucket["count"] += 1
                bucket["aliases"].add(entity.name)

        if not mention_index:
            return {}

        normalized_names = [key[0] for key in mention_index.keys()]
        entity_types = [key[1] for key in mention_index.keys()]
        rows = await db.execute(
            select(MILEntity).where(
                MILEntity.normalized_name.in_(normalized_names),
                MILEntity.entity_type.in_(entity_types),
            )
        )
        existing_lookup = {
            (row.normalized_name, row.entity_type): row for row in rows.scalars().all()
        }

        entity_id_lookup: dict[str, int] = {}
        for key, bucket in mention_index.items():
            row = existing_lookup.get(key)
            if row:
                aliases = set(row.aliases_json or [])
                aliases.update(bucket["aliases"])
                row.entity_name = bucket["name"]
                row.aliases_json = sorted(aliases)[:20]
                row.mention_count = int(row.mention_count or 0) + int(bucket["count"])
                row.last_seen_at = datetime.utcnow()
                row.trust_context_json = {
                    **(row.trust_context_json or {}),
                    "last_refresh_source": "mil_phase1",
                }
            else:
                row = MILEntity(
                    entity_name=bucket["name"],
                    normalized_name=bucket["normalized_name"],
                    entity_type=bucket["entity_type"],
                    aliases_json=sorted(bucket["aliases"])[:20],
                    first_seen_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    mention_count=int(bucket["count"]),
                    trust_context_json={"last_refresh_source": "mil_phase1"},
                )
                db.add(row)
                await db.flush()
                existing_lookup[key] = row
            entity_id_lookup[f"{key[1]}::{key[0]}"] = int(row.id)

        edge_counts: Counter[tuple[int, int, str]] = Counter()
        for article_entities in entities_by_article.values():
            entity_ids = []
            for entity in article_entities[:6]:
                entity_id = entity_id_lookup.get(f"{entity.entity_type}::{entity.normalized_name}")
                if entity_id:
                    entity_ids.append(entity_id)
            for source_entity_id, target_entity_id in combinations(sorted(set(entity_ids)), 2):
                edge_counts[(source_entity_id, target_entity_id, "co_mentioned")] += 1

        if edge_counts:
            edge_rows = await db.execute(
                select(MILEntityEdge).where(
                    MILEntityEdge.source_entity_id.in_([edge[0] for edge in edge_counts.keys()]),
                    MILEntityEdge.target_entity_id.in_([edge[1] for edge in edge_counts.keys()]),
                    MILEntityEdge.edge_type == "co_mentioned",
                )
            )
            existing_edges = {
                (row.source_entity_id, row.target_entity_id, row.edge_type): row for row in edge_rows.scalars().all()
            }
            for edge_key, evidence_count in edge_counts.items():
                row = existing_edges.get(edge_key)
                if row:
                    row.evidence_count = int(row.evidence_count or 0) + int(evidence_count)
                    row.weight = round(float(row.weight or 0.0) + float(evidence_count), 3)
                    row.last_seen_at = datetime.utcnow()
                else:
                    db.add(
                        MILEntityEdge(
                            source_entity_id=edge_key[0],
                            target_entity_id=edge_key[1],
                            edge_type=edge_key[2],
                            weight=float(evidence_count),
                            first_seen_at=datetime.utcnow(),
                            last_seen_at=datetime.utcnow(),
                            evidence_count=int(evidence_count),
                        )
                    )
        await db.flush()
        return entity_id_lookup

    def _build_cluster_signal_candidates(self, clusters: list[_ClusterBucket]) -> list[_SignalCandidate]:
        candidates: list[_SignalCandidate] = []
        for cluster in clusters:
            candidates.append(
                _SignalCandidate(
                    signal_code=f"MIL-{cluster.cluster_key.upper()}",
                    signal_type=MILSignalType.cluster_growth,
                    triage_action=cluster.triage_action,
                    priority=cluster.priority,
                    confidence_score=cluster.confidence_score,
                    explanation=dict(cluster.explanation),
                    payload=dict(cluster.payload),
                    target_surface=cluster.target_surface,
                    related_entity_id=cluster.dominant_entity_id,
                    related_cluster_id=cluster.payload.get("cluster_id"),
                    article_ids=cluster.article_ids[:8],
                    source_ids=sorted(cluster.source_ids),
                )
            )
            if cluster.triage_action != MILTriageAction.suggest and cluster.payload.get("source_count", 0) >= 2:
                confirmation_confidence = min(0.98, round(cluster.confidence_score + 0.04, 3))
                candidates.append(
                    _SignalCandidate(
                        signal_code=f"MIL-CONF-{cluster.cluster_key.upper()}",
                        signal_type=MILSignalType.multi_source_confirmation,
                        triage_action=cluster.triage_action,
                        priority=MILPriority.medium if cluster.triage_action == MILTriageAction.flag else MILPriority.high,
                        confidence_score=confirmation_confidence,
                        explanation={
                            "reason_codes": ["MULTI_SOURCE_CONFIRMATION", "CLUSTER_GROWTH"],
                            "human_summary": f"هذا المسار حظي بتأكيد من {cluster.payload.get('source_count', 0)} مصادر، ما يرفعه من مجرد رصد إلى تأكيد عملي.",
                            "metrics": {
                                "source_diversity_count": cluster.payload.get("source_count", 0),
                                "article_count": len(cluster.article_ids),
                            },
                        },
                        payload={
                            **dict(cluster.payload),
                            "recommended_action": "استثمر هذا التأكيد متعدد المصادر لفتح متابعة أكثر ثقة أو رفعه إلى مكتب القرار.",
                        },
                        target_surface=cluster.target_surface,
                        related_entity_id=cluster.dominant_entity_id,
                        related_cluster_id=cluster.payload.get("cluster_id"),
                        article_ids=cluster.article_ids[:8],
                        source_ids=sorted(cluster.source_ids),
                    )
                )
        return candidates

    async def _build_entity_signal_candidates(
        self,
        db: AsyncSession,
        *,
        articles: list[Article],
        entities_by_article: dict[int, list[_EntityMention]],
        entity_lookup: dict[str, int],
        source_scores: dict[int, float],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        previous_cutoff = cutoff - (datetime.utcnow() - cutoff)
        recent_counter: Counter[tuple[str, str]] = Counter()
        recent_source_names: dict[tuple[str, str], set[str]] = defaultdict(set)
        recent_article_ids: dict[tuple[str, str], list[int]] = defaultdict(list)
        article_lookup = {article.id: article for article in articles}

        for article_id, mentions in entities_by_article.items():
            article = article_lookup.get(article_id)
            if not article:
                continue
            for entity in mentions[:6]:
                key = (entity.normalized_name, entity.entity_type)
                recent_counter[key] += 1
                if article.source_name:
                    recent_source_names[key].add(article.source_name)
                recent_article_ids[key].append(article_id)

        previous_rows = await db.execute(
            select(ArticleEntity.entity, ArticleEntity.entity_type, func.count(ArticleEntity.id).label("c"))
            .join(Article, Article.id == ArticleEntity.article_id)
            .where(
                func.coalesce(Article.published_at, Article.crawled_at, Article.created_at) >= previous_cutoff,
                func.coalesce(Article.published_at, Article.crawled_at, Article.created_at) < cutoff,
            )
            .group_by(ArticleEntity.entity, ArticleEntity.entity_type)
        )
        previous_lookup = {
            (self._normalize_name(name), (entity_type or "topic").strip().lower()): int(count or 0)
            for name, entity_type, count in previous_rows.all()
            if self._normalize_name(name)
        }

        candidates: list[_SignalCandidate] = []
        for (normalized_name, entity_type), recent_count in recent_counter.items():
            if recent_count < 3:
                continue
            previous_count = previous_lookup.get((normalized_name, entity_type), 0)
            source_diversity = len(recent_source_names[(normalized_name, entity_type)])
            velocity_gain = recent_count - previous_count
            confidence = min(
                0.97,
                round(
                    0.46
                    + (min(recent_count, 6) * 0.06)
                    + (min(source_diversity, 4) * 0.08)
                    + (0.08 if velocity_gain >= 2 else 0.0),
                    3,
                ),
            )
            triage = MILTriageAction.flag if source_diversity >= 2 else MILTriageAction.suggest
            if recent_count >= 5 and source_diversity >= 3 and confidence >= 0.8:
                triage = MILTriageAction.escalate
            entity_name = next(
                (
                    mention.name
                    for mention_list in entities_by_article.values()
                    for mention in mention_list
                    if mention.normalized_name == normalized_name and mention.entity_type == entity_type
                ),
                normalized_name,
            )
            entity_id = entity_lookup.get(f"{entity_type}::{normalized_name}")
            signal_type = MILSignalType.mention_spike if velocity_gain >= 2 else MILSignalType.repeated_entity_burst
            target_surface = MILTargetSurface.today_orchestration if triage == MILTriageAction.escalate else MILTargetSurface.editorial_sidebar
            candidates.append(
                _SignalCandidate(
                    signal_code=f"MIL-ENT-{hashlib.sha1(f'{entity_type}:{normalized_name}'.encode('utf-8')).hexdigest()[:16].upper()}",
                    signal_type=signal_type,
                    triage_action=triage,
                    priority=MILPriority.high if triage == MILTriageAction.escalate else MILPriority.medium if triage == MILTriageAction.flag else MILPriority.low,
                    confidence_score=confidence,
                    explanation={
                        "reason_codes": ["MENTION_SPIKE" if signal_type == MILSignalType.mention_spike else "REPEATED_ENTITY_BURST", "SOURCE_DIVERSITY"],
                        "human_summary": f"الكيان {entity_name} ارتفع حضوره إلى {recent_count} ذكرًا حديثًا عبر {source_diversity} مصادر، مقابل {previous_count} في النافذة السابقة.",
                        "metrics": {
                            "recent_mentions": recent_count,
                            "previous_mentions": previous_count,
                            "source_diversity_count": source_diversity,
                        },
                    },
                    payload={
                        "title": f"{entity_name}: مسار صاعد",
                        "entity": entity_name,
                        "event_summary": f"تصاعد حضور {entity_name} في التغطية الحديثة.",
                        "related_sources": sorted(recent_source_names[(normalized_name, entity_type)])[:8],
                        "related_article_ids": recent_article_ids[(normalized_name, entity_type)][:8],
                        "source_count": source_diversity,
                        "cluster_id": None,
                        "action_suggested": triage.value,
                        "target_surface": target_surface.value,
                        "recommended_action": "راجع ما إذا كان هذا التصاعد يستحق متابعة مستقلة أو ربطه بقصة قائمة.",
                        "metadata": {"previous_mentions": previous_count},
                    },
                    target_surface=target_surface,
                    related_entity_id=entity_id,
                    article_ids=recent_article_ids[(normalized_name, entity_type)][:8],
                    source_ids=[
                        int(article.source_id)
                        for article in articles
                        if article.id in recent_article_ids[(normalized_name, entity_type)] and article.source_id
                    ],
                )
            )
        return candidates

    async def _build_story_signal_candidates(
        self,
        db: AsyncSession,
        *,
        articles: list[Article],
        source_scores: dict[int, float],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        story_rows = await db.execute(select(Story).where(Story.status.in_(["open", "monitoring"])).order_by(desc(Story.updated_at)).limit(30))
        stories = story_rows.scalars().all()
        candidates: list[_SignalCandidate] = []
        now = datetime.utcnow()
        for story in stories:
            article_rows = await db.execute(
                select(Article)
                .join(StoryItem, StoryItem.article_id == Article.id)
                .where(StoryItem.story_id == story.id, StoryItem.article_id.is_not(None))
            )
            story_articles = article_rows.scalars().all()
            if not story_articles:
                continue
            recent = [article for article in story_articles if (article.published_at or article.crawled_at or article.created_at) >= now - timedelta(hours=24)]
            older = [
                article
                for article in story_articles
                if now - timedelta(hours=72) <= (article.published_at or article.crawled_at or article.created_at) < now - timedelta(hours=24)
            ]
            if len(recent) >= 3 and len(recent) > len(older):
                confidence = min(0.96, round(0.55 + min(len(recent), 5) * 0.07, 3))
                candidates.append(
                    _SignalCandidate(
                        signal_code=f"MIL-STORY-UP-{story.id}",
                        signal_type=MILSignalType.story_momentum_up,
                        triage_action=MILTriageAction.flag if len(recent) < 5 else MILTriageAction.escalate,
                        priority=MILPriority.medium if len(recent) < 5 else MILPriority.high,
                        confidence_score=confidence,
                        explanation={
                            "reason_codes": ["STORY_MOMENTUM_UP", "RECENCY_WINDOW"],
                            "human_summary": f"قصة {story.title} استعادت الزخم: {len(recent)} مادة خلال 24 ساعة مقابل {len(older)} قبلها.",
                            "metrics": {"recent_count": len(recent), "previous_count": len(older)},
                        },
                        payload={
                            "title": f"قصة تصعد: {story.title}",
                            "entity": None,
                            "event_summary": "القصة تشهد موجة تغطية جديدة وتستحق متابعة أعلى.",
                            "related_sources": sorted({article.source_name for article in recent if article.source_name})[:8],
                            "related_article_ids": [article.id for article in recent[:8]],
                            "source_count": len({article.source_name for article in recent if article.source_name}),
                            "cluster_id": None,
                            "action_suggested": (MILTriageAction.flag if len(recent) < 5 else MILTriageAction.escalate).value,
                            "target_surface": MILTargetSurface.stories_workspace.value,
                            "recommended_action": "افتح ملف القصة وحدد زاوية المتابعة التالية قبل أن يسبقك المنافس.",
                            "metadata": {"story_id": story.id},
                        },
                        target_surface=MILTargetSurface.stories_workspace,
                        related_story_id=story.id,
                        article_ids=[article.id for article in recent[:8]],
                        source_ids=[int(article.source_id) for article in recent if article.source_id],
                    )
                )
            elif len(recent) == 0 and older:
                candidates.append(
                    _SignalCandidate(
                        signal_code=f"MIL-STORY-DOWN-{story.id}",
                        signal_type=MILSignalType.story_momentum_down,
                        triage_action=MILTriageAction.suggest,
                        priority=MILPriority.low,
                        confidence_score=0.62,
                        explanation={
                            "reason_codes": ["STORY_MOMENTUM_DOWN"],
                            "human_summary": f"قصة {story.title} فقدت الزخم خلال آخر 24 ساعة رغم نشاط سابق قريب.",
                            "metrics": {"previous_count": len(older)},
                        },
                        payload={
                            "title": f"قصة تفقد الزخم: {story.title}",
                            "entity": None,
                            "event_summary": "لا توجد موجة حديثة؛ تحتاج زاوية جديدة أو قرار إغلاق المتابعة.",
                            "related_sources": sorted({article.source_name for article in older if article.source_name})[:8],
                            "related_article_ids": [article.id for article in older[:8]],
                            "source_count": len({article.source_name for article in older if article.source_name}),
                            "cluster_id": None,
                            "action_suggested": MILTriageAction.suggest.value,
                            "target_surface": MILTargetSurface.stories_workspace.value,
                            "recommended_action": "إما ضخ زاوية جديدة، أو تحويل القصة إلى متابعة منخفضة الأولوية.",
                            "metadata": {"story_id": story.id},
                        },
                        target_surface=MILTargetSurface.stories_workspace,
                        related_story_id=story.id,
                        article_ids=[article.id for article in older[:8]],
                        source_ids=[int(article.source_id) for article in older if article.source_id],
                    )
                )
        return candidates

    async def _build_event_signal_candidates(
        self,
        db: AsyncSession,
        *,
        articles: list[Article],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        now = datetime.utcnow()
        event_rows = await db.execute(
            select(EventMemoItem)
            .where(
                EventMemoItem.starts_at >= now - timedelta(hours=2),
                EventMemoItem.starts_at <= now + timedelta(hours=48),
                EventMemoItem.status.in_(["planned", "monitoring"]),
            )
            .order_by(EventMemoItem.starts_at.asc())
            .limit(25)
        )
        article_lookup = articles
        candidates: list[_SignalCandidate] = []
        for event in event_rows.scalars().all():
            tokens = set(self._tokenize(event.title) + [self._normalize_name(tag) for tag in (event.tags or []) if self._normalize_name(tag)])
            if not tokens:
                continue
            matched = [
                article
                for article in article_lookup
                if tokens.intersection(self._tokenize(article.title_ar or article.original_title or ""))
            ]
            if len(matched) < 2:
                continue
            local_hits = sum(1 for article in matched if article.category and str(article.category).lower() in {"newscategory.local_algeria", "local_algeria"})
            triage = MILTriageAction.flag if len(matched) < 4 else MILTriageAction.escalate
            confidence = min(0.95, round(0.54 + min(len(matched), 5) * 0.07 + (0.05 if local_hits else 0), 3))
            candidates.append(
                _SignalCandidate(
                    signal_code=f"MIL-EVENT-{event.id}",
                    signal_type=MILSignalType.pre_event_attention_rise,
                    triage_action=triage,
                    priority=MILPriority.medium if triage == MILTriageAction.flag else MILPriority.high,
                    confidence_score=confidence,
                    explanation={
                        "reason_codes": ["PRE_EVENT_ATTENTION_RISE", "LOCAL_IMPACT_RELEVANCE" if local_hits else "SOURCE_DIVERSITY"],
                        "human_summary": f"الحدث {event.title} بدأ يجذب تغطية مبكرة عبر {len(matched)} مادة قبل موعده.",
                        "metrics": {"matched_articles": len(matched), "local_hits": local_hits},
                    },
                    payload={
                        "title": f"تصاعد مبكر: {event.title}",
                        "entity": None,
                        "event_summary": "الحدث يكتسب حرارة تغطية قبل موعده، ما يرفع خطر تفويت المسار إذا تأخرنا.",
                        "related_sources": sorted({article.source_name for article in matched if article.source_name})[:8],
                        "related_article_ids": [article.id for article in matched[:8]],
                        "source_count": len({article.source_name for article in matched if article.source_name}),
                        "cluster_id": None,
                        "action_suggested": triage.value,
                        "target_surface": MILTargetSurface.events_board.value,
                        "recommended_action": "جهّز حزمة ما قبل الحدث أو حوّل الحدث إلى متابعة مرفوعة الجاهزية.",
                        "metadata": {"event_id": event.id},
                    },
                    target_surface=MILTargetSurface.events_board,
                    related_event_id=event.id,
                    article_ids=[article.id for article in matched[:8]],
                    source_ids=[int(article.source_id) for article in matched if article.source_id],
                )
            )
        return candidates

    async def _build_archive_signal_candidates(
        self,
        db: AsyncSession,
        *,
        articles: list[Article],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        article_ids = [article.id for article in articles]
        if not article_ids:
            return []
        rows = await db.execute(
            select(ArticleRelation, Article)
            .join(Article, Article.id == ArticleRelation.to_article_id)
            .where(
                ArticleRelation.from_article_id.in_(article_ids),
                ArticleRelation.relation_type.in_(["related", "impact", "sequence"]),
                ArticleRelation.score >= 0.65,
            )
            .order_by(desc(ArticleRelation.score))
            .limit(20)
        )
        candidates: list[_SignalCandidate] = []
        seen_from_article_ids: set[int] = set()
        for relation, related_article in rows.all():
            if relation.from_article_id in seen_from_article_ids:
                continue
            seen_from_article_ids.add(relation.from_article_id)
            source_article = next((article for article in articles if article.id == relation.from_article_id), None)
            if not source_article:
                continue
            candidates.append(
                _SignalCandidate(
                    signal_code=f"MIL-ARCH-{relation.from_article_id}-{related_article.id}",
                    signal_type=MILSignalType.archive_relevance_found,
                    triage_action=MILTriageAction.suggest,
                    priority=MILPriority.low,
                    confidence_score=min(0.92, round(0.5 + float(relation.score or 0.0) * 0.35, 3)),
                    explanation={
                        "reason_codes": ["ARCHIVE_RELEVANCE_FOUND", relation.relation_type.upper()],
                        "human_summary": "تم العثور على سياق أرشيفي قريب يمكن أن يثري المعالجة الحالية بسرعة.",
                        "metrics": {"relation_score": float(relation.score or 0.0)},
                    },
                    payload={
                        "title": f"أرشيف مناسب: {source_article.title_ar or source_article.original_title}",
                        "entity": None,
                        "event_summary": f"هناك مادة أرشيفية مرتبطة: {related_article.title_ar or related_article.original_title}",
                        "related_sources": [value for value in [source_article.source_name, related_article.source_name] if value][:8],
                        "related_article_ids": [source_article.id, related_article.id],
                        "source_count": len({value for value in [source_article.source_name, related_article.source_name] if value}),
                        "cluster_id": None,
                        "action_suggested": MILTriageAction.suggest.value,
                        "target_surface": MILTargetSurface.editor_context.value,
                        "recommended_action": "أضف هذه الخلفية كفقرة تفسيرية أو رابط سياقي في المسودة أو القصة.",
                        "metadata": {"relation_type": relation.relation_type},
                    },
                    target_surface=MILTargetSurface.editor_context,
                    article_ids=[source_article.id, related_article.id],
                    source_ids=[int(source_article.source_id)] if source_article.source_id else [],
                )
            )
        return candidates

    def _build_risk_signal_candidates(
        self,
        *,
        articles: list[Article],
        source_scores: dict[int, float],
        topics_by_article: dict[int, list[str]],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        candidates: list[_SignalCandidate] = []
        topic_buckets: dict[str, list[Article]] = defaultdict(list)
        for article in articles:
            topics = topics_by_article.get(article.id) or article.keywords or []
            for topic in topics[:4]:
                normalized = self._normalize_name(str(topic))
                if normalized:
                    topic_buckets[normalized].append(article)

        for topic, bucket in topic_buckets.items():
            if len(bucket) < 2:
                continue
            low_trust_sources = [
                article
                for article in bucket
                if article.source_id and source_scores.get(int(article.source_id), 0.45) <= 0.35
            ]
            distinct_sources = {article.source_name for article in bucket if article.source_name}
            if len(low_trust_sources) >= 2 and len(distinct_sources) >= 2:
                candidates.append(
                    _SignalCandidate(
                        signal_code=f"MIL-RISK-{hashlib.sha1(topic.encode('utf-8')).hexdigest()[:14].upper()}",
                        signal_type=MILSignalType.low_trust_source_spread,
                        triage_action=MILTriageAction.flag,
                        priority=MILPriority.medium,
                        confidence_score=0.72,
                        explanation={
                            "reason_codes": ["LOW_TRUST_SOURCE_SPREAD"],
                            "human_summary": f"الموضوع {topic} ينتشر عبر مصادر منخفضة الثقة أكثر من اللازم.",
                            "metrics": {"article_count": len(bucket), "low_trust_count": len(low_trust_sources)},
                        },
                        payload={
                            "title": f"انتشار منخفض الثقة: {topic}",
                            "entity": topic,
                            "event_summary": "الموضوع ينتشر، لكن دعمه الحالي يأتي من مصادر تستحق حذرًا إضافيًا.",
                            "related_sources": sorted(distinct_sources)[:8],
                            "related_article_ids": [article.id for article in bucket[:8]],
                            "source_count": len(distinct_sources),
                            "cluster_id": None,
                            "action_suggested": MILTriageAction.flag.value,
                            "target_surface": MILTargetSurface.editorial_sidebar.value,
                            "recommended_action": "لا ترفع هذا المسار قبل تأكيده من مصدر أعلى ثقة.",
                            "metadata": {"topic": topic},
                        },
                        target_surface=MILTargetSurface.editorial_sidebar,
                        article_ids=[article.id for article in bucket[:8]],
                        source_ids=[int(article.source_id) for article in bucket if article.source_id],
                    )
                )
            elif len(distinct_sources) == 1 and len(bucket) >= 2:
                only_source = next(iter(distinct_sources))
                candidates.append(
                    _SignalCandidate(
                        signal_code=f"MIL-SINGLE-{hashlib.sha1((topic + only_source).encode('utf-8')).hexdigest()[:14].upper()}",
                        signal_type=MILSignalType.single_source_claim_only,
                        triage_action=MILTriageAction.suggest,
                        priority=MILPriority.low,
                        confidence_score=0.58,
                        explanation={
                            "reason_codes": ["SINGLE_SOURCE_CLAIM_ONLY"],
                            "human_summary": f"الموضوع {topic} يتكرر، لكن ما زال محصورًا في مصدر واحد عمليًا.",
                            "metrics": {"article_count": len(bucket)},
                        },
                        payload={
                            "title": f"ادعاء من مصدر واحد: {topic}",
                            "entity": topic,
                            "event_summary": "رصدنا تكرارًا من نفس المصدر دون دعم كافٍ من بقية المشهد.",
                            "related_sources": [only_source],
                            "related_article_ids": [article.id for article in bucket[:8]],
                            "source_count": 1,
                            "cluster_id": None,
                            "action_suggested": MILTriageAction.suggest.value,
                            "target_surface": MILTargetSurface.editorial_sidebar.value,
                            "recommended_action": "راقب ولا تتوسع تحريريًا قبل ظهور تأكيد مستقل.",
                            "metadata": {"topic": topic},
                        },
                        target_surface=MILTargetSurface.editorial_sidebar,
                        article_ids=[article.id for article in bucket[:8]],
                        source_ids=[int(article.source_id) for article in bucket if article.source_id],
                    )
                )
        return candidates

    async def _build_competitor_signal_candidates(
        self,
        db: AsyncSession,
        *,
        articles: list[Article],
        cutoff: datetime,
    ) -> list[_SignalCandidate]:
        rows = await db.execute(
            select(CompetitorXrayItem)
            .where(
                CompetitorXrayItem.created_at >= cutoff,
                CompetitorXrayItem.status == "new",
            )
            .order_by(desc(CompetitorXrayItem.priority_score), desc(CompetitorXrayItem.created_at))
            .limit(20)
        )
        candidates: list[_SignalCandidate] = []
        article_titles = [(article.id, set(self._tokenize(article.title_ar or article.original_title or ""))) for article in articles]
        for item in rows.scalars().all():
            item_tokens = set(self._tokenize(item.competitor_title))
            if not item_tokens:
                continue
            overlap = 0
            for _, title_tokens in article_titles:
                if item_tokens.intersection(title_tokens):
                    overlap += 1
            signal_type = MILSignalType.competitor_breakout_story if overlap else MILSignalType.competitor_coverage_gap
            triage = MILTriageAction.escalate if item.priority_score >= 0.75 and overlap == 0 else MILTriageAction.flag
            candidates.append(
                _SignalCandidate(
                    signal_code=f"MIL-COMP-{item.id}",
                    signal_type=signal_type,
                    triage_action=triage,
                    priority=MILPriority.high if triage == MILTriageAction.escalate else MILPriority.medium,
                    confidence_score=min(0.96, round(0.5 + float(item.priority_score or 0.0) * 0.4, 3)),
                    explanation={
                        "reason_codes": ["COMPETITOR_COVERAGE_GAP" if overlap == 0 else "COMPETITOR_BREAKOUT_STORY"],
                        "human_summary": item.angle_rationale or "المنافسون يدفعون قصة أو زاوية لم تتبلور لدينا بالقدر نفسه.",
                        "metrics": {"matching_internal_articles": overlap, "priority_score": float(item.priority_score or 0.0)},
                    },
                    payload={
                        "title": item.competitor_title[:180],
                        "entity": None,
                        "event_summary": item.competitor_summary or "قصة منافس صاعدة تستحق فحصًا تحريريًا.",
                        "related_sources": [f"competitor:{item.source_id}" if item.source_id else "competitor"],
                        "related_article_ids": ([item.matched_article_id] if item.matched_article_id else []),
                        "source_count": 1,
                        "cluster_id": None,
                        "action_suggested": triage.value,
                        "target_surface": MILTargetSurface.today_orchestration.value if triage == MILTriageAction.escalate else MILTargetSurface.stories_workspace.value,
                        "recommended_action": "افتح المنافسين وحدد هل نحتاج دخولًا سريعًا أو زاوية مختلفة قبل اتساع الفجوة.",
                        "metadata": {"competitor_url": item.competitor_url},
                    },
                    target_surface=MILTargetSurface.today_orchestration if triage == MILTriageAction.escalate else MILTargetSurface.stories_workspace,
                    competitor_item_ids=[item.id],
                    article_ids=[item.matched_article_id] if item.matched_article_id else [],
                    source_ids=[int(item.source_id)] if item.source_id else [],
                )
            )
        return candidates

    def _build_clusters(
        self,
        *,
        articles: list[Article],
        entities_by_article: dict[int, list[_EntityMention]],
        source_scores: dict[int, float],
        entity_lookup: dict[str, int],
        cutoff: datetime,
    ) -> list[_ClusterBucket]:
        buckets: dict[str, _ClusterBucket] = {}
        for article in articles:
            mentions = entities_by_article.get(article.id, [])
            dominant_entity = next((entity for entity in mentions if entity.entity_type in {"org", "location", "event", "topic", "person"}), None)
            title = (article.title_ar or article.original_title or "").strip()
            tokens = self._tokenize(title)
            if not tokens:
                continue
            key_seed = dominant_entity.normalized_name if dominant_entity else " ".join(tokens[:3])
            cluster_key = hashlib.sha1(f"{key_seed}|{' '.join(tokens[:4])}".encode("utf-8")).hexdigest()[:16]
            bucket = buckets.get(cluster_key)
            if not bucket:
                bucket = _ClusterBucket(
                    cluster_key=cluster_key,
                    label=title[:255] or f"Cluster {cluster_key}",
                    representative_title=title[:255] or None,
                    dominant_entity=dominant_entity.name if dominant_entity else None,
                )
                buckets[cluster_key] = bucket

            bucket.article_ids.append(article.id)
            if article.source_id:
                bucket.source_ids.add(int(article.source_id))
            if article.source_name:
                bucket.source_names.add(article.source_name)
            if article.category and article.category.lower() in {"local_algeria", "algeria", "national"}:
                bucket.local_boost += 1
            if article.source_name and any(marker in article.source_name.lower() for marker in ("alg", "dz", "الجز", "الشروق")):
                bucket.local_boost += 1
            if dominant_entity:
                bucket.entity_names[dominant_entity.name] += 1
                bucket.dominant_entity_id = entity_lookup.get(f"{dominant_entity.entity_type}::{dominant_entity.normalized_name}")
            article_time = article.published_at or article.crawled_at or article.created_at
            bucket.first_seen_at = min(bucket.first_seen_at, article_time) if bucket.first_seen_at else article_time
            bucket.last_seen_at = max(bucket.last_seen_at, article_time) if bucket.last_seen_at else article_time

        clusters: list[_ClusterBucket] = []
        for bucket in buckets.values():
            article_count = len(bucket.article_ids)
            # Some ingestion paths populate source_name before source_id.
            # Use the strongest available diversity signal so MIL does not
            # undercount corroborating sources in early-phase analysis.
            source_diversity = max(len(bucket.source_ids), len(bucket.source_names))
            if article_count < 2:
                continue

            span_hours = max(
                0.5,
                ((bucket.last_seen_at or datetime.utcnow()) - (bucket.first_seen_at or cutoff)).total_seconds() / 3600.0,
            )
            velocity = round(article_count / span_hours, 3)
            trust_values = [source_scores.get(source_id, 0.45) for source_id in bucket.source_ids]
            avg_trust = mean(trust_values) if trust_values else 0.45
            local_boost = 1 if bucket.local_boost >= 2 else 0
            confidence = min(
                0.99,
                round(
                    0.32
                    + (article_count * 0.08)
                    + (min(source_diversity, 4) * 0.12)
                    + (min(velocity, 4) * 0.05)
                    + (avg_trust * 0.18)
                    + (local_boost * 0.08),
                    3,
                ),
            )
            triage = MILTriageAction.suggest
            if article_count >= 4 and source_diversity >= 3 and confidence >= 0.82:
                triage = MILTriageAction.escalate
            elif article_count >= 3 and source_diversity >= 2 and confidence >= 0.68:
                triage = MILTriageAction.flag

            priority = MILPriority.low
            if triage == MILTriageAction.escalate and local_boost:
                priority = MILPriority.critical
            elif triage == MILTriageAction.escalate:
                priority = MILPriority.high
            elif triage == MILTriageAction.flag:
                priority = MILPriority.medium

            target_surface = self._map_target_surface(triage=triage, local_boost=bool(local_boost))
            dominant_entity_name = bucket.entity_names.most_common(1)[0][0] if bucket.entity_names else bucket.dominant_entity
            reason_codes = ["CLUSTER_GROWTH", "SOURCE_DIVERSITY"]
            if local_boost:
                reason_codes.append("LOCAL_IMPACT_RELEVANCE")
            if confidence >= 0.8:
                reason_codes.append("HIGH_CONFIDENCE")

            human_summary = (
                f"رُصد نمو متقارب لهذا الموضوع عبر {source_diversity} مصادر و{article_count} مادة خلال نافذة قصيرة، "
                f"بمستوى ثقة {int(confidence * 100)}٪."
            )
            recommended_action = {
                MILTriageAction.escalate: "افتح ملف التغطية الآن ونسّق متابعة تحريرية عاجلة.",
                MILTriageAction.flag: "راقب هذا المسار وراجع إن كان يحتاج زاوية أو متابعة إضافية.",
                MILTriageAction.suggest: "استخدمه كاقتراح سياقي أو زاوية متابعة منخفضة المخاطر.",
            }[triage]
            bucket.velocity_score = velocity
            bucket.confidence_score = confidence
            bucket.triage_action = triage
            bucket.priority = priority
            bucket.target_surface = target_surface
            bucket.explanation = {
                "reason_codes": reason_codes,
                "human_summary": human_summary,
                "metrics": {
                    "article_count": article_count,
                    "source_diversity_count": source_diversity,
                    "velocity_score": velocity,
                    "avg_source_trust": round(avg_trust, 3),
                    "local_boost": local_boost,
                },
            }
            bucket.payload = {
                "title": bucket.representative_title or bucket.label,
                "entity": dominant_entity_name,
                "event_summary": human_summary,
                "related_sources": sorted(bucket.source_names)[:8],
                "related_article_ids": bucket.article_ids[:8],
                "source_count": source_diversity,
                "cluster_id": None,
                "action_suggested": triage.value,
                "target_surface": target_surface.value,
                "recommended_action": recommended_action,
                "metadata": {
                    "priority": priority.value,
                    "local_boost": bool(local_boost),
                },
            }
            clusters.append(bucket)

        triage_rank = {
            MILTriageAction.escalate: 3,
            MILTriageAction.flag: 2,
            MILTriageAction.suggest: 1,
        }
        clusters.sort(
            key=lambda item: (
                triage_rank.get(item.triage_action, 0),
                item.confidence_score,
                item.velocity_score,
            ),
            reverse=True,
        )
        return clusters

    async def _upsert_clusters(self, db: AsyncSession, clusters: list[_ClusterBucket]) -> list[_ClusterBucket]:
        if not clusters:
            return []
        keys = [cluster.cluster_key for cluster in clusters]
        rows = await db.execute(select(MILCluster).where(MILCluster.cluster_key.in_(keys)))
        existing_lookup = {row.cluster_key: row for row in rows.scalars().all()}

        for cluster in clusters:
            row = existing_lookup.get(cluster.cluster_key)
            metadata_json = {
                "article_ids": cluster.article_ids[:12],
                "source_names": sorted(cluster.source_names)[:12],
            }
            if row:
                row.label = cluster.label
                row.dominant_entity = cluster.dominant_entity
                row.article_count = len(cluster.article_ids)
                row.source_diversity_count = max(len(cluster.source_ids), len(cluster.source_names))
                row.velocity_score = cluster.velocity_score
                row.confidence_score = cluster.confidence_score
                row.target_surface = cluster.target_surface.value
                row.metadata_json = metadata_json
                row.last_seen_at = cluster.last_seen_at or datetime.utcnow()
            else:
                row = MILCluster(
                    cluster_key=cluster.cluster_key,
                    label=cluster.label,
                    dominant_entity=cluster.dominant_entity,
                    article_count=len(cluster.article_ids),
                    source_diversity_count=max(len(cluster.source_ids), len(cluster.source_names)),
                    velocity_score=cluster.velocity_score,
                    confidence_score=cluster.confidence_score,
                    target_surface=cluster.target_surface.value,
                    metadata_json=metadata_json,
                    first_seen_at=cluster.first_seen_at or datetime.utcnow(),
                    last_seen_at=cluster.last_seen_at or datetime.utcnow(),
                )
                db.add(row)
                await db.flush()
                existing_lookup[cluster.cluster_key] = row

            cluster.payload["cluster_id"] = int(row.id)
            article_rows = await db.execute(
                select(MILClusterArticle.article_id).where(MILClusterArticle.cluster_id == row.id)
            )
            existing_article_ids = set(article_rows.scalars().all())
            for article_id in cluster.article_ids:
                if article_id in existing_article_ids:
                    continue
                db.add(
                    MILClusterArticle(
                        cluster_id=row.id,
                        article_id=article_id,
                        weight=cluster.confidence_score,
                    )
                )
        await db.flush()
        return clusters

    async def _upsert_signals(
        self,
        db: AsyncSession,
        *,
        candidates: list[_SignalCandidate],
        created_from_job_id: str | None,
    ) -> list[MILSignal]:
        if not candidates:
            return []
        signal_codes = [candidate.signal_code for candidate in candidates]
        rows = await db.execute(select(MILSignal).where(MILSignal.signal_code.in_(signal_codes)))
        existing_lookup = {row.signal_code: row for row in rows.scalars().all()}
        created_or_updated: list[MILSignal] = []

        for candidate in candidates:
            row = existing_lookup.get(candidate.signal_code)
            payload = dict(candidate.payload)
            explanation = dict(candidate.explanation)
            if row:
                row.signal_type = candidate.signal_type.value
                row.triage_action = candidate.triage_action.value
                row.priority = candidate.priority.value
                row.confidence_score = candidate.confidence_score
                row.explanation_json = explanation
                row.payload_json = payload
                row.target_surface = candidate.target_surface.value
                row.related_entity_id = candidate.related_entity_id
                row.related_story_id = candidate.related_story_id
                row.related_event_id = candidate.related_event_id
                row.related_cluster_id = candidate.related_cluster_id or payload.get("cluster_id")
                row.created_from_job_id = created_from_job_id
                row.updated_at = datetime.utcnow()
                row.status = MILSignalStatus.active.value
            else:
                row = MILSignal(
                    signal_code=candidate.signal_code,
                    signal_type=candidate.signal_type.value,
                    triage_action=candidate.triage_action.value,
                    priority=candidate.priority.value,
                    confidence_score=candidate.confidence_score,
                    explanation_json=explanation,
                    payload_json=payload,
                    target_surface=candidate.target_surface.value,
                    related_entity_id=candidate.related_entity_id,
                    related_story_id=candidate.related_story_id,
                    related_event_id=candidate.related_event_id,
                    related_cluster_id=candidate.related_cluster_id or payload.get("cluster_id"),
                    created_from_job_id=created_from_job_id,
                    status=MILSignalStatus.active.value,
                )
                db.add(row)
                await db.flush()
                existing_lookup[candidate.signal_code] = row

            created_or_updated.append(row)
            await self._sync_signal_sources(
                db,
                signal=row,
                article_ids=candidate.article_ids[:8],
                source_ids=sorted(set(candidate.source_ids)),
                competitor_item_ids=candidate.competitor_item_ids[:8],
            )
        await db.flush()
        return created_or_updated

    async def _sync_signal_sources(
        self,
        db: AsyncSession,
        *,
        signal: MILSignal,
        article_ids: list[int],
        source_ids: list[int],
        competitor_item_ids: list[int] | None = None,
    ) -> None:
        rows = await db.execute(select(MILSignalSource).where(MILSignalSource.signal_id == signal.id))
        existing_refs = {row.support_ref for row in rows.scalars().all()}
        for article_id in article_ids:
            support_ref = f"article:{article_id}"
            if support_ref in existing_refs:
                continue
            db.add(
                MILSignalSource(
                    signal_id=signal.id,
                    article_id=article_id,
                    support_kind=MILSupportKind.article.value,
                    support_ref=support_ref,
                    weight=1.0,
                )
            )
        for source_id in source_ids:
            support_ref = f"source:{source_id}"
            if support_ref in existing_refs:
                continue
            db.add(
                MILSignalSource(
                    signal_id=signal.id,
                    source_id=source_id,
                    support_kind=MILSupportKind.source.value,
                    support_ref=support_ref,
                    weight=0.6,
                )
            )
        for competitor_item_id in competitor_item_ids or []:
            support_ref = f"competitor_item:{competitor_item_id}"
            if support_ref in existing_refs:
                continue
            db.add(
                MILSignalSource(
                    signal_id=signal.id,
                    competitor_item_id=competitor_item_id,
                    support_kind=MILSupportKind.competitor_item.value,
                    support_ref=support_ref,
                    weight=0.75,
                )
            )

    def _serialize_signal(self, signal: MILSignal) -> MILSignalListItem:
        return MILSignalListItem(
            id=signal.id,
            signal_code=signal.signal_code,
            signal_type=MILSignalType(signal.signal_type),
            triage_action=MILTriageAction(signal.triage_action),
            priority=MILPriority(signal.priority),
            confidence_score=float(signal.confidence_score or 0.0),
            target_surface=MILTargetSurface(signal.target_surface),
            status=MILSignalStatus(signal.status),
            payload=MILSignalPayload.model_validate(signal.payload_json or {}),
            explanation=MILSignalExplanation.model_validate(signal.explanation_json or {}),
            related_story_id=signal.related_story_id,
            related_event_id=signal.related_event_id,
            related_cluster_id=signal.related_cluster_id,
            created_at=signal.created_at,
            updated_at=signal.updated_at,
            dismissed_at=signal.dismissed_at,
            dismissed_by=signal.dismissed_by,
            useful_count=int(signal.useful_count or 0),
            useful_last_marked_at=signal.useful_last_marked_at,
            snoozed_until=signal.snoozed_until,
        )

    def _serialize_signal_detail(self, signal: MILSignal, supports: list[MILSignalSource]) -> MILSignalDetail:
        list_item = self._serialize_signal(signal)
        return MILSignalDetail(
            **list_item.model_dump(),
            supports=[
                MILSignalSupportItem(
                    article_id=support.article_id,
                    source_id=support.source_id,
                    competitor_item_id=support.competitor_item_id,
                    support_kind=support.support_kind,
                    support_ref=support.support_ref,
                    weight=float(support.weight or 0.0),
                    created_at=support.created_at,
                )
                for support in supports
            ],
        )

    def _serialize_today_card(self, signal: MILSignal) -> MILTodayCard:
        payload = MILSignalPayload.model_validate(signal.payload_json or {})
        explanation = MILSignalExplanation.model_validate(signal.explanation_json or {})
        return MILTodayCard(
            signal_id=signal.id,
            signal_code=signal.signal_code,
            title=payload.title,
            why_it_matters=explanation.human_summary,
            confidence_score=float(signal.confidence_score or 0.0),
            recommended_action=payload.recommended_action,
            source_count=int(payload.source_count or 0),
            target_surface=MILTargetSurface(signal.target_surface),
            href=self._resolve_signal_href(signal),
            created_at=signal.created_at,
            signal_type=MILSignalType(signal.signal_type),
            triage_action=MILTriageAction(signal.triage_action),
            priority=MILPriority(signal.priority),
            useful_count=int(signal.useful_count or 0),
        )

    def _resolve_signal_href(self, signal: MILSignal) -> str | None:
        payload = MILSignalPayload.model_validate(signal.payload_json or {})
        if signal.related_story_id:
            return f"/stories?story_id={signal.related_story_id}"
        if signal.related_event_id:
            return f"/events?event_id={signal.related_event_id}"
        if payload.related_article_ids:
            return f"/news/{payload.related_article_ids[0]}"
        if signal.target_surface == MILTargetSurface.director_dashboard.value:
            return "/dashboard"
        if signal.target_surface == MILTargetSurface.events_board.value:
            return "/events"
        if signal.target_surface == MILTargetSurface.stories_workspace.value:
            return "/stories"
        if signal.target_surface == MILTargetSurface.editor_context.value:
            return "/workspace-drafts"
        return "/news"

    def _resolve_signal_href_from_item(self, signal: MILSignalListItem) -> str | None:
        if signal.related_story_id:
            return f"/stories?story_id={signal.related_story_id}"
        if signal.related_event_id:
            return f"/events?event_id={signal.related_event_id}"
        if signal.payload.related_article_ids:
            return f"/news/{signal.payload.related_article_ids[0]}"
        return None

    def _map_target_surface(self, *, triage: MILTriageAction, local_boost: bool) -> MILTargetSurface:
        if triage == MILTriageAction.escalate:
            return MILTargetSurface.today_orchestration
        if triage == MILTriageAction.flag and local_boost:
            return MILTargetSurface.events_board
        if triage == MILTriageAction.flag:
            return MILTargetSurface.editorial_sidebar
        return MILTargetSurface.stories_workspace

    def _tokenize(self, value: str) -> list[str]:
        normalized = self._normalize_name(value)
        if not normalized:
            return []
        return [token for token in normalized.split() if token and token not in _STOP_WORDS and len(token) > 2][:6]

    def _normalize_name(self, value: str | None) -> str:
        if not value:
            return ""
        normalized = _TOKEN_RE.sub(" ", value.strip().lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized


mil_service = MediaIntelligenceService()
