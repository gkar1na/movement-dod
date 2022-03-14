import logging
from typing import Optional
from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository
from database.repositories.button import ButtonRepository
from database.repositories.script import ScriptRepository

from telegram_bot.config import settings


logger = logging.getLogger(__name__)


async def get_markup(session, title: Optional[str]) -> InlineKeyboardMarkup:
    button_rep = ButtonRepository(session)
    script_rep = ScriptRepository(session)

    buttons = await button_rep.get_all(title_from=title)
    keyboard = []
    if buttons:
        keyboard.append([])
        for button in buttons:
            keyboard[-1].append(InlineKeyboardButton(
                text=button['text'],
                callback_data=(await script_rep.get_one(uid=button['title_to']))['title']
            ))

    stop_button = await button_rep.get_one(title_to=settings.STOP_TITLE)
    keyboard.append([
        InlineKeyboardButton(text=stop_button['text'], callback_data=stop_button['title_to'])
    ])

    return InlineKeyboardMarkup(keyboard)
