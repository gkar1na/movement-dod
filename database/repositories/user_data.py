from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from uuid import UUID, uuid4
from typing import Optional, List, Union, Any

from database.create_table import UserDataModel


class UserDataDB:
    __tablename__ = 'user_data'

    uid: Union[UUID, str, None]
    tg_chat_id: Union[int, str, None]
    is_admin: Union[int, str, None]
    step: Optional[str]
    quest_message_id: Union[int, str, None]
    is_in_quest: Union[bool, str, None]

    def __init__(self, uid='', tg_chat_id='', is_admin='', step='',
                 quest_message_id='', is_in_quest=''):
        self.uid = uid
        self.tg_chat_id = tg_chat_id
        self.is_admin = is_admin
        self.step = step
        self.quest_message_id = quest_message_id
        self.is_in_quest = is_in_quest

    def __repr__(self):
        return f'<UserDataDB(uid={self.uid}, tg_chat_id={self.tg_chat_id}, ' \
               f'is_admin={self.is_admin}, step={self.step}, ' \
               f'quest_message_id={self.quest_message_id}, is_in_quest={self.is_in_quest})>'

    __str__ = __repr__

    def __eq__(self, other: Any):
        if not isinstance(other, UserDataDB):
            return False

        return (
                self.uid == other.uid and
                self.tg_chat_id == other.tg_chat_id and
                self.is_admin == other.is_admin and
                self.step == other.step and
                self.quest_message_id == other.quest_message_id and
                self.is_in_quest == other.is_in_quest
        )

    def __le__(self, other: Any):
        if not isinstance(other, UserDataDB):
            return False

        return (
                (self.uid == other.uid or self.uid == '') and
                (self.tg_chat_id == other.tg_chat_id or self.tg_chat_id == '') and
                (self.is_admin == other.is_admin or self.is_admin == '') and
                (self.step == other.step or self.step == '') and
                (self.quest_message_id == other.quest_message_id or self.quest_message_id == '') and
                (self.is_in_quest == other.is_in_quest or self.is_in_quest == '')
        )

    def __ge__(self, other: Any):
        if not isinstance(other, UserDataDB):
            return False

        return (
                (self.uid == other.uid or other.uid == '') and
                (self.tg_chat_id == other.tg_chat_id or other.tg_chat_id == '') and
                (self.is_admin == other.is_admin or other.is_admin == '') and
                (self.step == other.step or other.step == '') and
                (
                        self.quest_message_id == other.quest_message_id or
                        other.quest_message_id == ''
                ) and
                (self.is_in_quest == other.is_in_quest or other.is_in_quest == '')
        )


def fill_query(query, request_user_data: UserDataDB = '', new_user_data: UserDataDB = ''):
    is_query_empty = True

    if request_user_data != '':

        if request_user_data.uid != '':
            is_query_empty = False
            query = query.where(UserDataModel.uid == request_user_data.uid)

        if request_user_data.tg_chat_id != '':
            is_query_empty = False
            query = query.where(UserDataModel.tg_chat_id == request_user_data.tg_chat_id)

        if request_user_data.is_admin != '':
            is_query_empty = False
            query = query.where(UserDataModel.is_admin == request_user_data.is_admin)

        if request_user_data.step != '':
            is_query_empty = False
            query = query.where(UserDataModel.step == request_user_data.step)

        if request_user_data.quest_message_id != '':
            is_query_empty = False
            query = query.where(
                UserDataModel.quest_message_id == request_user_data.quest_message_id
            )

        if request_user_data.is_in_quest != '':
            is_query_empty = False
            query = query.where(UserDataModel.is_in_quest == request_user_data.is_in_quest)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_user_data != '':

            if new_user_data.tg_chat_id != '':
                is_query_empty = False
                query = query.values(tg_chat_id=new_user_data.tg_chat_id)

            if new_user_data.is_admin != '':
                is_query_empty = False
                query = query.values(is_admin=new_user_data.is_admin)

            if new_user_data.step != '':
                is_query_empty = False
                query = query.values(step=new_user_data.step)

            if new_user_data.quest_message_id != '':
                is_query_empty = False
                query = query.values(quest_message_id=new_user_data.quest_message_id)

            if new_user_data.is_in_quest != '':
                is_query_empty = False
                query = query.values(is_in_quest=new_user_data.is_in_quest)

        if is_query_empty:
            return None

    return query


class UserDataRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, request_user_data: UserDataDB = '') -> List[Optional[UserDataDB]]:
        query = fill_query(select(UserDataModel), request_user_data)

        users_data = [
            UserDataDB(
                uid=user_data.uid,
                tg_chat_id=user_data.tg_chat_id,
                is_admin=user_data.is_admin,
                step=user_data.step,
                quest_message_id=user_data.quest_message_id,
                is_in_quest=user_data.is_in_quest
            ) for user_data in (await self.session.execute(query)).scalars()
        ]

        return users_data

    async def get_one(self, request_user_data: UserDataDB = '') -> Optional[UserDataDB]:
        users_data = await self.get_all(request_user_data)

        if users_data and users_data[0]:
            return users_data[0]
        return None

    async def delete(self, request_user_data: UserDataDB = '') -> None:
        query = fill_query(delete(UserDataModel), request_user_data)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(
            self,
            request_users_data: Union[UserDataDB, List[UserDataDB]]
    ) -> Union[UserDataDB, List[UserDataDB], None]:
        if isinstance(request_users_data, UserDataDB):
            request_users_data = [request_users_data]

        for user_data in request_users_data:
            params = {}

            if user_data.uid != '':
                if isinstance(user_data.uid, str):
                    try:
                        params['uid'] = UUID(user_data.uid)
                    except ValueError:
                        raise ValueError(f'Unable to add new user_data '
                                         f'because a parameter "uid" is incorrect.')
                elif isinstance(user_data.uid, UUID):
                    params['uid'] = user_data.uid
            else:
                params['uid'] = uuid4()

            if user_data.tg_chat_id:
                params['tg_chat_id'] = user_data.tg_chat_id
            else:
                raise ValueError(f'Unable to add new user_data '
                                 f'because a parameter "tg_chat_id" does not exist.')

            if user_data.is_admin:
                params['is_admin'] = user_data.is_admin

            if user_data.step:
                params['step'] = user_data.step

            if user_data.quest_message_id:
                params['quest_message_id'] = user_data.quest_message_id

            if user_data.is_in_quest:
                params['is_in_quest'] = user_data.is_in_quest

            self.session.add(UserDataModel(**params))

        await self.session.commit()

        response_users_data = []
        for user_data in request_users_data:
            response_users_data.append(await self.get_one(user_data))

        if len(response_users_data) == 1:
            response_users_data = response_users_data[0]
        elif not len(response_users_data):
            response_users_data = None

        return response_users_data

    async def update(self, request_user_data: UserDataDB = '',
                     new_user_data: UserDataDB = '') -> None:
        query = fill_query(update(UserDataModel), request_user_data, new_user_data)
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
