"""
Flask-based webhook entrypoint for Telegram Bot (Render-compatible)

This replaces long-polling with a minimal Flask server that:
- Imports the existing handlers from `bots.py` (start, handle_photo, unknown)
- Exposes POST "/" to receive Telegram updates
- Reads TELEGRAM_TOKEN (or TELEGRAM_BOT_TOKEN) from environment
- Runs on host 0.0.0.0 and port from PORT env var (Render requirement)
- Automatically sets the bot webhook on startup using WEBHOOK_URL or RENDER_EXTERNAL_URL

Notes:
- python-telegram-bot v20+ is asyncio-based. We run a background asyncio loop
  and feed updates from Flask into the PTB Application using process_update().
- Ensure you set these env vars on Render:
    TELEGRAM_TOKEN (or TELEGRAM_BOT_TOKEN)
    TELEGRAM_ADMIN_ID  (already used by bots.py handlers)
    WEBHOOK_URL        (e.g., https://your-service.onrender.com/)
  If WEBHOOK_URL is not set, we try RENDER_EXTERNAL_URL from Render automatically.
"""

from __future__ import annotations

import sys
import os
import json
import asyncio
import threading
from typing import Optional

# python-telegram-bot 20.x currently requires Python <= 3.12 for the
# prebuilt binary wheels. Running on Python 3.13+ can produce an
# AttributeError when building the PTB Application. Detect this early
# and print a clear message so users know to run with Python 3.12/3.11
# or install a compatible build.
if sys.version_info >= (3, 13):
    raise RuntimeError(
        "python-telegram-bot may not be compatible with Python >= 3.13.\n"
        "Please run this project with Python 3.12 or 3.11, or install a "
        "python-telegram-bot wheel built for your Python version."
    )

from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Import existing bot logic (handlers and any constants like ADMIN_ID)
import bots as bot_logic


# -------------------- Config --------------------
TOKEN: Optional[str] = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN (or TELEGRAM_BOT_TOKEN) environment variable.")

# Optional: explicit webhook URL or inferred from Render
WEBHOOK_URL: Optional[str] = os.environ.get("WEBHOOK_URL") or os.environ.get("RENDER_EXTERNAL_URL")
# Optional secret token used to secure the webhook. If set, the same value
# will be passed to Telegram via set_webhook(secret_token=...) and Telegram
# will include it in the request header 'X-Telegram-Bot-Api-Secret-Token'.
WEBHOOK_SECRET: Optional[str] = os.environ.get("WEBHOOK_SECRET") or os.environ.get("TELEGRAM_WEBHOOK_SECRET")


# -------------------- PTB Application (async) --------------------
# We'll run PTB on a dedicated asyncio event loop in a background thread.

ptb_loop = asyncio.new_event_loop()


def _run_loop_forever(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


loop_thread = threading.Thread(target=_run_loop_forever, args=(ptb_loop,), daemon=True)
loop_thread.start()


# Create the Application and register handlers using the existing functions from bots.py
ptb_app = Application.builder().token(TOKEN).build()
ptb_app.add_handler(CommandHandler("start", bot_logic.start))
ptb_app.add_handler(MessageHandler(filters.PHOTO, bot_logic.handle_photo))
ptb_app.add_handler(MessageHandler(filters.ALL, bot_logic.unknown))


async def _ptb_startup():
    """Initialize and start PTB Application, and set webhook if URL is provided."""
    await ptb_app.initialize()
    await ptb_app.start()

    if WEBHOOK_URL:
        # Normalize URL and set webhook on Telegram. If WEBHOOK_SECRET is
        # provided, pass it to Telegram so incoming requests include the
        # 'X-Telegram-Bot-Api-Secret-Token' header with this value.
        url = WEBHOOK_URL.strip()
        if WEBHOOK_SECRET:
            await ptb_app.bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
        else:
            await ptb_app.bot.set_webhook(url=url)
    else:
        # Webhook URL not available — warn, but continue. Incoming updates will 404.
        print("⚠️ WEBHOOK_URL not set and RENDER_EXTERNAL_URL not found — set one to enable Telegram to deliver updates.")


# Schedule startup on the background loop and wait for completion
asyncio.run_coroutine_threadsafe(_ptb_startup(), ptb_loop).result()


# -------------------- Flask App --------------------
app = Flask(__name__)


@app.get("/")
def health() -> str:
    return "OK", 200


@app.post("/")
def telegram_webhook():
    # Verify request is JSON (Telegram sends JSON)
    # If a WEBHOOK_SECRET is configured, validate the Telegram secret header
    # to ensure the request really came from Telegram.
    if WEBHOOK_SECRET:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not header_secret or header_secret != WEBHOOK_SECRET:
            # Forbidden when secret is present but doesn't match
            abort(403)

    if not request.is_json:
        abort(400)

    data = request.get_json(force=True)
    try:
        update = Update.de_json(data, ptb_app.bot)
    except Exception as e:
        print(f"Failed to parse update JSON: {e}")
        abort(400)

    # Process the update on the PTB asyncio loop
    fut = asyncio.run_coroutine_threadsafe(ptb_app.process_update(update), ptb_loop)
    try:
        # Optionally wait a short time for errors; not strictly necessary.
        fut.result(timeout=5)
    except Exception as e:
        # Log but still return 200 to avoid Telegram re-sending repeatedly if it's our internal error
        print(f"Error while processing update: {e}")
    return "", 200


if __name__ == "__main__":
    # Start Flask server for Render (PORT is provided by the platform)
    port = int(os.environ.get("PORT", "8080"))
    host = "0.0.0.0"
    print(f"Starting Flask server on {host}:{port} with webhook mode enabled")
    app.run(host=host, port=port)

