"""Media Intelligence Layer persistence models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class MILSignal(Base):
    __tablename__ = "mil_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_code = Column(String(64), nullable=False, unique=True, index=True)
    signal_type = Column(String(64), nullable=False, index=True)
    triage_action = Column(String(16), nullable=False, index=True)
    priority = Column(String(16), nullable=False, default="medium", index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    explanation_json = Column(JSON, nullable=False, default=dict)
    payload_json = Column(JSON, nullable=False, default=dict)
    target_surface = Column(String(48), nullable=False, default="editorial_sidebar", index=True)
    related_entity_id = Column(Integer, ForeignKey("mil_entities.id"), nullable=True, index=True)
    related_story_id = Column(Integer, ForeignKey("stories.id"), nullable=True, index=True)
    related_event_id = Column(Integer, ForeignKey("event_memo_items.id"), nullable=True, index=True)
    related_cluster_id = Column(Integer, ForeignKey("mil_clusters.id"), nullable=True, index=True)
    created_from_job_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    dismissed_at = Column(DateTime, nullable=True, index=True)
    dismissed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    useful_count = Column(Integer, nullable=False, default=0)
    useful_last_marked_at = Column(DateTime, nullable=True, index=True)
    useful_last_marked_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    snoozed_until = Column(DateTime, nullable=True, index=True)
    status = Column(String(16), nullable=False, default="active", index=True)

    signal_sources = relationship("MILSignalSource", back_populates="signal")
    entity = relationship("MILEntity", foreign_keys=[related_entity_id])

    __table_args__ = (
        Index("ix_mil_signal_triage_status_created", "triage_action", "status", "created_at"),
        Index("ix_mil_signal_surface_status_created", "target_surface", "status", "created_at"),
    )


class MILSignalSource(Base):
    __tablename__ = "mil_signal_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("mil_signals.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True, index=True)
    competitor_item_id = Column(Integer, ForeignKey("competitor_xray_items.id"), nullable=True, index=True)
    support_kind = Column(String(32), nullable=False, default="article", index=True)
    support_ref = Column(String(255), nullable=True)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    signal = relationship("MILSignal", back_populates="signal_sources")

    __table_args__ = (
        UniqueConstraint(
            "signal_id",
            "article_id",
            "source_id",
            "competitor_item_id",
            "support_kind",
            name="uq_mil_signal_source_support",
        ),
    )


class MILEntity(Base):
    __tablename__ = "mil_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String(255), nullable=False)
    entity_type = Column(String(32), nullable=False, default="topic", index=True)
    normalized_name = Column(String(255), nullable=False, index=True)
    aliases_json = Column(JSON, nullable=False, default=list)
    first_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    mention_count = Column(Integer, nullable=False, default=0, index=True)
    trust_context_json = Column(JSON, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("normalized_name", "entity_type", name="uq_mil_entities_name_type"),
        Index("ix_mil_entity_type_mentions", "entity_type", "mention_count"),
    )


class MILEntityEdge(Base):
    __tablename__ = "mil_entity_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_entity_id = Column(Integer, ForeignKey("mil_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id = Column(Integer, ForeignKey("mil_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    edge_type = Column(String(32), nullable=False, index=True)
    weight = Column(Float, nullable=False, default=0.0)
    first_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    evidence_count = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("source_entity_id", "target_entity_id", "edge_type", name="uq_mil_entity_edge"),
        Index("ix_mil_entity_edge_type_weight", "edge_type", "weight"),
    )


class MILSourceTrustScore(Base):
    __tablename__ = "mil_source_trust_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    score = Column(Float, nullable=False, default=0.0, index=True)
    score_components_json = Column(JSON, nullable=False, default=dict)
    last_calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class MILCluster(Base):
    __tablename__ = "mil_clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_key = Column(String(64), nullable=False, unique=True, index=True)
    label = Column(String(255), nullable=False)
    dominant_entity = Column(String(255), nullable=True, index=True)
    article_count = Column(Integer, nullable=False, default=0)
    source_diversity_count = Column(Integer, nullable=False, default=0)
    velocity_score = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    target_surface = Column(String(48), nullable=False, default="editorial_sidebar", index=True)
    metadata_json = Column(JSON, nullable=False, default=dict)
    first_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_mil_clusters_velocity_last_seen", "velocity_score", "last_seen_at"),
    )


class MILClusterArticle(Base):
    __tablename__ = "mil_cluster_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("mil_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    weight = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("cluster_id", "article_id", name="uq_mil_cluster_article"),
        Index("ix_mil_cluster_article_cluster_weight", "cluster_id", "weight"),
    )
