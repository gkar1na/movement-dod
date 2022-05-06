from loguru import logger
from aiogram import Dispatcher

from database.create_table import SessionLocal
from database.repositories.token import TokenRepository, TokenDB
from telegram_bot.config import settings


async def on_startup_notify(dp: Dispatcher):
    session = SessionLocal()
    token_rep = TokenRepository(session)
    tokens = list(await token_rep.get_all(TokenDB(is_active=True)))
    if len(tokens) < 2:
        tokens.append(await token_rep.add(TokenDB()))
        tokens.append(await token_rep.add(TokenDB()))

    for i in range(len(tokens)):
        tokens[i] = str(tokens[i].uid)

    for admin in settings.ADMINS:
        try:
            await dp.bot.send_message(
                admin,
                "Бот запущен.\nСвободные токены:\n`" + '`\n`'.join(tokens) + '`',
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f'{e}')

    await session.close()


async def on_shutdown_notify(dp: Dispatcher):
    for admin in settings.ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот остановлен.")

        except Exception as e:
            logger.error(f'{e}')
