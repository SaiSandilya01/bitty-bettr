"""
services/email_service.py [Phase 6]

Sends the generated digest to a Kindle via email.
Uses Python's built-in smtplib.
"""

import os
import smtplib
import time
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

def send_to_kindle(html_filepath: str, date_str: str, title: str, to_email: str = None):
    """
    Sends the HTML file to the configured Kindle email address.
    """
    kindle_email = to_email or os.getenv("KINDLE_EMAIL")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not all([kindle_email, smtp_user, smtp_password]):
        logger.warning(
            "Email config missing. Skipping Kindle delivery. "
            "Ensure KINDLE_EMAIL, SMTP_USER, and SMTP_PASSWORD are set."
        )
        return

    logger.info(f"Preparing to send digest to Kindle: {kindle_email}")

    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = smtp_user
    msg["To"] = kindle_email
    
    # Body can be empty for Send-to-Kindle, Amazon only cares about the attachment
    msg.set_content("Enjoy your daily learning digest from Bitty Bettr!")

    # Read and attach the HTML file
    try:
        with open(html_filepath, "rb") as f:
            file_data = f.read()
            
        msg.add_attachment(
            file_data,
            maintype="text",
            subtype="html",
            filename=f"Daily_Digest_{date_str.replace(' ', '_').replace(',', '')}_{int(time.time())}.html"
        )
    except Exception as e:
        logger.error(f"Failed to read digest file for attachment: {e}")
        return

    # Send the email via SMTP
    try:
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Successfully sent digest to Kindle!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
