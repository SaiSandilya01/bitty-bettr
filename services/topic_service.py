"""
services/topic_service.py  [Phase 2]

Clean interface for reading processed topics.
Wraps storage layer — callers never touch the file directly.
"""

import logging
from storage.topic_store import get_active_topics, mark_topics_processed as store_mark

logger = logging.getLogger(__name__)


def get_topics(user_id: str, limit: int = 5) -> list[str]:
    """
    Return a list of topics ready for LLM consumption, limited by quota.
    Raises ValueError if no topics are queued.
    """
    topics = get_active_topics(user_id, limit=limit)

    if not topics:
        raise ValueError("No topics found. Add some via Telegram first.")

    logger.info(f"Loaded {len(topics)} topic(s) for user {user_id}: {topics}")
    return topics

def mark_topics_processed(user_id: str, topics: list[str]) -> None:
    """Mark the given topics as processed for the user."""
    store_mark(user_id, topics)
    logger.info(f"Marked {len(topics)} topic(s) as processed for user {user_id}.")
