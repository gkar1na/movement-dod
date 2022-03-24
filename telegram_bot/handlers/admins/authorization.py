import logging
from aiogram import types

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository
from database.repositories.token import TokenRepository


logger = logging.getLogger(__name__)


async def read_token(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(tg_chat_id=message.from_user.id)
    if user_data['is_admin']:
        await message.reply(f'Ты уже админ, успокойся.')

    token_rep = TokenRepository(session)
    token = await token_rep.get_one(uid=message.text)
    if token and token['is_active']:
        await token_rep.update(
            uid=token['uid'],
            new_is_active=False,
            new_tg_chat_id=message.from_user.id
        )
        await user_data_rep.update(uid=user_data['uid'], new_is_admin=True)
        await message.reply(f'Токен успешно использован.\nВы добавлены в админы.')

    await session.close()
