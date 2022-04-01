import json
from database.repositories.script import ScriptDB

with open('tests/data/script.json') as f:
    scripts = [ScriptDB(**script) for script in json.load(f)]

with open('tests/data/button.json') as f:
    buttons = json.load(f)

with open('tests/data/user_data.json') as f:
    users_data = json.load(f)

with open('tests/data/token.json') as f:
    tokens = json.load(f)
