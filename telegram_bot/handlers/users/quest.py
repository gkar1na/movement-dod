import logging
from aiogram import types

from telegram_bot.config import dp

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository
from telegram_bot.keyboards.quest import get_markup

from telegram_bot.config import settings


logger = logging.getLogger(__name__)


@dp.message_handler(commands=['quest'])
async def run_quest(message: types.Message):
    await message.reply(f'start quest')
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(tg_chat_id=message.from_user.id)

    if user_data['quest_message_id']:
        dp.bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=user_data['quest_message_id'],
            inline_message_id=None,
            reply_markup=None
        )

    if not user_data['step']:
        await user_data_rep.update(uid=user_data['uid'], new_step=settings.START_TITLE)
        user_data['step'] = settings.START_TITLE

    reply_markup = await get_markup(session, user_data['step'])



    await session.close()
