"""
digest_runner.py  [Phase 5]

Manual trigger to generate today's digest.
Usage:
    python digest_runner.py <user_id>

Provider is selected via LLM_PROVIDER in .env (default: gemini).
Output:
    - Prints HTML to console
    - Saves to digest_<user_id>.html

Extension points (Phase 6):
    - EPUB: pass digest.html to ebooklib converter
    - Email to Kindle: attach digest.epub via smtplib
    - Telegram bot: call this from a bot command handler
"""

import logging
import sys
import datetime
from dotenv import load_dotenv

from llm.factory import get_llm_client
from services.digest_service import DigestService
from services.email_service import send_to_kindle
from storage.topic_store import get_kindle_email, update_last_digest_date

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run(user_id: str):
    logger.info(f"=== Bitty Bettr Digest Runner starting for user {user_id} ===")
    user_id = str(user_id)

    # Get email upfront
    to_email = get_kindle_email(user_id)
    if not to_email:
        # Fallback to general Kindle Email if not set
        import os
        to_email = os.getenv("KINDLE_EMAIL")
        if not to_email:
            logger.error(f"No Kindle email set for user {user_id} and no fallback.")
            raise ValueError("No Kindle email configured for user.")

    try:
        llm_client = get_llm_client()
        service = DigestService(llm_client)
        html, title = service.generate(user_id)
    except ValueError as e:
        # Friendly message for empty topic list
        logger.error(str(e))
        raise
    except EnvironmentError as e:
        logger.error(str(e))
        raise

    # Print to console (optional but good for debugging)
    print("Digest generated successfully.")

    # Save to file
    output_file = f"digest_{user_id}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"=== Digest saved to {output_file} ===")

    # Send to Kindle via email
    today = datetime.date.today().strftime("%B %d, %Y")
    send_to_kindle(output_file, today, title, to_email=to_email)

    # Track last digest date (using local time logic contextually, but here we just store local date string)
    from storage.topic_store import get_timezone
    import pytz
    tz_str = get_timezone(user_id)
    try:
        tz = pytz.timezone(tz_str)
    except pytz.UnknownTimeZoneError:
        tz = pytz.UTC
        
    local_now = datetime.datetime.now(datetime.timezone.utc).astimezone(tz)
    date_str = local_now.strftime("%Y-%m-%d")
    
    update_last_digest_date(user_id, date_str)
    
    logger.info(f"=== Digest workflow complete for user {user_id} ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python digest_runner.py <user_id>")
        sys.exit(1)
    run(sys.argv[1])
