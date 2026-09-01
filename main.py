import asyncio

from prices import build_report
from telegram_bot import send_report


async def run_once():
    try:
        print("🚀 Market Radar IR")
        print("📤 در حال دریافت قیمت‌ها و ارسال گزارش...\n")

        report = build_report()

        print(report)
        print("\n📤 در حال ارسال گزارش...")

        await send_report(report)

        print("✅ گزارش با موفقیت ارسال شد.")
        return True

    except Exception as error:
        print(f"❌ خطا: {error}")
        return False


async def main():
    await run_once()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 اجرای برنامه متوقف شد.")