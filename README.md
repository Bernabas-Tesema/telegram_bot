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
