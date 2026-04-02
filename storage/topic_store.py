"""
storage/topic_store.py

Handles all file I/O for user_data.json.
Keeps storage logic isolated from routing logic.
"""

import os
import json
import logging
import datetime
import pytz
from typing import Optional

logger = logging.getLogger(__name__)

DATA_FILE = "user_data.json"

def _load_data() -> dict:
    """Read all user data from JSON file. Returns empty dict if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse {DATA_FILE}, starting fresh.")
        return {}

def _save_data(data: dict) -> None:
    """Write data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _ensure_user(data: dict, user_id: str) -> None:
    """Ensure user structure exists in data."""
    if user_id not in data:
        data[user_id] = {
            "kindle_email": None,
            "timezone": "UTC",
            "last_digest_date": None,
            "topics_queue": [],
            "processed_topics": []
        }

def add_topic(user_id: str, topic: str) -> tuple[bool, int]:
    """
    Normalize and append a topic to the user's queue.
    Returns (True if added/False if duplicate, current queue length).
    """
    user_id = str(user_id)
    data = _load_data()
    _ensure_user(data, user_id)

    normalized = topic.strip().lower()
    
    # Check if duplicate in queue
    queued_topics = [t["topic"] for t in data[user_id]["topics_queue"]]
    if normalized in queued_topics:
        logger.info(f"Duplicate topic in queue for user {user_id}: '{normalized}'")
        return False, len(queued_topics)

    # Note: We allow adding even if it's in processed_topics to let them revisit, 
    # but we prevent duplicates currently in the queue.
    
    data[user_id]["topics_queue"].append({
        "topic": normalized,
        "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

    _save_data(data)
    logger.info(f"Topic added for user {user_id}: '{normalized}'")
    return True, len(data[user_id]["topics_queue"])

def get_active_topics(user_id: str, limit: int = 5) -> list[str]:
    """Return the oldest `limit` topics from the user's queue."""
    user_id = str(user_id)
    data = _load_data()
    if user_id not in data:
        return []
    
    # Sort by added_at just in case
    queue = sorted(data[user_id]["topics_queue"], key=lambda x: x.get("added_at", ""))
    return [t["topic"] for t in queue[:limit]]

def mark_topics_processed(user_id: str, topics: list[str]) -> None:
    """Move specified topics from topics_queue to processed_topics."""
    user_id = str(user_id)
    data = _load_data()
    if user_id not in data:
        return
    
    topics_set = set(topics)
    remaining_queue = []
    
    for item in data[user_id]["topics_queue"]:
        if item["topic"] in topics_set:
            # Move to processed
            data[user_id]["processed_topics"].append({
                "topic": item["topic"],
                "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        else:
            remaining_queue.append(item)
            
    data[user_id]["topics_queue"] = remaining_queue
    _save_data(data)

def get_all_topics(user_id: str) -> list[str]:
    """Return list of all topics currently in the user's queue."""
    user_id = str(user_id)
    data = _load_data()
    if user_id not in data:
        return []
    
    queue = sorted(data[user_id]["topics_queue"], key=lambda x: x.get("added_at", ""))
    return [t["topic"] for t in queue]

def clear_topics(user_id: str) -> None:
    """Clear all topics in the user's queue."""
    user_id = str(user_id)
    data = _load_data()
    if user_id in data:
        data[user_id]["topics_queue"] = []
        _save_data(data)
        logger.info(f"All queued topics cleared for user {user_id}.")

def set_kindle_email(user_id: str, email: str) -> None:
    """Set the Kindle email for the user."""
    user_id = str(user_id)
    data = _load_data()
    _ensure_user(data, user_id)
    data[user_id]["kindle_email"] = email.strip()
    _save_data(data)

def get_kindle_email(user_id: str) -> Optional[str]:
    """Get the Kindle email for the user."""
    user_id = str(user_id)
    data = _load_data()
    return data.get(user_id, {}).get("kindle_email")

def set_timezone(user_id: str, tz_name: str) -> bool:
    """Set the timezone for the user. Returns True if valid, False if invalid tz."""
    user_id = str(user_id)
    try:
        pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return False
        
    data = _load_data()
    _ensure_user(data, user_id)
    data[user_id]["timezone"] = tz_name
    _save_data(data)
    return True

def get_timezone(user_id: str) -> str:
    """Get the user's timezone, defaulting to UTC."""
    user_id = str(user_id)
    data = _load_data()
    return data.get(user_id, {}).get("timezone", "UTC")

def update_last_digest_date(user_id: str, date_str: str) -> None:
    """Update the last digest date for the user."""
    user_id = str(user_id)
    data = _load_data()
    _ensure_user(data, user_id)
    data[user_id]["last_digest_date"] = date_str
    _save_data(data)

def get_users_for_scheduled_digest(utc_now: datetime.datetime, hour: int = 18) -> list[str]:
    """
    Find users whose local time aligns with the specified `hour` (default 18 for 6 PM)
    and haven't received a digest for their local *today*. 
    Also they must have queued topics and a kindle email.
    """
    data = _load_data()
    eligible_users = []
    
    for user_id, user_data in data.items():
        if not user_data.get("kindle_email"):
            continue
        if not user_data.get("topics_queue"):
            continue
            
        tz_str = user_data.get("timezone", "UTC")
        try:
            tz = pytz.timezone(tz_str)
            local_time = utc_now.astimezone(tz)
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC
            local_time = utc_now.astimezone(tz)
            
        # Is it at or past the target hour? (e.g., 18:00)
        # Assuming cron runs every 30 mins, we check if hour >= target
        if local_time.hour >= hour:
            local_date_str = local_time.strftime("%Y-%m-%d")
            last_date = user_data.get("last_digest_date")
            if last_date != local_date_str:
                eligible_users.append(user_id)
                
    return eligible_users
