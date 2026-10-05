# -*- coding: utf-8 -*-
import asyncio
import sys
import time
from datetime import datetime

from prices import build_report
from telegram_bot import send_report

INTERVAL_SECONDS = 10 * 60

async def run_once():
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] 🔄 دریافت قیمت‌ها...")
    report = build_report()
    print(report)
    print("📤 ارسال به Telegram...")
    await send_report(report)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ✅ ارسال موفق")

async def main():
    print("🚀 Market Radar IR — اجرای دائمی")
    print("⏱️ فاصله ارسال: هر 10 دقیقه")
    print("🛑 برای توقف: Ctrl+C")
    while True:
        started = time.monotonic()
        try:
            await run_once()
        except Exception as e:
            print(f"❌ خطای این نوبت: {type(e).__name__}: {e}")
        elapsed = time.monotonic() - started
        wait_seconds = max(5, INTERVAL_SECONDS - elapsed)
        print(f"⏳ نوبت بعدی حدود {wait_seconds/60:.1f} دقیقه دیگر...")
        await asyncio.sleep(wait_seconds)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Market Radar متوقف شد.")
        sys.exit(0)
