import asyncio

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.sql.sqltypes import String, Boolean, BigInteger, DateTime
from sqlalchemy.sql.schema import Column, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from uuid import uuid4 as create_uuid

from config import settings


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


# create tables
async def update_tables(dev=False):
    from tests.test_all import TestBase

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if dev:
        testing = TestBase(Base)
        await testing.start()

    print('DB - OK')
    return 0


if __name__ == "__main__":
    # uncomment to test all db functions
    asyncio.run(update_tables(dev=True))
