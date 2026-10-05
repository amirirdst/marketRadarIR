# -*- coding: utf-8 -*-

import asyncio
import sys
from datetime import datetime, timedelta

from prices import build_report
from telegram_bot import send_report


# هر 10 دقیقه
INTERVAL_MINUTES = 10

# زمان‌های ارسال:
# 01، 11، 21، 31، 41، 51
START_MINUTE = 1


async def run_once():
    print(
        f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        "🔄 دریافت قیمت‌ها..."
    )

    report = build_report()

    print(report)
    print("📤 ارسال به Telegram...")

    await send_report(report)

    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        "✅ ارسال موفق"
    )


def get_next_run_time():
    now = datetime.now()

    # پیدا کردن نزدیک‌ترین دقیقه از الگوی:
    # 01, 11, 21, 31, 41, 51

    current_minute = now.minute

    next_minute = (
        START_MINUTE
        + (
            (
                current_minute - START_MINUTE
            ) // INTERVAL_MINUTES
            + 1
        )
        * INTERVAL_MINUTES
    )

    next_run = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    ) + timedelta(minutes=next_minute)

    return next_run


async def main():

    print("🚀 Market Radar IR — اجرای دائمی")
    print("⏱️ ارسال هر 10 دقیقه")
    print("🕐 زمان‌ها: 01، 11، 21، 31، 41، 51")
    print("🛑 برای توقف: Ctrl+C")

    while True:

        try:

            next_run = get_next_run_time()
            now = datetime.now()

            wait_seconds = (
                next_run - now
            ).total_seconds()

            print(
                f"⏳ ارسال بعدی: "
                f"{next_run:%H:%M:%S}"
            )

            print(
                f"⏱️ حدود "
                f"{wait_seconds / 60:.1f} دقیقه دیگر"
            )

            await asyncio.sleep(wait_seconds)

            await run_once()

        except Exception as e:

            print(
                f"❌ خطا: "
                f"{type(e).__name__}: {e}"
            )

            # خطای موقت نباید ربات را متوقف کند.
            await asyncio.sleep(5)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n🛑 Market Radar متوقف شد.")
        sys.exit(0)
