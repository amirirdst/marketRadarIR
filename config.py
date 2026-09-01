import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN در فایل .env تنظیم نشده است.")

if not TELEGRAM_CHANNEL_ID:
    raise RuntimeError("TELEGRAM_CHANNEL_ID در فایل .env تنظیم نشده است.")
