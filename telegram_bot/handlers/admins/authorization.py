from loguru import logger
from aiogram import types

from database.create_table import SessionLocal
from database.repositories.user_data import UserDataRepository, UserDataDB
from database.repositories.token import TokenRepository, TokenDB


async def read_token(message: types.Message):
    session = SessionLocal()
    user_data_rep = UserDataRepository(session)
    user_data = await user_data_rep.get_one(UserDataDB(tg_chat_id=message.from_user.id))
    if user_data.is_admin:
        await message.reply(f'Ты уже админ, успокойся.')
        await session.close()
        return

    token_rep = TokenRepository(session)
    token = await token_rep.get_one(TokenDB(uid=message.text))
    if token and token.is_active:
        token = await token_rep.update(
            request_token=token,
            new_token=TokenDB(
                is_active=False,
                tg_chat_id=message.from_user.id
            )
        )
        user_data = await user_data_rep.update(
            request_user_data=user_data,
            new_user_data=UserDataDB(
                is_admin=True,
            )
        )
        await message.reply(f'Токен успешно использован.\nВы добавлены в админы.')
        logger.warning(f'New admin: '
                       f'id={message.from_user.id}, username={message.from_user.username}')

    await session.close()
