import json
from random import randint
from database.repositories.script import ScriptRepository

with open('tests/data/script.json') as f:
    scripts = json.load(f)

with open('tests/data/button.json') as f:
    buttons = json.load(f)

