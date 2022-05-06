import asyncio

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.sql.sqltypes import String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import Column, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import text

from uuid import uuid4

# TODO idk how install own module by "pip install -Ue ." – it doesn't work
import sys
sys.path.append('..')

from database.config import settings


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

engine = create_async_engine(
    settings.DB_PATH
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

meta = MetaData(naming_convention=convention)
Base = declarative_base(metadata=meta)


class ScriptModel(Base):
    __tablename__ = 'script'

    uid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    text = Column(String, nullable=False)


class ButtonModel(Base):
    __tablename__ = 'button'

    uid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    title_from = Column(String)
    text = Column(String, nullable=False)
    title_to = Column(String)


class UserDataModel(Base):
    __tablename__ = 'user_data'

    uid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    tg_chat_id = Column(BigInteger, nullable=False, unique=True)
    is_admin = Column(Boolean, default=False)
    step = Column(String)
    quest_message_id = Column(BigInteger)
    is_in_quest = Column(Boolean, default=False)


class TokenModel(Base):
    __tablename__ = 'token'

    uid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    is_active = Column(Boolean, default=True)
    tg_chat_id = Column(
        BigInteger,
        ForeignKey(UserDataModel.tg_chat_id, onupdate='cascade', ondelete='cascade')
    )


# create tables
async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    return 0


if __name__ == "__main__":
    # uncomment to test all db functions
    asyncio.run(main())
