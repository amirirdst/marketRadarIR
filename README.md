# marketRadarIR

هسته اولیه ربات قیمت بازار برای Telegram.

## راه‌اندازی
1. Python 3.11 یا جدیدتر نصب باشد.
2. فایل `.env.example` را به `.env` تغییر نام دهید.
3. توکن BotFather را داخل `TELEGRAM_BOT_TOKEN` قرار دهید.
4. شناسه کانال را داخل `TELEGRAM_CHANNEL_ID` قرار دهید.
5. در پوشه پروژه اجرا کنید:
   `pip install -r requirements.txt`
6. تست:
   `python main.py`

فعلاً برای تست، منبع قیمت به‌صورت نمونه در نظر گرفته شده تا قبل از اتصال API واقعی، مسیر Telegram را تست کنیم.
