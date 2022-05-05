from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Instance stores all app settings, mainly environment variables """
    PROJECT_NAME: str = 'Movement Quest'
    DB_PATH: Optional[str]
    SPREADSHEET_ID: Optional[str]

    class Config:
        env_prefix = 'MOVEMENT_QUEST_'
        # uncomment when testing locally
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
