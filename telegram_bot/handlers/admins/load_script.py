import re
import logging
from aiogram import types

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['load_script'])
async def run_quest(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))
    arguments = re.search(r'\S*docs.google.com/spreadsheets/d/\S*', message.get_args())
    arguments = arguments[0] if arguments else None
    if not user_data.is_admin:
        return
    await message.reply(f'Здесь будет обновление данных из таблицы:\n{arguments}')  # TODO
