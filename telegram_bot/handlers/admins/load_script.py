import re
import logging
from aiogram import types

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['load_script'])
async def run_quest(message: types.Message):
    session = SessionLocal()
    user_data = UserDataRepository(session)
    user = await user_data.get_one(tg_chat_id=message.from_user.id)
    arguments = re.search(r'\S*docs.google.com/spreadsheets/d/\S*', message.get_args())
    arguments = arguments[0] if arguments else None
    if not user['is_admin']:
        return
    await message.reply(f'Здесь будет обновление данных из таблицы:\n{arguments}')  # TODO
