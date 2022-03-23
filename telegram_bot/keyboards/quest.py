import logging
from typing import Optional
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from database.repositories.button import ButtonRepository

from telegram_bot.config import settings


logger = logging.getLogger(__name__)


async def get_markup(session, title: Optional[str], user_data: dict) -> InlineKeyboardMarkup:
    button_rep = ButtonRepository(session)
    buttons = await button_rep.get_all(title_from=title)
    keyboard = InlineKeyboardMarkup()
    if buttons:
        for button in buttons:
            if button['title_to'] is None:
                callback_data = user_data['step']
            else:
                callback_data = button['title_to']
            keyboard.add(InlineKeyboardButton(
                text=button['text'],
                callback_data=callback_data
            ))

    if user_data['is_in_quest']:
        stop_button = await button_rep.get_one(title_to=settings.STOP_TITLE)
        if stop_button:
            keyboard.add(
                InlineKeyboardButton(text=stop_button['text'], callback_data=stop_button['title_to'])
            )

    return keyboard
