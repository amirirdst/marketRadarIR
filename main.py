import asyncio

from prices import build_report
from telegram_bot import send_report


async def main():
    print("📊 در حال دریافت قیمت‌های لحظه‌ای...")

    report = build_report()

    print()
    print(report)
    print()

    print("📤 در حال ارسال گزارش به تلگرام...")

    await send_report(report)

    print()
    print("✅ گزارش با موفقیت به Telegram ارسال شد.")


if __name__ == "__main__":
    asyncio.run(main())
