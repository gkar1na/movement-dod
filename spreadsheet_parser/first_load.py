import os

from database.repositories.script import ScriptRepository
from spreadsheet_parser.sheet2db import convert
from spreadsheet_parser.config import settings


async def update_db(session, force: bool = False):

    # user_password = settings.DB_PATH[settings.DB_PATH.rfind('//') + 1:settings.DB_PATH.rfind('@')]
    #
    # username, password = user_password.split(':')
    # db_name = settings.DB_PATH[settings.DB_PATH.rfind('/') + 1:]
    # os.system(f'sudo -u {username} {password} {db_name}')

    script_repository = ScriptRepository(session)

    scripts = await script_repository.get_one()

    if not scripts or force:
        await convert(
            settings.SPREADSHEET_ID,
            settings.DB_PATH
        )


# asyncio.run(update_db())
