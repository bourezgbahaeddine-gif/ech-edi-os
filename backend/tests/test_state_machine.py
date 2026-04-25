from app.domain.news.state_machine import can_transition, validate_transition
from app.models.news import NewsStatus


def test_valid_transition_candidate_to_approved_handoff() -> None:
    assert can_transition(NewsStatus.CANDIDATE, NewsStatus.APPROVED_HANDOFF)


def test_valid_transition_classified_to_approved_handoff() -> None:
    assert can_transition(NewsStatus.CLASSIFIED, NewsStatus.APPROVED_HANDOFF)


def test_valid_transition_rejected_to_approved_handoff() -> None:
    assert can_transition(NewsStatus.REJECTED, NewsStatus.APPROVED_HANDOFF)


def test_invalid_transition_rejected_to_candidate() -> None:
    result = validate_transition(NewsStatus.REJECTED, NewsStatus.CANDIDATE)
    assert result.valid is False
    assert NewsStatus.CANDIDATE not in result.allowed_targets


def test_valid_transition_published_to_ready_for_manual_publish() -> None:
    assert can_transition(NewsStatus.PUBLISHED, NewsStatus.READY_FOR_MANUAL_PUBLISH)
