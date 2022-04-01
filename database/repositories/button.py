from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.expression import select, delete, update
from uuid import UUID, uuid4
from typing import Optional, List, Union, Any

from database.create_table import ButtonModel


class ButtonDB:
    __tablename__ = ButtonModel.__tablename__

    uid: Union[UUID, str, None]
    title_from: Union[str, None]
    text: str
    title_to: Union[str, None]

    def __init__(self, uid='', title_from='', text='', title_to=''):
        self.uid = uid
        self.title_from = title_from
        self.text = text
        self.title_to = title_to

    def __repr__(self):
        return f'<ButtonDB(uid={self.uid}, title_from={self.title_from}, ' \
               f'text={self.text}, title_to={self.title_to})>'

    __str__ = __repr__

    def __eq__(self, other: Any):
        if not isinstance(other, ButtonDB):
            return False

        return (
                self.uid == other.uid and
                self.title_from == other.title_from and
                self.text == other.text and
                self.title_to == other.title_to
        )

    def __le__(self, other: Any):
        if not isinstance(other, ButtonDB):
            return False

        return (
                (self.uid == other.uid or self.uid == '') and
                (self.title_from == other.title_from or self.title_from == '') and
                (self.text == other.text or self.text == '') and
                (self.title_to == other.title_to or self.title_to == '')
        )

    def __ge__(self, other: Any):
        if not isinstance(other, ButtonDB):
            return False

        return (
                (self.uid == other.uid or other.uid == '') and
                (self.title_from == other.title_from or other.title_from == '') and
                (self.text == other.text or other.text == '') and
                (self.title_to == other.title_to or other.title_to == '')
        )


def fill_query(query, request_button: ButtonDB = '', new_button: ButtonDB = ''):
    is_query_empty = True

    if request_button != '':

        if request_button.uid != '':
            is_query_empty = False
            query = query.where(ButtonModel.uid == request_button.uid)

        if request_button.title_from != '':
            is_query_empty = False
            query = query.where(ButtonModel.title_from == request_button.title_from)

        if request_button.text != '':
            is_query_empty = False
            query = query.where(ButtonModel.text == request_button.text)

        if request_button.title_to != '':
            is_query_empty = False
            query = query.where(ButtonModel.title_to == request_button.title_to)

    if isinstance(query, Update):
        if is_query_empty:
            return None
        is_query_empty = True

        if new_button != '':

            if new_button.title_from != '':
                is_query_empty = False
                query = query.values(title_from=new_button.title_from)

            if new_button.text != '':
                is_query_empty = False
                query = query.values(text=new_button.text)

            if new_button.title_to != '':
                is_query_empty = False
                query = query.values(title_to=new_button.title_to)

        if is_query_empty:
            return None

    return query


class ButtonRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, request_button: ButtonDB = '') -> List[Optional[ButtonDB]]:
        query = fill_query(select(ButtonModel), request_button)

        buttons = [
            ButtonDB(
                uid=button.uid,
                title_from=button.title_from,
                text=button.text,
                title_to=button.title_to
            ) for button in (await self.session.execute(query)).scalars()
        ]

        return buttons

    async def get_one(self, request_button: ButtonDB = '') -> Optional[ButtonDB]:
        buttons = await self.get_all(request_button)

        if buttons and buttons[0]:
            return buttons[0]
        return None

    async def delete(self, request_button: ButtonDB = '') -> None:
        query = fill_query(delete(ButtonModel), request_button)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(
            self,
            request_buttons: Union[ButtonDB, List[ButtonDB]]
    ) -> Union[ButtonDB, List[ButtonDB], None]:
        if isinstance(request_buttons, ButtonDB):
            request_buttons = [request_buttons]

        for button in request_buttons:
            params = {}

            if button.uid != '':
                if isinstance(button.uid, str):
                    try:
                        params['uid'] = UUID(button.uid)
                    except ValueError:
                        raise ValueError(f'Unable to add new button '
                                         f'because a parameter "uid" is incorrect.')
                elif isinstance(button.uid, UUID):
                    params['uid'] = button.uid
            else:
                params['uid'] = uuid4()

            if button.title_from != '':
                params['title_from'] = button.title_from
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "title_from" does not exist.')

            if button.text != '':
                params['text'] = button.text
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "text" does not exist.')

            if button.title_to:
                params['title_to'] = button.title_to
            else:
                raise ValueError(f'Unable to add new button '
                                 f'because a parameter "title_to" does not exist.')

            self.session.add(ButtonModel(**params))

        await self.session.commit()

        response_buttons = []
        for button in request_buttons:
            response_buttons.append(await self.get_one(button))

        if len(response_buttons) == 1:
            response_buttons = response_buttons[0]
        elif not len(response_buttons):
            response_buttons = None

        return response_buttons

    async def update(self, request_button: Optional[ButtonDB] = '',
                     new_button: Optional[ButtonDB] = '') -> None:
        query = fill_query(update(ButtonModel), request_button, new_button)
        if query is None:
            return None

        await self.session.execute(query)
        await self.session.commit()
