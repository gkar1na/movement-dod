from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from typing import Optional, List, Union

from database.create_table import ScriptModel


def fill_query(query, uid='', title='', text='', new_title='', new_text=''):
    is_query_empty = True

    if uid != '':
        is_query_empty = False
        query = query.where(ScriptModel.uid == uid)

    if title != '':
        is_query_empty = False
        query = query.where(ScriptModel.title == title)

    if text != '':
        is_query_empty = False
        query = query.where(ScriptModel.text == text)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_title != '':
            is_query_empty = False
            query = query.values(title=new_title)

        if new_text != '':
            is_query_empty = False
            query = query.values(text=new_text)

        if is_query_empty:
            return None

    return query


class ScriptRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, uid='', title='', text='') -> List[Optional[dict]]:
        query = fill_query(select(ScriptModel), uid, title, text)

        scripts = [
            {
                'uid': script.uid,
                'title': script.title,
                'text': script.text
            } for script in (await self.session.execute(query)).scalars()
        ]

        return scripts

    async def get_one(self, uid='', title='', text='') -> Optional[dict]:
        scripts = await self.get_all(
            uid=uid,
            title=title,
            text=text
        )

        if scripts and scripts[0]:
            return scripts[0]
        return None

    async def delete(self, uid='', title='', text='') -> None:
        query = fill_query(delete(ScriptModel), uid, title, text)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, scripts: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        if type(scripts) == dict:
            scripts = [scripts]

        return_scripts = []

        for script in scripts:
            params = {}

            if 'title' in script.keys():
                params['title'] = script['title']
            else:
                raise ValueError(f'Unable to add new script '
                                 f'because a parameter "title" does not exist.')

            if 'text' in script.keys():
                params['text'] = script['text']
            else:
                raise ValueError(f'Unable to add new script '
                                 f'because a parameter "text" does not exist.')

            self.session.add(ScriptModel(**params))

            return_scripts.append(params)

        await self.session.commit()

        if len(return_scripts) == 1:
            return_scripts = return_scripts[0]

        return return_scripts

    async def update(self, uid='', title='', text='', new_title='', new_text='') -> None:
        query = fill_query(update(ScriptModel), uid, title, text, new_title, new_text)
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
