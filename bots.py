import os
import sys
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import TelegramError

# -------------------- CONFIG --------------------
# Get token and admin ID from environment variables if available
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8414176554:AAHZjxCXihNbjTMmF-V9EkrePwRvRnJIx14")
ADMIN_ID = int(os.environ.get("TELEGRAM_ADMIN_ID", "5102029450"))

# -------------------- HANDLERS --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when user starts the bot"""
    await update.message.reply_text("👋 Hello! Please send your screenshot here.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward the screenshot to the admin and notify the user"""
    try:
        photo = update.message.photo[-1]
        user = update.message.from_user
        caption = f"📩 New screenshot received!\n👤 From: @{user.username or user.first_name}\n🆔 {user.id}"

        # Notify admin
        await context.bot.send_message(chat_id=ADMIN_ID, text="🔔 New screenshot received!")

        # Forward the screenshot to admin
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption)

        # Acknowledge to user
        await update.message.reply_text("✅ Screenshot received successfully!")

    except TelegramError as e:
        print(f"❌ Failed to send to admin: {e}")
        await update.message.reply_text("⚠️ Sorry, there was an error sending your screenshot. Please try again later.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages that are not photos"""
    await update.message.reply_text("❗ Please send only a screenshot image.")

# -------------------- MAIN --------------------

def main():
    """Start the bot"""
    # Quick runtime compatibility hint: older/newer combinations of
    # Python and python-telegram-bot can raise cryptic AttributeError
    # (for example when running on Python 3.13 with an incompatible
    # python-telegram-bot wheel). Detect obvious mismatch and provide
    # a helpful error message instead of the low-level traceback.
    if sys.version_info >= (3, 13):
        print("⚠️ Detected Python >= 3.13. python-telegram-bot may not yet support this version in some releases.")
        print("If you see an AttributeError referencing '_Updater__polling_cleanup_cb', try one of:")
        print("  * Use Python 3.12 or 3.11 for now (create a venv with that interpreter)")
        print("  * Upgrade/downgrade python-telegram-bot to a version built for your Python: e.g. `pip install --upgrade 'python-telegram-bot'` or pin a known good version")
        print("  * If using a hosted environment (Render, etc.), select a Python 3.12 runtime or add a compatible wheel")
        print("Proceeding — the program will still attempt to build the Application but will print a clearer message if it fails.")
    max_start_retries = 5
    backoff = 2

    for attempt in range(1, max_start_retries + 1):
        try:
            # Build the application (bot)
            app = Application.builder().token(BOT_TOKEN).build()

            # Add handlers
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            app.add_handler(MessageHandler(filters.ALL, unknown))

            print("🤖 Bot is running...")
            app.run_polling()
            return

        except TelegramError as e:
            print(f"⚠️ Telegram error (attempt {attempt}/{max_start_retries}): {e}")
            if attempt == max_start_retries:
                print("❌ Max retries reached, exiting.")
                raise
            sleep_for = backoff
            print(f"⏱ Waiting {sleep_for}s before retrying...")
            time.sleep(sleep_for)
            backoff *= 2

        except AttributeError as e:
            # Known symptom: when PTB/Updater is incompatible with the
            # Python runtime, an AttributeError like the one below is seen:
            # "'Updater' object has no attribute '_Updater__polling_cleanup_cb' and no __dict__ for setting new attributes"
            msg = str(e)
            if "_Updater__polling_cleanup_cb" in msg:
                print("\n❌ Compatibility error building python-telegram-bot Application:")
                print(f"   {msg}\n")
                print("This usually means the installed python-telegram-bot package is not compatible with the Python version in use (common on Python 3.13).")
                print("Recommended fixes:")
                print("  1) Use Python 3.12 or 3.11 for the runtime (create a venv with that interpreter).")
                print("  2) Or install a compatible release of python-telegram-bot (try: pip install --upgrade 'python-telegram-bot').")
                print("  3) If deploying to a host (Render, etc.), select a Python 3.12 runtime or add a compatible wheel to the build.")
                # Fail fast with clear message
                raise SystemExit(1)
            # Otherwise, re-raise unknown AttributeError
            print(f"❌ Unexpected AttributeError: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

if __name__ == "__main__":
    main()
