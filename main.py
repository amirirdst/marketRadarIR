# -*- coding: utf-8 -*-

import asyncio
import sys

from prices import build_report
from telegram_bot import send_report


async def main():
    print("🚀 Market Radar IR شروع شد.")
    print("🔄 دریافت قیمت‌های جدید...")

    report = build_report()

    print(report)
    print("\n📤 ارسال گزارش به تلگرام...")

    await send_report(report)

    print("✅ گزارش با موفقیت به تلگرام ارسال شد.")
    print("🏁 اجرای این نوبت تمام شد.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        sys.exit(0)
    except Exception as e:
        print(f"❌ خطا: {e}")
        sys.exit(1)