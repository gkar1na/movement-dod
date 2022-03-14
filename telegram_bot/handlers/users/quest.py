import logging
from aiogram import types

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository

from telegram_bot.config import settings


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['quest'])
async def run_quest(message: types.Message):
    await message.reply(f'start quest')
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(tg_chat_id=message.from_user.id)
    if not user_data['step']:
        await user_data_rep.update(uid=user_data['uid'], new_step=settings.START_TITLE)
        user_data['step'] = settings.START_TITLE

    # TODO

    await session.close()
