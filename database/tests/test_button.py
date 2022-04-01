from random import randint

from database.repositories.button import ButtonRepository, ButtonDB
from database.tests.test_data import buttons

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
            button.title_from = scripts[i_from].title
            button.title_to = scripts[i_to].title

        repository = ButtonRepository(session)

        # adding items does not throw exceptions
        load_buttons = await repository.add(buttons)
        assert all(buttons[i] <= load_buttons[i] for i in range(len(buttons)))  # no exceptions

        # updating all data for all parameters does not throw exceptions
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert (await repository.get_one(buttons[1])) >= buttons[1]
        await repository.update(buttons[1])
        assert await repository.get_one(buttons[1]) >= buttons[1]
        new_button = ButtonDB(text='new_text')
        await repository.update(new_button=new_button)
        assert await repository.get_one(new_button) is None  # no update is performed without input data

        new_button = ButtonDB(
            title_to=scripts[0].title,
            text='new_text',
            title_from=scripts[0].title
        )
        await repository.update(request_button=buttons[1], new_button=new_button)
        assert await repository.get_one(new_button) >= new_button  # updating by ButtonDB
        assert len(await repository.get_all(new_button)) == 1

        # return of modified data
        await repository.update(request_button=new_button, new_button=buttons[1])
        assert await repository.get_one(buttons[1]) >= buttons[1]
        assert len(await repository.get_all(buttons[1])) == 1
        assert await repository.get_one(new_button) is None
        assert len(await repository.get_all(new_button)) == 0

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(new_button)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed

        # deletes by parameter
        await repository.delete()
        load_buttons = await repository.add(buttons)
        assert all(buttons[i] <= load_buttons[i] for i in range(len(buttons)))
        assert await repository.get_one(buttons[1]) >= buttons[1]  # element exists
        await repository.delete(buttons[1])  # no exceptions
        assert await repository.get_one(buttons[1]) is None  # element deleted
        assert old_number - 1 == len(await repository.get_all())
        del new_button, old_number

        # return of modified data
        await repository.delete()
        await repository.add(buttons)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH BUTTONS--------\n')
