import logging
from aiogram import types

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    session = SessionLocal()
    user_data = UserDataRepository(session)
    user = await user_data.get_one(tg_chat_id=message.from_user.id)
    if user:
        await message.reply('You are already in the database.')
    else:
        try:
            await user_data.add({
                'tg_chat_id': message.from_user.id
            })
        except Exception as e:
            logger.error(e)
        else:
            await message.reply('You are now in the database.')
    await session.close()
