from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import sessionmaker

from config import settings


class TestBase:
    def __init__(self, base: DeclarativeMeta):
        self.base = base
        self.engine = create_async_engine(settings.DB_PATH)

        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
