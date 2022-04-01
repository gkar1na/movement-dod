import logging
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from telegram_bot.config import dp
from telegram_bot.keyboards.quest import get_markup

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from database.repositories.script import ScriptRepository, ScriptDB

from telegram_bot.config import settings


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start'])
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
        except Exception as e:
            logger.error(e)
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
                    is_admin=False,
                    step=settings.WELCOME_TITLE
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
            quest_message_id=new_quest_message
        )
    )

    await session.close()
