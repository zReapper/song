import os
import logging
import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reuse Notegpt endpoints and headers from the web app
API_GENERATE = "https://notegpt.io/api/v2/music/generate"
API_STATUS = "https://notegpt.io/api/v2/music/status"
HEADERS = {
    "Host": "notegpt.io",
    "sec-ch-ua-platform": '"Android"',
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "accept": "*/*",
    "origin": "https://notegpt.io",
    "referer": "https://notegpt.io/ai-music-generator",
    # NOTE: if cookies are required, set them via environment variable NOTE_COOKIES
}

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
NOTEGPT_COOKIES = os.environ.get('NOTEGPT_COOKIES')
if NOTEGPT_COOKIES:
    HEADERS['cookie'] = NOTEGPT_COOKIES

# Helper: generate song using same logic as api/index.py
def generate_track(prompt: str, lyrics: str = "", timeout_seconds: int = 240):
    payload = {"prompt": prompt, "lyrics": lyrics, "duration": 0}

    try:
        gen_resp = requests.post(API_GENERATE, json=payload, headers=HEADERS, timeout=20)
        gen_resp.raise_for_status()
        gen_json = gen_resp.json()
    except Exception as e:
        logger.exception("Generation request failed")
        # return error string
        msg = str(e)
        if "403" in msg or "401" in msg:
            return None, "Auth Failed. Cookies expired or invalid."
        return None, "Failed to start generation."

    conv_id = gen_json.get("data", {}).get("conversation_id") or gen_json.get("conversation_id")
    if not conv_id:
        return None, "Server did not return a Task ID."

    # Poll for status
    sleep_interval = 3
    max_attempts = max(5, timeout_seconds // sleep_interval)

    for attempt in range(max_attempts):
        try:
            status_resp = requests.get(API_STATUS, params={"conversation_id": conv_id}, headers=HEADERS, timeout=15)
            status_resp.raise_for_status()
            status_json = status_resp.json()
            data_block = status_json.get("data", {})
            status_text = data_block.get("status", "").lower()

            if status_text == "failed":
                return None, "Generation Failed."

            if status_text == "success":
                music_url = data_block.get("music_url")
                thumb_url = data_block.get("thumbnail_url")
                return {"music_url": music_url, "thumbnail_url": thumb_url}, None

            time.sleep(sleep_interval)
        except requests.exceptions.RequestException as e:
            logger.warning("Poll request failed: %s", e)
            time.sleep(sleep_interval)
            continue

    return None, "Timeout: The AI took too long."


# Telegram command handler
async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /generate <theme> | optionally add lyrics after '||' e.g. /generate Cinematic || some lyrics")
        return

    text = " ".join(args)
    # allow split by || to include lyrics
    parts = text.split('||', 1)
    prompt = parts[0].strip()
    lyrics = parts[1].strip() if len(parts) > 1 else ""

    await update.message.reply_text(f"Starting generation for: {prompt}\nThis may take a minute or two...")

    result, err = generate_track(prompt, lyrics)
    if err:
        await update.message.reply_text(f"Error: {err}")
        return

    music_url = result.get('music_url')
    if not music_url:
        await update.message.reply_text("No music URL returned by the service.")
        return

    # send the music URL back
    await update.message.reply_text(f"Your track is ready: {music_url}")


def main():
    if not TELEGRAM_TOKEN:
        print("Please set TELEGRAM_BOT_TOKEN environment variable.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('generate', generate_command))

    print("Bot started. Press Ctrl-C to stop.")
    app.run_polling()


if __name__ == '__main__':
    main()
