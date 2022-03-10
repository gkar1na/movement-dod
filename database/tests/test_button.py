from random import randint
from database.repositories.button import ButtonRepository

from tests.test_data import buttons
from database.repositories.script import ScriptRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH BUTTONS---------')

    async with SessionLocal() as session:
        repository_script = ScriptRepository(session)
        scripts = await repository_script.get_all()
        len_scripts = len(scripts) - 1
        for button in buttons:
            i_from = randint(0, len_scripts)
            i_to = randint(0, len_scripts)
            while i_to == i_from:
                i_to = randint(0, len_scripts)
            button['title_from'] = scripts[i_from]['uid']
            button['title_to'] = scripts[i_to]['uid']

        repository = ButtonRepository(session)

        # adding items does not throw exceptions
        assert await repository.add(buttons) == buttons  # no exceptions

        # updating all data for all parameters does not throw exceptions
        old_uid = (await repository.get_one(title_from=buttons[1]['title_from']))['uid']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['title_from'] == buttons[1]['title_from']
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['text'] == buttons[1]['text']
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['title_to'] == buttons[1]['title_to']
        await repository.update(uid=old_uid)
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['title_from'] == buttons[1]['title_from']
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['text'] == buttons[1]['text']
        assert (await repository.get_one(title_from=buttons[1]['title_from']))['title_to'] == buttons[1]['title_to']
        await repository.update(new_text='100000000')
        assert await repository.get_one(text='100000000') is None  # no update is performed without input data

        await repository.update(uid=old_uid, new_title_from=scripts[0]['uid'])
        assert await repository.get_one(title_from=scripts[0]['uid']) is not None  # updating by uid

        await repository.update(title_from=scripts[0]['uid'], new_text='new text')
        assert await repository.get_one(text='new text') is not None  # updating by title_from

        await repository.update(text='new text', new_title_to=scripts[1]['uid'])
        assert await repository.get_one(title_to=scripts[1]['uid']) is not None  # updating by text

        await repository.update(title_to=scripts[1]['uid'], new_title_to=scripts[2]['uid'])
        assert await repository.get_one(title_to=scripts[2]['uid']) is not None  # updating by text

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(text='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(buttons[1]) == buttons[1]
        assert await repository.get_one(uid=old_uid) is not None  # element exists
        await repository.delete(uid=old_uid)  # no exceptions
        assert await repository.get_one(uid=old_uid) is None  # element deleted
        del old_uid

        assert await repository.add(buttons[1]) == buttons[1]
        assert await repository.get_one(title_from=buttons[1]['title_from']) is not None  # element exists
        await repository.delete(title_from=buttons[1]['title_from'])  # no exceptions
        assert await repository.get_one(title_from=buttons[1]['title_from']) is None  # element deleted

        assert await repository.add(buttons[1]) == buttons[1]
        assert await repository.get_one(text=buttons[1]['text']) is not None  # element exists
        await repository.delete(text=buttons[1]['text'])  # no exceptions
        assert await repository.get_one(text=buttons[1]['text']) is None  # element deleted

        assert await repository.add(buttons[1]) == buttons[1]
        assert await repository.get_one(title_to=buttons[1]['title_to']) is not None  # element exists
        await repository.delete(title_to=buttons[1]['title_to'])  # no exceptions
        assert await repository.get_one(title_to=buttons[1]['title_to']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(buttons)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH BUTTONS--------\n')
