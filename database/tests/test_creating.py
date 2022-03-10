from database.create_table import main


async def start(SessionLocal):
    print('----------------START DB CREATING----------------')

    # all tables with dependencies exist or are being created
    async with SessionLocal() as session:
        assert await main() == 0  # no exceptions

        # close session
        await session.close()

    print('---------------FINISH DB CREATING----------------\n')
