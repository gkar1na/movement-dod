import uuid

from database.repositories.script import ScriptRepository, ScriptDB
from database.tests.test_data import scripts


async def start(SessionLocal):
    print('----------START INTERACTION WITH SCRIPTS---------')

    async with SessionLocal() as session:
        repository = ScriptRepository(session)

        # adding items does not throw exceptions
        # print(scripts[0])
        load_scripts = await repository.add(scripts)
        assert all(scripts[i] <= load_scripts[i] for i in range(len(scripts)))  # no exceptions

        # updating all data for all parameters does not throw exceptions
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(scripts[1]) <= scripts[1]
        await repository.update(scripts[1])
        assert await repository.get_one(scripts[1]) <= scripts[1]
        new_script = ScriptDB(title='new_title')
        await repository.update(new_script=new_script)
        assert await repository.get_one(new_script) is None  # no update is performed without input data

        new_script = ScriptDB(
            title='new_title',
            text='new_text'
        )
        await repository.update(request_script=scripts[1], new_script=new_script)
        assert await repository.get_one(new_script) <= new_script  # updating by ScriptDB
        assert len(await repository.get_all(new_script)) == 1

        # return of modified data
        await repository.update(request_script=new_script, new_script=scripts[1])
        assert await repository.get_one(scripts[1]) <= scripts[1]
        assert len(await repository.get_all(scripts[1])) == 1
        assert await repository.get_one(new_script) is None
        assert len(await repository.get_all(new_script)) == 0

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(new_script)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed

        # deletes by parameter
        await repository.delete()
        load_scripts = await repository.add(scripts)
        assert all(scripts[i] <= load_scripts[i] for i in range(len(scripts)))
        assert await repository.get_one(scripts[1]) <= scripts[1]  # element exists
        await repository.delete(scripts[1])  # no exceptions
        assert await repository.get_one(scripts[1]) is None  # element deleted
        assert old_number - 1 == len(await repository.get_all())
        del new_script, old_number

        # return of modified data
        await repository.delete()
        await repository.add(scripts)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH SCRIPTS--------\n')
