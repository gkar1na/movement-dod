from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete, update
from typing import Optional, List, Union

from create_table import ScriptModel


def fill_query(query, uid='', title='', text='',
               new_uid='', new_title='', new_text=''):
    if uid != '':
        query = query.where(ScriptModel.uid == uid)

    if title != '':
        query = query.where(ScriptModel.title == title)

    if text != '':
        query = query.where(ScriptModel.text == text)

    if new_uid != '':
        query = query.values(uid=new_uid)

    if new_title != '':
        query = query.values(title=title)

    if new_text != '':
        query = query.values(text=text)

    return query


class ScriptRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, uid='', title='', text='') -> List[Optional[dict]]:
        query = select(ScriptModel)

        query = fill_query(query, uid, title, text)

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
        query = delete(ScriptModel)

        query = fill_query(query, uid, title, text)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, scripts: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        query = select(ScriptModel).distinct()

        if type(scripts) == dict:
            scripts = [scripts]

        return_scripts = []

        for script in scripts:
            params = {}

            if 'uid' in script.keys():
                params['uid'] = script['uid']
            else:
                raise ValueError(f'Unable to add new script '
                                 f'because a parameter "uid" does not exist.')

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

    async def update(self, uid='', title='', text='',
                     new_uid='', new_title='', new_text='') -> None:
        query = update(ScriptModel)

        query = fill_query(query, uid, title, text, new_uid, new_title, new_text)

        await self.session.execute(query)
        await self.session.commit()
