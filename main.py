# -*- coding: utf-8 -*-

from prices import build_report
from telegram_bot import send_report
import asyncio


async def main():
    print("🚀 Market Radar IR شروع شد.")
    print("🔄 دریافت قیمت‌های جدید...")

    try:
        report = build_report()

        print(report)
        print("\n📤 ارسال گزارش به تلگرام...")

        await send_report(report)

        print("✅ گزارش با موفقیت به تلگرام ارسال شد.")

    except Exception as e:
        print(f"❌ خطا: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())