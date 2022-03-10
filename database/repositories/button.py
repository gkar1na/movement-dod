from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from typing import Optional, List, Union

from database.create_table import ButtonModel


def fill_query(query, uid='', title_from='', text='', title_to='',
               new_title_from='', new_text='', new_title_to=''):
    is_query_empty = True

    if uid != '':
        is_query_empty = False
        query = query.where(ButtonModel.uid == uid)

    if title_from != '':
        is_query_empty = False
        query = query.where(ButtonModel.title_from == title_from)

    if text != '':
        is_query_empty = False
        query = query.where(ButtonModel.text == text)

    if title_to != '':
        is_query_empty = False
        query = query.where(ButtonModel.title_to == title_to)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_title_from != '':
            is_query_empty = False
            query = query.values(title_from=new_title_from)

        if new_text != '':
            is_query_empty = False
            query = query.values(text=new_text)

        if new_title_to != '':
            is_query_empty = False
            query = query.values(title_to=new_title_to)

        if is_query_empty:
            return None

    return query


class ButtonRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, uid='', title_from='', text='', title_to='') -> List[Optional[dict]]:
        query = fill_query(select(ButtonModel), uid, title_from, text, title_to)

        buttons = [
            {
                'uid': button.uid,
                'title_from': button.title_from,
                'text': button.text,
                'title_to': button.title_to
            } for button in (await self.session.execute(query)).scalars()
        ]

        return buttons

    async def get_one(self, uid='', title_from='', text='', title_to='') -> Optional[dict]:
        buttons = await self.get_all(
            uid=uid,
            title_from=title_from,
            text=text,
            title_to=title_to
        )

        if buttons and buttons[0]:
            return buttons[0]
        return None

    async def delete(self, uid='', title_from='', text='', title_to='') -> None:
        query = fill_query(delete(ButtonModel), uid, title_from, text, title_to)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, buttons: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        if type(buttons) == dict:
            buttons = [buttons]

        return_buttons = []

        for button in buttons:
            params = {}

            if 'title_from' in button.keys():
                params['title_from'] = button['title_from']
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "title_from" does not exist.')

            if 'text' in button.keys():
                params['text'] = button['text']
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "text" does not exist.')

            if 'title_to' in button.keys():
                params['title_to'] = button['title_to']
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "title_to" does not exist.')

            self.session.add(ButtonModel(**params))

            return_buttons.append(params)

        await self.session.commit()

        if len(return_buttons) == 1:
            return_buttons = return_buttons[0]

        return return_buttons

    async def update(self, uid='', title_from='', text='', title_to='',
                     new_title_from='', new_text='', new_title_to='') -> None:
        query = fill_query(
            update(ButtonModel),
            uid, title_from, text, title_to,
            new_title_from, new_text, new_title_to
        )
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
