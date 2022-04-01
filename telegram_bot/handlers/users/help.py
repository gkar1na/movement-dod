import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from telegram_bot.config import dp
from telegram_bot.utils.misc.throttling import rate_limit

logger = logging.getLogger(__name__)


@dp.message_handler(CommandHelp())
@rate_limit(5)
async def bot_help(message: types.Message):
    await message.reply('I\'m just alive.')
