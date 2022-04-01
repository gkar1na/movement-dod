from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from uuid import UUID, uuid4
from typing import Optional, List, Union, Any

from database.create_table import ScriptModel


class ScriptDB:
    __tablename__ = ScriptModel.__tablename__

    uid: Union[UUID, str, None]
    title: Optional[str]
    text: Optional[str]

    def __init__(self, uid='', title='', text=''):
        self.uid = uid
        self.title = title
        self.text = text

    def __repr__(self):
        return f'<ScriptDB(uid={self.uid}, title={self.title}, text={self.text})>'

    __str__ = __repr__

    def __eq__(self, other: Any):
        if not isinstance(other, ScriptDB):
            return False

        return (
                self.uid == other.uid and
                self.title == other.title and
                self.text == other.text
        )

    def __le__(self, other: Any):
        if not isinstance(other, ScriptDB):
            return False

        return (
                (self.uid == other.uid or self.uid == '') and
                (self.title == other.title or self.title == '') and
                (self.text == other.text or self.text == '')
        )

    def __ge__(self, other: Any):
        if not isinstance(other, ScriptDB):
            return False

        return (
                (self.uid == other.uid or other.uid == '') and
                (self.title == other.title or other.title == '') and
                (self.text == other.text or other.text == '')
        )


def fill_query(query, request_script: ScriptDB = '', new_script: ScriptDB = ''):
    is_query_empty = True

    if request_script != '':

        if request_script.uid != '':
            is_query_empty = False
            query = query.where(ScriptModel.uid == request_script.uid)

        if request_script.title != '':
            is_query_empty = False
            query = query.where(ScriptModel.title == request_script.title)

        if request_script.text != '':
            is_query_empty = False
            query = query.where(ScriptModel.text == request_script.text)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_script != '':

            if new_script.title != '':
                is_query_empty = False
                query = query.values(title=new_script.title)

            if new_script.text != '':
                is_query_empty = False
                query = query.values(text=new_script.text)

        if is_query_empty:
            return None

    return query


class ScriptRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, request_script: ScriptDB = '') -> List[Optional[ScriptDB]]:
        query = fill_query(select(ScriptModel), request_script)

        scripts = [
            ScriptDB(
                uid=script.uid,
                title=script.title,
                text=script.text
            ) for script in (await self.session.execute(query)).scalars()
        ]

        return scripts

    async def get_one(self, request_script: ScriptDB = '') -> Optional[ScriptDB]:
        scripts = await self.get_all(request_script)

        if scripts and scripts[0]:
            return scripts[0]
        return None

    async def delete(self, request_script: ScriptDB = '') -> Optional[ScriptDB]:
        query = fill_query(delete(ScriptModel), request_script)

        response_script = await self.get_one(request_script)
        await self.session.execute(query)
        await self.session.commit()

        return response_script

    async def add(
            self,
            request_scripts: Union[ScriptDB, List[ScriptDB]]
    ) -> Union[ScriptDB, List[ScriptDB], None]:
        if isinstance(request_scripts, ScriptDB):
            request_scripts = [request_scripts]

        for script in request_scripts:
            params = {}

            if script.uid != '':
                if isinstance(script.uid, str):
                    try:
                        params['uid'] = UUID(script.uid)
                    except ValueError:
                        raise ValueError(f'Unable to add new script '
                                         f'because a parameter "uid" is incorrect.')
                elif isinstance(script.uid, UUID):
                    params['uid'] = script.uid
            else:
                params['uid'] = uuid4()

            if script.title != '':
                params['title'] = script.title
            else:
                raise ValueError(f'Unable to add new script '
                                 f'because a parameter "title" does not exist.')

            if script.text != '':
                params['text'] = script.text
            else:
                raise ValueError(f'Unable to add new script '
                                 f'because a parameter "text" does not exist.')

            self.session.add(ScriptModel(**params))

        await self.session.commit()

        response_scripts = []
        for script in request_scripts:
            response_scripts.append(await self.get_one(script))

        if len(response_scripts) == 1:
            response_scripts = response_scripts[0]
        elif not len(response_scripts):
            response_scripts = None

        return response_scripts

    async def update(self, request_script: ScriptDB = '',
                     new_script: ScriptDB = '') -> Optional[ScriptDB]:
        query = fill_query(update(ScriptModel), request_script, new_script)
        if query is None:
            return None

        response_script = await self.get_one(request_script)
        await self.session.execute(query)
        await self.session.commit()

        return response_script
