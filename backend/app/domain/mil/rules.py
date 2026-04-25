"""Typed enums and constants for the Media Intelligence Layer."""

from __future__ import annotations

from enum import Enum


class MILTriageAction(str, Enum):
    suggest = "suggest"
    flag = "flag"
    escalate = "escalate"


class MILSignalStatus(str, Enum):
    active = "active"
    dismissed = "dismissed"
    consumed = "consumed"
    archived = "archived"


class MILPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class MILSignalType(str, Enum):
    cluster_growth = "cluster_growth"
    mention_spike = "mention_spike"
    topic_velocity = "topic_velocity"
    repeated_entity_burst = "repeated_entity_burst"
    competitor_coverage_gap = "competitor_coverage_gap"
    competitor_breakout_story = "competitor_breakout_story"
    competitor_speed_advantage = "competitor_speed_advantage"
    story_momentum_up = "story_momentum_up"
    story_momentum_down = "story_momentum_down"
    story_needs_followup = "story_needs_followup"
    pre_event_attention_rise = "pre_event_attention_rise"
    event_localization_growth = "event_localization_growth"
    newsroom_missing_angle = "newsroom_missing_angle"
    archive_relevance_found = "archive_relevance_found"
    multi_source_confirmation = "multi_source_confirmation"
    low_trust_source_spread = "low_trust_source_spread"
    single_source_claim_only = "single_source_claim_only"


class MILTargetSurface(str, Enum):
    today_orchestration = "today_orchestration"
    editorial_sidebar = "editorial_sidebar"
    stories_workspace = "stories_workspace"
    events_board = "events_board"
    director_dashboard = "director_dashboard"
    editor_context = "editor_context"


class MILSupportKind(str, Enum):
    article = "article"
    source = "source"
    competitor_item = "competitor_item"
    cluster = "cluster"
    story = "story"
    event = "event"
    memory = "memory"
