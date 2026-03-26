"""
services/topic_service.py  [Phase 2]

Clean interface for reading processed topics.
Wraps storage layer — callers never touch the file directly.
"""

import logging
from storage.topic_store import get_all_topics

logger = logging.getLogger(__name__)


def get_topics() -> list[str]:
    """
    Return a deduplicated, normalized list of topics ready for LLM consumption.
    Raises ValueError if no topics are stored.
    """
    topics = get_all_topics()

    if not topics:
        raise ValueError("No topics found. Add some via POST /topics first.")

    logger.info(f"Loaded {len(topics)} topic(s) for processing: {topics}")
    return topics
