from random import randint

from database.repositories.user_data import UserDataRepository, UserDataDB
from database.tests.test_data import users_data

from database.repositories.script import ScriptRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH USERS_DATA---------')

    async with SessionLocal() as session:
        repository_script = ScriptRepository(session)
        scripts = await repository_script.get_all()
        len_scripts = len(scripts) - 1
        for user_data in users_data:
            if randint(0, 2):
                user_data.step = scripts[randint(0, len_scripts)].title

        repository = UserDataRepository(session)

        # adding items does not throw exceptions
        load_users_data = await repository.add(users_data)
        assert all(users_data[i] <= load_users_data[i] for i in range(len(users_data)))

        # updating all data for all parameters does not throw exceptions
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(users_data[1]) >= users_data[1]
        await repository.update(users_data[1])
        assert await repository.get_one(users_data[1]) >= users_data[1]
        new_user_data = UserDataDB(tg_chat_id=0)
        await repository.update(new_user_data=new_user_data)
        assert await repository.get_one(new_user_data) is None # no update is performed without input data

        new_user_data = UserDataDB(
            tg_chat_id=0,
            is_admin=True,
            step=scripts[0].title,
            quest_message_id=0,
            is_in_quest=True
        )
        await repository.update(request_user_data=users_data[1], new_user_data=new_user_data)
        assert await repository.get_one(new_user_data) >= new_user_data  # updating by UserDataDB
        assert len(await repository.get_all(new_user_data)) == 1

        # return of modified data
        await repository.update(request_user_data=new_user_data, new_user_data=users_data[1])
        assert await repository.get_one(users_data[1]) >= users_data[1]
        assert len(await repository.get_all(users_data[1])) == 1
        assert await repository.get_one(new_user_data) is None
        assert len(await repository.get_all(new_user_data)) == 0

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(new_user_data)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed

        # deletes by parameter
        await repository.delete()
        load_users_data = await repository.add(users_data)
        assert all(users_data[i] <= load_users_data[i] for i in range(len(users_data)))
        assert await repository.get_one(users_data[1]) >= users_data[1]  # element exists
        await repository.delete(users_data[1])  # no exceptions
        assert await repository.get_one(users_data[1]) is None  # element deleted
        assert old_number - 1 == len(await repository.get_all())
        del new_user_data, old_number

        # return of modified data
        await repository.delete()
        await repository.add(users_data)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH USERS_DATA--------\n')
