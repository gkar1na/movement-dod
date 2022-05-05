import re
import logging
from aiogram import types
from telegram_bot.config import dp
from telegram_bot.utils.misc.throttling import rate_limit

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from spreadsheet_parser.sheet2db import convert
from spreadsheet_parser.config import settings


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['load_script'])
@rate_limit(10)
async def run_quest(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))
    if not user_data.is_admin:
        await session.close()
        return

    link = message.get_args()
    index = link.rfind('docs.google.com/spreadsheets/d/')
    if index == -1:
        await message.reply(f'Неверная ссылка: "{link}"')
        await session.close()
        return
    spreadsheet_id = link[index + 31:]
    index = spreadsheet_id.find('/')
    if index != -1:
        spreadsheet_id = spreadsheet_id[:index]

    await message.reply(f'Здесь будет обновление данных из таблицы:\n'
                        f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}')

    try:
        await convert(
            spreadsheet_id=spreadsheet_id,
            db_url=settings.DB_PATH,
            creds_file_name='../spreadsheet_parser/credentials.json',
            token_file_name='../spreadsheet_parser/token.json'
        )
    except Exception as e:
        logger.error(e)
        await message.reply(f'ERROR.')
    else:
        await message.reply(f'DB is up-to-date.')

    await session.close()
