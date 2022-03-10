from database.create_table import update_tables


async def start(SessionLocal):
    print('----------------START DB CREATING----------------')

    # all tables with dependencies exist or are being created
    async with SessionLocal() as session:
        assert await update_tables() == 0  # no exceptions

        # close session
        await session.close()

    print('---------------FINISH DB CREATING----------------\n')
