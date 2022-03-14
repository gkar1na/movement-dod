import json

with open('database/tests/data/script.json') as f:
    scripts = json.load(f)

with open('database/tests/data/button.json') as f:
    buttons = json.load(f)

with open('database/tests/data/user_data.json') as f:
    users_data = json.load(f)

with open('database/tests/data/token.json') as f:
    tokens = json.load(f)
