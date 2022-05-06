from loguru import logger
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from telegram_bot.config import dp
from telegram_bot.utils.misc.throttling import rate_limit


@dp.message_handler(CommandHelp())
@rate_limit(1)
async def bot_help(message: types.Message):
    await message.reply('Ты можешь пройти квест, написав /start и '
                        'проследовав инструкции из следующих сообщений.')
