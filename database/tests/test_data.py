import json
from database.repositories.script import ScriptDB
from database.repositories.button import ButtonDB
from database.repositories.user_data import UserDataDB
from database.repositories.token import TokenDB

with open('tests/data/script.json') as f:
    scripts = [ScriptDB(**script) for script in json.load(f)]

with open('tests/data/button.json') as f:
    buttons = [ButtonDB(**button) for button in json.load(f)]

with open('tests/data/user_data.json') as f:
    users_data = [UserDataDB(**user_data) for user_data in json.load(f)]

with open('tests/data/token.json') as f:
    tokens = [TokenDB(**token) for token in json.load(f)]
