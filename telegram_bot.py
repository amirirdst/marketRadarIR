# -*- coding: utf-8 -*-

from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


async def send_report(report):
    async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=report,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )