from loguru import logger
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from telegram_bot.config import dp
from telegram_bot.utils.misc.throttling import rate_limit

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from database.repositories.script import ScriptRepository, ScriptDB
from telegram_bot.keyboards.quest import get_markup

from telegram_bot.config import settings


@dp.callback_query_handler(lambda c: c.data == 'null')
@dp.message_handler(commands=['quest'])
@rate_limit(1)
async def command_run_quest(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))

    await run_quest(session, user_data, user_data.step)


@dp.callback_query_handler()
@rate_limit(1)
async def callback_run_quest(callback: types.CallbackQuery):
    session = SessionLocal()
    script_rep = ScriptRepository(session)
    titles = {script.title for script in await script_rep.get_all()}
    if callback.data not in titles:
        await session.close()
        return

    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=callback.from_user.id))

    await run_quest(session, user_data, callback.data)


async def run_quest(session, user_data: UserDataDB, new_step=settings.START_TITLE):
    user_data_rep = UserDataRepository(session)

    if user_data.quest_message_id:
        try:
            await dp.bot.edit_message_reply_markup(
                chat_id=user_data.tg_chat_id,
                message_id=user_data.quest_message_id,
                inline_message_id=None,
                reply_markup=None
            )
        except MessageNotModified as e:
            pass

    if new_step == 'остановка квеста':
        if user_data.is_in_quest:
            user_data = await user_data_rep.update(
                request_user_data=user_data,
                new_user_data=UserDataDB(
                    is_in_quest=False
                )
            )
            user_data.step = new_step

    elif user_data.step != new_step:
        user_data = await user_data_rep.update(
            request_user_data=user_data,
            new_user_data=UserDataDB(
                step=new_step
            )
        )

    if user_data.step != 'остановка квеста':
        if not user_data.is_in_quest:
            user_data = await user_data_rep.update(
                request_user_data=user_data,
                new_user_data=UserDataDB(
                    is_in_quest=True
                )
            )

    script = await ScriptRepository(session).get_one(ScriptDB(title=user_data.step))
    quest_message_id = None
    is_in_quest = user_data.is_in_quest
    if script is None:
        await dp.bot.send_message(
            chat_id=user_data.tg_chat_id,
            text='/start'
        )
        is_in_quest = False
    else:
        message = await dp.bot.send_message(
            chat_id=user_data.tg_chat_id,
            text=script.text,
            reply_markup=await get_markup(session, user_data.step, user_data)
        )
        quest_message_id = message.message_id

    user_data = await user_data_rep.update(
        request_user_data=UserDataDB(
            tg_chat_id=user_data.tg_chat_id
        ),
        new_user_data=UserDataDB(
            quest_message_id=quest_message_id,
            is_in_quest=is_in_quest
        )
    )

    await session.close()
