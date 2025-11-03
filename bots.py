import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import TelegramError

# -------------------- CONFIG --------------------
# Get token and admin ID from environment variables (required).
# For security we do NOT keep a hardcoded token in the repo.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required. Do not store your token in the repo.")

ADMIN_ID_ENV = os.environ.get("TELEGRAM_ADMIN_ID")
if not ADMIN_ID_ENV:
    raise RuntimeError("TELEGRAM_ADMIN_ID environment variable is required.")
try:
    ADMIN_ID = int(ADMIN_ID_ENV)
except ValueError:
    raise RuntimeError("TELEGRAM_ADMIN_ID must be an integer (the numeric chat id of the admin).")

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

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

if __name__ == "__main__":
    main()
