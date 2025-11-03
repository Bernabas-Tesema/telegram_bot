# Telegram screenshot bot

Simple Telegram bot that accepts screenshots from users and forwards them to an admin chat.

Setup
1. Create a Python virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

2. Set environment variables (required):

```powershell
$env:TELEGRAM_BOT_TOKEN = "<your-bot-token>"
$env:TELEGRAM_ADMIN_ID = "<your-admin-chat-id>"
```

3. Run the bot (from the project folder):

```powershell
python bot.py
```

Security
- Do NOT commit your bot token. The code requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ADMIN_ID` environment variables and will fail fast if missing.

Troubleshooting
- If you see an AttributeError mentioning "_Updater__polling_cleanup_cb" when the bot starts (for example on hosted platforms or when using Python 3.13), this is usually a compatibility issue between your Python runtime and the installed `python-telegram-bot` wheel. Try one of the following:
	- Use Python 3.12 or 3.11 for the runtime (create a venv using that interpreter).
	- Upgrade/downgrade `python-telegram-bot`: `python -m pip install --upgrade "python-telegram-bot"` or pin a known good version.
	- On hosted services (Render, etc.) select a runtime image that uses Python 3.12.

## Deploying with Docker on Render

If `runtime.txt` does not correctly pin the Python version, you can switch your Render service to use Docker for a guaranteed environment.

1.  **Go to your service's "Settings" page on the Render Dashboard.**
2.  **Change the "Environment" from "Python" to "Docker".**
3.  **Render will automatically detect the `Dockerfile` in your repository and build from it.**
4.  **Trigger a new deploy.**

This will build the bot inside a container running Python 3.12, which will resolve the compatibility errors.

