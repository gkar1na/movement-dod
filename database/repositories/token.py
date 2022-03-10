from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from typing import Optional, List, Union

from database.create_table import TokenModel


def fill_query(query, uid='', is_active: Optional[bool] = '', tg_chat_id: Optional[int] = '',
               new_is_active: Optional[bool] = '', new_tg_chat_id: Optional[int] = ''):
    is_query_empty = True

    if uid != '':
        is_query_empty = False
        query = query.where(TokenModel.uid == uid)

    if is_active != '':
        is_query_empty = False
        query = query.where(TokenModel.is_active == is_active)

    if tg_chat_id != '':
        is_query_empty = False
        query = query.where(TokenModel.tg_chat_id == tg_chat_id)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_is_active != '':
            is_query_empty = False
            query = query.values(is_active=new_is_active)

        if new_tg_chat_id != '':
            is_query_empty = False
            query = query.values(tg_chat_id=new_tg_chat_id)

        if is_query_empty:
            return None

    return query


class TokenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, uid='', is_active: Optional[bool] = '',
                      tg_chat_id: Optional[int] = '') -> List[Optional[dict]]:
        query = fill_query(select(TokenModel), uid, is_active, tg_chat_id)

        tokens = [
            {
                'uid': token.uid,
                'is_active': token.is_active,
                'tg_chat_id': token.tg_chat_id
            } for token in (await self.session.execute(query)).scalars()
        ]

        return tokens

    async def get_one(self, uid='', is_active: Optional[bool] = '',
                      tg_chat_id: Optional[int] = '') -> Optional[dict]:
        tokens = await self.get_all(
            uid=uid,
            is_active=is_active,
            tg_chat_id=tg_chat_id
        )

        if tokens and tokens[0]:
            return tokens[0]
        return None

    async def delete(self, uid='', is_active: Optional[bool] = '',
                     tg_chat_id: Optional[int] = '') -> None:
        query = fill_query(delete(TokenModel), uid, is_active, tg_chat_id)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, tokens: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        if type(tokens) == dict:
            tokens = [tokens]

        return_tokens = []

        for token in tokens:
            params = {}

            if 'is_active' in token.keys():
                params['is_active'] = token['is_active']

            if 'tg_chat_id' in token.keys():
                params['tg_chat_id'] = token['tg_chat_id']

            self.session.add(TokenModel(**params))

            return_tokens.append(params)

        await self.session.commit()

        if len(return_tokens) == 1:
            return_tokens = return_tokens[0]

        return return_tokens

    async def update(self, uid='', is_active: Optional[bool] = '',
                     tg_chat_id: Optional[int] = '', new_is_active: Optional[bool] = '',
                     new_tg_chat_id: Optional[int] = '') -> None:
        query = fill_query(
            update(TokenModel),
            uid, is_active, tg_chat_id,
            new_is_active, new_tg_chat_id
        )
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
