"""Pydantic schemas for the Media Intelligence Layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.mil import MILPriority, MILSignalStatus, MILSignalType, MILTargetSurface, MILTriageAction


class MILSignalPayload(BaseModel):
    title: str
    entity: str | None = None
    event_summary: str
    related_sources: list[str] = Field(default_factory=list)
    related_article_ids: list[int] = Field(default_factory=list)
    source_count: int = 0
    cluster_id: int | None = None
    action_suggested: MILTriageAction
    target_surface: MILTargetSurface
    recommended_action: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MILSignalExplanation(BaseModel):
    reason_codes: list[str] = Field(default_factory=list)
    human_summary: str
    metrics: dict[str, float | int | str] = Field(default_factory=dict)


class MILEntitySummary(BaseModel):
    id: int
    entity_name: str
    entity_type: str
    normalized_name: str
    aliases_json: list[str] = Field(default_factory=list)
    mention_count: int = 0
    first_seen_at: datetime
    last_seen_at: datetime
    trust_context_json: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class MILClusterSummary(BaseModel):
    id: int
    cluster_key: str
    label: str
    dominant_entity: str | None = None
    article_count: int
    source_diversity_count: int
    velocity_score: float
    confidence_score: float
    target_surface: str
    first_seen_at: datetime
    last_seen_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class MILSignalListItem(BaseModel):
    id: int
    signal_code: str
    signal_type: MILSignalType
    triage_action: MILTriageAction
    priority: MILPriority
    confidence_score: float
    target_surface: MILTargetSurface
    status: MILSignalStatus
    payload: MILSignalPayload
    explanation: MILSignalExplanation
    related_story_id: int | None = None
    related_event_id: int | None = None
    related_cluster_id: int | None = None
    created_at: datetime
    updated_at: datetime
    dismissed_at: datetime | None = None
    dismissed_by: int | None = None
    useful_count: int = 0
    useful_last_marked_at: datetime | None = None
    snoozed_until: datetime | None = None


class MILSignalSupportItem(BaseModel):
    article_id: int | None = None
    source_id: int | None = None
    competitor_item_id: int | None = None
    support_kind: str
    support_ref: str | None = None
    weight: float = 0.0
    created_at: datetime


class MILSignalDetail(MILSignalListItem):
    supports: list[MILSignalSupportItem] = Field(default_factory=list)


class MILTodayCard(BaseModel):
    signal_id: int
    signal_code: str
    title: str
    why_it_matters: str
    confidence_score: float
    recommended_action: str
    source_count: int
    target_surface: MILTargetSurface
    href: str | None = None
    created_at: datetime
    signal_type: MILSignalType
    triage_action: MILTriageAction = MILTriageAction.escalate
    priority: MILPriority = MILPriority.medium
    useful_count: int = 0


class MILTodaySection(BaseModel):
    key: str
    title: str
    hint: str
    items: list[MILTodayCard] = Field(default_factory=list)


class MILTodayFullResponse(BaseModel):
    generated_at: datetime
    critical_now: MILTodaySection
    watch_closely: MILTodaySection
    opportunities: MILTodaySection


class MILDashboardMetric(BaseModel):
    key: str
    label: str
    value: int | float | str
    hint: str | None = None
    tone: str = "default"


class MILDashboardListItem(BaseModel):
    title: str
    subtitle: str | None = None
    hint: str
    href: str | None = None
    confidence_score: float | None = None


class MILDashboardResponse(BaseModel):
    generated_at: datetime
    metrics: list[MILDashboardMetric] = Field(default_factory=list)
    rising_stories: list[MILDashboardListItem] = Field(default_factory=list)
    missed_opportunities: list[MILDashboardListItem] = Field(default_factory=list)
    competitor_pressure: list[MILDashboardListItem] = Field(default_factory=list)
    source_trust_watch: list[MILDashboardListItem] = Field(default_factory=list)


class MILInsightItem(BaseModel):
    title: str
    summary: str
    tone: str = "default"
    confidence_score: float | None = None
    href: str | None = None


class MILStoryInsights(BaseModel):
    story_id: int
    story_title: str
    momentum: str
    competitor_pressure: str
    archive_angle: str | None = None
    follow_up_angle: str | None = None
    linked_entities: list[str] = Field(default_factory=list)
    cards: list[MILInsightItem] = Field(default_factory=list)


class MILEventInsights(BaseModel):
    event_id: int
    event_title: str
    attention_level: str
    geographic_spread: str
    social_relevance: str
    coverage_risk: str
    suggested_pack: list[str] = Field(default_factory=list)
    cards: list[MILInsightItem] = Field(default_factory=list)


class MILEditorContext(BaseModel):
    draft_id: int
    article_id: int | None = None
    work_id: str | None = None
    live_signals: list[MILSignalListItem] = Field(default_factory=list)
    archive_links: list[MILInsightItem] = Field(default_factory=list)
    missing_angles: list[MILInsightItem] = Field(default_factory=list)
    related_entities: list[str] = Field(default_factory=list)
    competitor_angles: list[MILInsightItem] = Field(default_factory=list)


class MILAnalyzeRecentRequest(BaseModel):
    hours: int = Field(default=6, ge=1, le=48)
    max_articles: int = Field(default=300, ge=25, le=1000)
    include_competitors: bool = False


class MILDismissRequest(BaseModel):
    note: str | None = None


class MILSnoozeRequest(BaseModel):
    hours: int = Field(default=6, ge=1, le=72)


class MILActionResponse(BaseModel):
    signal_id: int
    status: str
    useful_count: int = 0
    snoozed_until: datetime | None = None
