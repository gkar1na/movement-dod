import logging
from aiogram import types
from uuid import UUID

from telegram_bot.config import dp

from telegram_bot.handlers.admins.authorization import read_token

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository


logger = logging.getLogger(__name__)


@dp.message_handler()
async def echo(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(tg_chat_id=message.from_user.id)
    if not user_data:
        try:
            user_data = await user_data_rep.add({
                'tg_chat_id': message.from_user.id
            })
        except Exception as e:
            logger.error(e)
        else:
            await message.reply('Ты добавлен в базу данных.')

    try:
        UUID(message.text, version=4)
    except ValueError:
        # if the user writes something other than the token
        await message.reply(message.text)  # TODO
    else:
        await read_token(message)

    await session.close()
