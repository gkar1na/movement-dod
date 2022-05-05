import logging
from aiogram import types
from telegram_bot.config import dp
from telegram_bot.utils.misc.throttling import rate_limit

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from database.repositories.token import TokenRepository, TokenDB


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['create_token'])
@rate_limit(10)
async def run_quest(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    toker_rep = TokenRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))
    if not user_data.is_admin:
        await session.close()
        return

    await message.reply(f'Добавляю токен.')

    try:
        token = await toker_rep.add(TokenDB())
    except Exception as e:
        logger.error(e)
        await message.reply(f'ERROR.')
    else:
        await message.reply(f'Токен добавлен: "`{token.uid}`".', parse_mode='Markdown')

    await session.close()
