"""
storage/topic_store.py

Handles all file I/O for topics.txt.
Keeps storage logic isolated from routing logic.
"""

import os
import logging

logger = logging.getLogger(__name__)

TOPICS_FILE = "topics.txt"


def _read_topics() -> list[str]:
    """Read all topics from file. Returns empty list if file doesn't exist."""
    if not os.path.exists(TOPICS_FILE):
        return []
    with open(TOPICS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def get_all_topics() -> list[str]:
    """Return deduplicated list of topics, preserving insertion order."""
    topics = _read_topics()
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def add_topic(topic: str) -> bool:
    """
    Normalize and append a topic.
    Returns True if added, False if it was a duplicate.
    """
    normalized = topic.strip().lower()
    existing = get_all_topics()

    if normalized in existing:
        logger.info(f"Duplicate topic skipped: '{normalized}'")
        return False

    with open(TOPICS_FILE, "a") as f:
        f.write(normalized + "\n")

    logger.info(f"Topic added: '{normalized}'")
    return True


def clear_topics() -> None:
    """Delete all stored topics."""
    if os.path.exists(TOPICS_FILE):
        os.remove(TOPICS_FILE)
        logger.info("All topics cleared.")
