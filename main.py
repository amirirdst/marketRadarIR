# -*- coding: utf-8 -*-

import asyncio

from prices import build_report
from telegram_bot import send_report


async def send_fresh_report():

    print("\n" + "=" * 60)
    print("🔄 دریافت قیمت‌های جدید...")

    try:
        # هر اجرا قیمت‌های تازه را از API دریافت می‌کند.
        report = build_report()

        print(report)

        print("\n📤 در حال ارسال گزارش جدید به تلگرام...")

        await send_report(report)

        print("✅ گزارش با موفقیت به تلگرام ارسال شد.")

        return True

    except Exception as e:

        print(f"❌ خطا در دریافت یا ارسال گزارش: {e}")

        return False


async def main():

    print("🚀 Market Radar IR شروع شد.")
    print("📡 دریافت قیمت‌های تازه و ارسال یک گزارش...")

    success = await send_fresh_report()

    if success:
        print("🏁 اجرای این نوبت با موفقیت تمام شد.")
    else:
        print("🏁 اجرای این نوبت با خطا تمام شد.")


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 ربات توسط کاربر متوقف شد.")