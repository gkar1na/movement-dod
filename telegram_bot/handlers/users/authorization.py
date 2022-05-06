from loguru import logger
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from telegram_bot.config import dp
from telegram_bot.keyboards.quest import get_markup

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from database.repositories.script import ScriptRepository, ScriptDB

from telegram_bot.config import settings
from telegram_bot.utils.misc.throttling import rate_limit


@dp.message_handler(commands=['start'])
@rate_limit(1)
async def send_welcome(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))
    if not user_data:
        try:
            user_data = await user_data_rep.add(UserDataDB(
                tg_chat_id=message.from_user.id,
                step=settings.WELCOME_TITLE
            ))
            logger.warning(f'Add user '
                           f'id={message.from_user.id}, username={message.from_user.username}')
        except Exception as e:
            logger.error(f'Adding user '
                         f'id={message.from_user.id}, username={message.from_user.username}: {e}')

    elif user_data.quest_message_id:
        try:
            await dp.bot.edit_message_reply_markup(
                chat_id=user_data.tg_chat_id,
                message_id=user_data.quest_message_id,
                inline_message_id=None,
                reply_markup=None
            )
            user_data = await user_data_rep.update(
                request_user_data=user_data,
                new_user_data=UserDataDB(
                    step=settings.WELCOME_TITLE,
                    is_in_quest=False
                )
            )
        except MessageNotModified:
            pass

    new_quest_message = await message.reply(
        (await ScriptRepository(session).get_one(ScriptDB(title=settings.WELCOME_TITLE))).text,
        reply_markup=await get_markup(session, settings.WELCOME_TITLE, user_data)
    )
    user_data = await user_data_rep.update(
        request_user_data=user_data,
        new_user_data=UserDataDB(
            quest_message_id=new_quest_message.message_id
        )
    )

    await session.close()
