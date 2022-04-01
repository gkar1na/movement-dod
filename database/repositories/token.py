from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from uuid import UUID, uuid4
from typing import Optional, List, Union, Any

from database.create_table import TokenModel


class TokenDB:
    __tablename__ = 'token'

    uid: Union[UUID, str, None]
    is_active: Union[bool, str, None]
    tg_chat_id: Union[int, str, None]

    def __init__(self, uid='', is_active='', tg_chat_id=''):
        self.uid = uid
        self.is_active = is_active
        self.tg_chat_id = tg_chat_id

    def __repr__(self):
        return f'<TokenDB(uid={self.uid}, is_active={self.is_active}, ' \
               f'tg_chat_id={self.tg_chat_id})>'

    __str__ = __repr__

    def __eq__(self, other: Any):
        if not isinstance(other, TokenDB):
            return False

        return (
                self.uid == other.uid and
                self.is_active == other.is_active and
                self.tg_chat_id == other.tg_chat_id
        )

    def __le__(self, other: Any):
        if not isinstance(other, TokenDB):
            return False

        return (
                (self.uid == other.uid or self.uid == '') and
                (self.is_active == other.is_active or self.is_active == '') and
                (self.tg_chat_id == other.tg_chat_id or self.tg_chat_id == '')
        )

    def __ge__(self, other: Any):
        if not isinstance(other, TokenDB):
            return False

        return (
                (self.uid == other.uid or other.uid == '') and
                (self.is_active == other.is_active or other.is_active == '') and
                (self.tg_chat_id == other.tg_chat_id or other.tg_chat_id == '')
        )


def fill_query(query, request_token: TokenDB = '', new_token: TokenDB = ''):
    is_query_empty = True

    if request_token != '':

        if request_token.uid != '':
            is_query_empty = False
            query = query.where(TokenModel.uid == request_token.uid)

        if request_token.is_active != '':
            is_query_empty = False
            query = query.where(TokenModel.is_active == request_token.is_active)

        if request_token.tg_chat_id != '':
            is_query_empty = False
            query = query.where(TokenModel.tg_chat_id == request_token.tg_chat_id)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_token != '':

            if new_token.is_active != '':
                is_query_empty = False
                query = query.values(is_active=new_token.is_active)

            if new_token.tg_chat_id != '':
                is_query_empty = False
                query = query.values(tg_chat_id=new_token.tg_chat_id)

        if is_query_empty:
            return None

    return query


class TokenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, request_token: TokenDB = '') -> List[Optional[TokenDB]]:
        query = fill_query(select(TokenModel), request_token)

        tokens = [
            TokenDB(
                uid=token.uid,
                is_active=token.is_active,
                tg_chat_id=token.tg_chat_id
            ) for token in (await self.session.execute(query)).scalars()
        ]

        return tokens

    async def get_one(self, request_token: TokenDB = '') -> Optional[TokenDB]:
        tokens = await self.get_all(request_token)

        if tokens and tokens[0]:
            return tokens[0]
        return None

    async def delete(self, request_token: TokenDB = '') -> Optional[TokenDB]:
        query = fill_query(delete(TokenModel), request_token)

        response_token = await self.get_one(request_token)
        await self.session.execute(query)
        await self.session.commit()

        return request_token

    async def add(
            self,
            request_tokens: Union[TokenDB, List[TokenDB]]
    ) -> Union[TokenDB, List[TokenDB], None]:
        if isinstance(request_tokens, TokenDB):
            request_tokens = [request_tokens]

        for token in request_tokens:
            params = {}

            if token.uid != '':
                if isinstance(token.uid, str):
                    try:
                        params['uid'] = UUID(token.uid)
                    except ValueError:
                        raise ValueError(f'Unable to add new token '
                                         f'because a parameter "uid" is incorrect.')
                elif isinstance(token.uid, UUID):
                    params['uid'] = token.uid
            else:
                params['uid'] = uuid4()

            if token.is_active != '':
                params['is_active'] = token.is_active

            if token.tg_chat_id != '':
                params['tg_chat_id'] = token.tg_chat_id

            self.session.add(TokenModel(**params))

        await self.session.commit()

        response_tokens = []
        for token in request_tokens:
            response_tokens.append(await self.get_one(token))

        if len(response_tokens) == 1:
            response_tokens = response_tokens[0]
        elif not len(response_tokens):
            response_tokens = None

        return response_tokens

    async def update(self, request_token: TokenDB = '',
                     new_token: TokenDB = '') -> Optional[TokenDB]:
        query = fill_query(update(TokenModel), request_token, new_token)
        if query is None:
            return None

        response_token = await self.get_one(request_token)
        await self.session.execute(query)
        await self.session.commit()

        return response_token
