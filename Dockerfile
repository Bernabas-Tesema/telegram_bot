# Use the official Python 3.12 slim image as a base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local project files to the container
COPY . .

# Install dependencies
# --no-cache-dir: Disables the cache, which is good for keeping image sizes down.
# --upgrade pip: Ensures the latest version of pip is used.
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables for the bot token and admin ID
# These will be provided by Render's secret management.
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_ADMIN_ID=""

# Command to run the bot when the container starts
CMD ["python", "bot.py"]
