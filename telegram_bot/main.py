from aiogram import executor

# TODO idk how install own module by "pip install -Ue ." – it doesn't work
import sys
sys.path.append('..')

from telegram_bot import handlers, middlewares
from telegram_bot.utils.set_bot_commands import set_default_commands
from telegram_bot.utils.notify_admins import on_startup_notify, on_shutdown_notify
from loguru import logger

from telegram_bot.config import dp


async def on_startup(dispatcher):
    from utils.misc import logging
    logging.setup()
    from database.repositories.script import ScriptRepository
    from database.create_table import SessionLocal
    from spreadsheet_parser.sheet2db import convert
    from spreadsheet_parser.config import settings
    from sqlalchemy.exc import ProgrammingError

    session = SessionLocal()
    try:
        script_repository = ScriptRepository(session)
        scripts = await script_repository.get_one()
    except ProgrammingError as e:
        scripts = []
    await session.close()

    if not scripts:
        await convert(
            settings.SPREADSHEET_ID,
            settings.DB_PATH,
            creds_file_name='../spreadsheet_parser/credentials.json',
            token_file_name='../spreadsheet_parser/token.json'
        )

    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)


async def on_shutdown(dispatcher):
    await on_shutdown_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
