import logging

from aiogram import Dispatcher

from telegram_bot.config import settings


async def on_startup_notify(dp: Dispatcher):
    for admin in settings.ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот запущен.")

        except Exception as e:
            logging.exception(e)


async def on_shutdown_notify(dp: Dispatcher):
    for admin in settings.ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот остановлен.")

        except Exception as e:
            logging.exception(e)
