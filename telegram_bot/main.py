import logging
from aiogram import executor, types

import telegram_bot.handlers

from telegram_bot.config import dp


logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply('I\'m just alive.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
