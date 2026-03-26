"""
digest_runner.py  [Phase 5]

Manual trigger to generate today's digest.
Usage:
    python digest_runner.py

Provider is selected via LLM_PROVIDER in .env (default: gemini).
Output:
    - Prints HTML to console
    - Saves to digest.html

Extension points (Phase 6):
    - EPUB: pass digest.html to ebooklib converter
    - Email to Kindle: attach digest.epub via smtplib
    - Telegram bot: call this from a bot command handler
"""

import logging
import sys
from dotenv import load_dotenv

from llm.factory import get_llm_client
from services.digest_service import DigestService
from services.email_service import send_to_kindle
from datetime import date

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_FILE = "digest.html"


def run():
    logger.info("=== Bitty Bettr Digest Runner starting ===")

    try:
        llm_client = get_llm_client()
        service = DigestService(llm_client)
        html = service.generate()
    except ValueError as e:
        # Friendly message for empty topic list
        logger.error(str(e))
        sys.exit(1)
    except EnvironmentError as e:
        logger.error(str(e))
        sys.exit(1)

    # Print to console
    print(html)

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"=== Digest saved to {OUTPUT_FILE} ===")

    # Send to Kindle via email
    today = date.today().strftime("%B %d, %Y")
    send_to_kindle(OUTPUT_FILE, today)

if __name__ == "__main__":
    run()
