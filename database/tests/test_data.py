import json

with open('tests/data/script.json') as f:
    scripts = json.load(f)

with open('tests/data/button.json') as f:
    buttons = json.load(f)

with open('tests/data/user_data.json') as f:
    users_data = json.load(f)
