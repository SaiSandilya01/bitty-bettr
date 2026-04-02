"""
telegram_bot/bot.py

Telegram bot interface for BittyBettr.
Lets you queue topics, config email/timezone, and trigger digest generation from your phone.

Commands:
    /start         — Welcome message & command list
    /add <topic>   — Add a topic to the queue
    /list          — Show all queued topics
    /clear         — Clear all queued topics
    /digest        — Generate digest and email it to your Kindle now
    /mailId <mail> — Set your Kindle Email Address
    /timezone <tz> — Set your timezone (e.g. America/New_York)

Usage:
    python -m telegram_bot.bot
"""

import asyncio
import logging
import os
import sys
import datetime

from dotenv import load_dotenv
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Ensure the project root is in the path when run as a module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.topic_store import (
    add_topic, get_all_topics, clear_topics, set_kindle_email, 
    set_timezone, get_kindle_email, get_timezone, get_users_for_scheduled_digest
)
import digest_runner

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# UI Helpers
# ─────────────────────────────────────────────

def get_popular_topics_keyboard() -> InlineKeyboardMarkup:
    """Returns an inline keyboard with popular topic suggestions."""
    keyboard = [
        [
            InlineKeyboardButton("Artificial Intelligence", callback_data="add_topic:AI"),
            InlineKeyboardButton("Space Exploration", callback_data="add_topic:Space Exploration"),
        ],
        [
            InlineKeyboardButton("Personal Finance", callback_data="add_topic:Personal Finance"),
            InlineKeyboardButton("Ancient History", callback_data="add_topic:Ancient History"),
        ],
        [
            InlineKeyboardButton("Quantum Physics", callback_data="add_topic:Quantum Physics"),
            InlineKeyboardButton("Psychology", callback_data="add_topic:Psychology")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ─────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message listing available commands."""
    text = (
        "👋 *Welcome to BittyBettr!*\n\n"
        "Queue any topics you're curious about. I'll bundle them into a "
        "deep-dive digest sent straight to your Kindle daily at 6 PM local time.\n\n"
        "⚙️ *Setup:*\n"
        "1. `/mailId <your_kindle_email>` - Required for delivery.\n"
        "2. `/timezone <your_timezone>` - e.g. Europe/London. Default is UTC.\n\n"
        "📚 *Usage:*\n"
        "  /add `<topic>` — Add a topic to the queue\n"
        "  /list — Show your queued topics\n"
        "  /digest — Generate your digest *now*\n\n"
        "Want some ideas? Tap a suggestion below:"
    )
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_popular_topics_keyboard()
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a topic to the queue."""
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a topic. Example: `/add Quantum Computing`\n\nOr pick a popular one:",
            parse_mode="Markdown",
            reply_markup=get_popular_topics_keyboard()
        )
        return

    topic = " ".join(context.args).strip()
    await _handle_add_topic(update, user_id, topic)


async def _handle_add_topic(update: Update, user_id: str, topic: str) -> None:
    """Helper to process adding a topic (called via command or button)."""
    if not topic:
        await update.effective_message.reply_text("⚠️ Topic cannot be blank.")
        return

    added, queue_length = add_topic(user_id, topic)
    if added:
        await update.effective_message.reply_text(
            f"✅ Added: *{topic.lower()}*\n"
            f"You have {queue_length} topics in your queue. (We process up to 5 per digest)", 
            parse_mode="Markdown"
        )
    else:
        await update.effective_message.reply_text(
            f"⚠️ Already in your queue: *{topic.lower()}*\n"
            f"Queue length: {queue_length}", 
            parse_mode="Markdown"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(update.effective_user.id)
    
    if data.startswith("add_topic:"):
        topic = data.split(":", 1)[1]
        await _handle_add_topic(update, user_id, topic)


async def list_topics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all queued topics."""
    user_id = str(update.effective_user.id)
    topics = get_all_topics(user_id)
    if not topics:
        await update.message.reply_text("📭 No topics queued yet. Use /add to start.")
        return

    lines = "\n".join(f"  {i + 1}. {t}" for i, t in enumerate(topics))
    await update.message.reply_text(
        f"📋 *Your queued topics ({len(topics)}):*\n{lines}", parse_mode="Markdown"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all queued topics."""
    user_id = str(update.effective_user.id)
    clear_topics(user_id)
    await update.message.reply_text("🗑️ All topics cleared.")

async def mail_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the user's Kindle Email Address."""
    user_id = str(update.effective_user.id)
    if not context.args:
        current = get_kindle_email(user_id)
        msg = f"Your current Kindle Email: `{current}`" if current else "You haven't set a Kindle email yet."
        await update.message.reply_text(f"{msg}\nTo set it, use: `/mailId user_xyz@kindle.com`", parse_mode="Markdown")
        return
        
    email = context.args[0]
    set_kindle_email(user_id, email)
    await update.message.reply_text(f"✅ Kindle Email set to: `{email}`", parse_mode="Markdown")

async def timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the user's Timezone."""
    user_id = str(update.effective_user.id)
    if not context.args:
        current = get_timezone(user_id)
        await update.message.reply_text(
            f"Your current Timezone: `{current}`\n"
            "To set it, use: `/timezone America/New_York`\n"
            "Use standard IANA timezone names.", 
            parse_mode="Markdown"
        )
        return
        
    tz_name = context.args[0]
    if set_timezone(user_id, tz_name):
        await update.message.reply_text(f"✅ Timezone set to: `{tz_name}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Invalid timezone name: `{tz_name}`. Please use format like 'Europe/London'.", parse_mode="Markdown")

async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate the digest now and send it to Kindle."""
    user_id = str(update.effective_user.id)
    topics = get_all_topics(user_id)
    
    if not get_kindle_email(user_id):
        await update.message.reply_text("⚠️ Please set your Kindle Email first using `/mailId <email>`", parse_mode="Markdown")
        return
        
    if not topics:
        await update.message.reply_text("📭 No topics queued yet. Use /add to add some first.")
        return

    digest_count = min(5, len(topics))
    await update.message.reply_text(
        f"⏳ Generating your digest for the oldest *{digest_count} topic(s)*… this may take a minute.",
        parse_mode="Markdown",
    )

    try:
        await asyncio.to_thread(digest_runner.run, user_id)
        await update.message.reply_text("✅ Digest sent to your Kindle! Check your device shortly.")
    except Exception as e:
        logger.exception("Digest generation failed")
        await update.message.reply_text(f"❌ Something went wrong:\n`{e}`", parse_mode="Markdown")


# ─────────────────────────────────────────────
# Background Jobs
# ─────────────────────────────────────────────

async def scheduled_digest_job(context: ContextTypes.DEFAULT_TYPE):
    """Checks for users who should receive their digest now (6 PM local time)."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    # Defaulting to hour 18 (6 PM)
    eligible_users = get_users_for_scheduled_digest(utc_now, hour=18)
    
    if eligible_users:
        logger.info(f"Found {len(eligible_users)} user(s) eligible for scheduled digest.")
        
    for user_id in eligible_users:
        logger.info(f"Triggering scheduled digest for user {user_id}")
        try:
            # Send status message optionally
            await context.bot.send_message(
                chat_id=user_id, 
                text="🕰️ It's 6 PM! Generating your daily BittyBettr digest now..."
            )
            await asyncio.to_thread(digest_runner.run, user_id)
            await context.bot.send_message(
                chat_id=user_id, 
                text="✅ Your daily digest has been sent to your Kindle!"
            )
        except Exception as e:
            logger.error(f"Scheduled digest failed for user {user_id}: {e}")
            await context.bot.send_message(
                chat_id=user_id, 
                text=f"❌ Failed to generate daily digest automatically:\n`{str(e)}`",
                parse_mode="Markdown"
            )

# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

async def post_init(application: Application) -> None:
    """Set bot commands menu after init."""
    commands = [
        BotCommand("start", "Welcome message & instructions"),
        BotCommand("add", "Add a topic to your queue"),
        BotCommand("list", "Show your queued topics"),
        BotCommand("digest", "Generate and send digest immediately"),
        BotCommand("mailid", "Set your Kindle Email"),
        BotCommand("timezone", "Set your local timezone"),
        BotCommand("clear", "Clear all topics in queue"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu updated.")

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Add it to your .env file and try again.")
        sys.exit(1)

    app = Application.builder().token(token).post_init(post_init).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_topics))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("digest", digest))
    app.add_handler(CommandHandler("mailid", mail_id))
    app.add_handler(CommandHandler("mailId", mail_id)) # Handle camelCase variant just in case
    app.add_handler(CommandHandler("timezone", timezone))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(button_handler))

    # JobQueue
    if app.job_queue:
        # Run the check every 30 minutes
        app.job_queue.run_repeating(scheduled_digest_job, interval=1800, first=10)
        logger.info("Scheduled delivery job started (runs every 30 min).")
    else:
        logger.warning("JobQueue is not initialized! Scheduled digests will not work.")

    logger.info("BittyBettr Telegram bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
