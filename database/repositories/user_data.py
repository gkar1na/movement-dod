from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from typing import Optional, List, Union

from database.create_table import UserDataModel


def fill_query(query,
               uid='', tg_chat_id: Optional[int] = '', is_admin: Optional[bool] = '', step='',
               new_tg_chat_id: Optional[int] = '', new_is_admin: Optional[bool] = '', new_step=''):
    is_query_empty = True

    if uid != '':
        is_query_empty = False
        query = query.where(UserDataModel.uid == uid)

    if tg_chat_id != '':
        is_query_empty = False
        query = query.where(UserDataModel.tg_chat_id == tg_chat_id)

    if is_admin != '':
        is_query_empty = False
        query = query.where(UserDataModel.is_admin == is_admin)

    if step != '':
        is_query_empty = False
        query = query.where(UserDataModel.step == step)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_tg_chat_id != '':
            is_query_empty = False
            query = query.values(tg_chat_id=new_tg_chat_id)

        if new_is_admin != '':
            is_query_empty = False
            query = query.values(is_admin=new_is_admin)

        if new_step != '':
            is_query_empty = False
            query = query.values(step=new_step)

        if is_query_empty:
            return None

    return query


class UserDataRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, uid='', tg_chat_id: Optional[int] = '',
                      is_admin: Optional[bool] = '', step='') -> List[Optional[dict]]:
        query = fill_query(select(UserDataModel), uid, tg_chat_id, is_admin, step)

        users_data = [
            {
                'uid': user_data.uid,
                'tg_chat_id': user_data.tg_chat_id,
                'is_admin': user_data.is_admin,
                'step': user_data.step
            } for user_data in (await self.session.execute(query)).scalars()
        ]

        return users_data

    async def get_one(self, uid='', tg_chat_id: Optional[int] = '',
                      is_admin: Optional[bool] = '', step='') -> Optional[dict]:
        users_data = await self.get_all(
            uid=uid,
            tg_chat_id=tg_chat_id,
            is_admin=is_admin,
            step=step
        )

        if users_data and users_data[0]:
            return users_data[0]
        return None

    async def delete(self, uid='', tg_chat_id: Optional[int] = '',
                     is_admin: Optional[bool] = '', step='') -> None:
        query = fill_query(delete(UserDataModel), uid, tg_chat_id, is_admin, step)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, users_data: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        if type(users_data) == dict:
            users_data = [users_data]

        return_users_data = []

        for user_data in users_data:
            params = {}

            if 'tg_chat_id' in user_data.keys():
                params['tg_chat_id'] = user_data['tg_chat_id']
            else:
                raise ValueError(f'Unable to add new user_data '
                                 f'because a parameter "tg_chat_id" does not exist.')

            if 'is_admin' in user_data.keys():
                params['is_admin'] = user_data['is_admin']

            if 'step' in user_data.keys():
                params['step'] = user_data['step']

            self.session.add(UserDataModel(**params))

            return_users_data.append(params)

        await self.session.commit()

        if len(return_users_data) == 1:
            return_users_data = return_users_data[0]

        return return_users_data

    async def update(self, uid='', tg_chat_id: Optional[int] = '',
                     is_admin: Optional[bool] = '', step='', new_tg_chat_id: Optional[int] = '',
                     new_is_admin: Optional[bool] = '', new_step='') -> None:
        query = fill_query(
            update(UserDataModel),
            uid, tg_chat_id, is_admin, step,
            new_tg_chat_id, new_is_admin, new_step
        )
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
