import pytest
from database.create_table import Base, engine

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from database.tests import (
    test_creating,
    test_dropping,
    test_script,
    test_button,
    test_user_data,
    test_token
)

session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


@pytest.mark.asyncio
class TestBase:
    async def test_db(self):
        print('\n------------------START TESTING------------------\n')
        await test_creating.start(session_local)
        await test_dropping.start(engine, Base)
        await test_creating.start(session_local)

        await test_script.start(session_local)
        await test_button.start(session_local)
        await test_user_data.start(session_local)
        await test_token.start(session_local)
        # await test_dropping.start(self.engine, Base)

        print('------------------FINISH TESTING-----------------')
