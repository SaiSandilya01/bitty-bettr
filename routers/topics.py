"""
routers/topics.py

REST endpoints for topic management.
POST /topics  — add a topic
GET  /topics  — list all topics
DELETE /topics — clear all topics
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from storage.topic_store import add_topic, get_all_topics, clear_topics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/topics", tags=["topics"])


class TopicRequest(BaseModel):
    topic: str

    @field_validator("topic")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("topic must not be empty")
        return v


class TopicResponse(BaseModel):
    topics: list[str]


@router.post("", status_code=201)
def create_topic(body: TopicRequest):
    """Add a new topic. Returns 409 if the topic already exists."""
    added = add_topic(body.topic)
    if not added:
        raise HTTPException(status_code=409, detail="Topic already exists")
    return {"message": "Topic added", "topic": body.topic.strip().lower()}


@router.get("", response_model=TopicResponse)
def list_topics():
    """Return all stored topics."""
    topics = get_all_topics()
    logger.info(f"Returning {len(topics)} topics")
    return TopicResponse(topics=topics)


@router.delete("", status_code=200)
def delete_all_topics():
    """Clear all stored topics."""
    clear_topics()
    return {"message": "All topics cleared"}
