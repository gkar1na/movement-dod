from random import randint

from database.repositories.user_data import UserDataRepository
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
                user_data['step'] = scripts[randint(0, len_scripts)]['title']

        repository = UserDataRepository(session)

        # adding items does not throw exceptions
        assert await repository.add(users_data) == users_data  # no exceptions

        # updating all data for all parameters does not throw exceptions
        old_uid = (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['uid']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['tg_chat_id'] == users_data[1]['tg_chat_id']
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['is_admin'] == users_data[1]['is_admin']
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['quest_message_id'] == users_data[1]['quest_message_id']
        await repository.update(uid=old_uid)
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['tg_chat_id'] == users_data[1]['tg_chat_id']
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['is_admin'] == users_data[1]['is_admin']
        assert (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['quest_message_id'] == users_data[1]['quest_message_id']
        await repository.update(new_tg_chat_id=123)
        assert await repository.get_one(tg_chat_id=123) is None  # no update is performed without input data

        await repository.update(uid=old_uid, new_tg_chat_id=1)
        assert await repository.get_one(tg_chat_id=1) is not None  # updating by uid

        await repository.update(tg_chat_id=1, new_is_admin=not users_data[1]['is_admin'])
        assert await repository.get_one(tg_chat_id=1, is_admin=not users_data[1]['is_admin']) is not None  # updating by tg_chat_id

        await repository.update(tg_chat_id=1, is_admin=not users_data[1]['is_admin'], new_step=scripts[1]['title'])
        assert await repository.get_one(step=scripts[1]['title']) is not None  # updating by tg_chat_id

        await repository.update(step=scripts[1]['title'], new_quest_message_id=0)
        assert await repository.get_one(quest_message_id=0) is not None  # updating by step

        await repository.update(quest_message_id=0, new_is_admin=not users_data[1]['is_in_quest'])
        assert await repository.get_one(quest_message_id=0, is_admin=not users_data[1]['is_in_quest']) is not None  # updating by quest_message_id

        await repository.update(quest_message_id=0, is_admin=not users_data[1]['is_in_quest'], new_is_in_quest=users_data[1]['is_in_quest'])
        assert await repository.get_one(quest_message_id=0, is_in_quest=users_data[1]['is_in_quest'])  # updating by is_in_quest

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(tg_chat_id=12345)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(users_data[1]) == users_data[1]
        old_uid = (await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']))['uid']
        assert await repository.get_one(uid=old_uid) is not None  # element exists
        await repository.delete(uid=old_uid)  # no exceptions
        assert await repository.get_one(uid=old_uid) is None  # element deleted
        del old_uid

        assert await repository.add(users_data[1]) == users_data[1]
        assert await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']) is not None  # element exists
        await repository.delete(tg_chat_id=users_data[1]['tg_chat_id'])  # no exceptions
        assert await repository.get_one(tg_chat_id=users_data[1]['tg_chat_id']) is None  # element deleted

        assert await repository.add(users_data[1]) == users_data[1]
        assert await repository.get_one(is_admin=users_data[1]['is_admin']) is not None  # element exists
        await repository.delete(is_admin=users_data[1]['is_admin'])  # no exceptions
        assert await repository.get_one(is_admin=users_data[1]['is_admin']) is None  # element deleted

        await repository.delete()
        assert await repository.add(users_data) == users_data
        for user_data in users_data:
            if 'step' in user_data.keys():
                user_data = user_data
                break
        assert await repository.get_one(step=user_data['step']) is not None  # element exists
        await repository.delete(step=user_data['step'])  # no exceptions
        assert await repository.get_one(step=user_data['step']) is None  # element deleted

        await repository.delete()
        assert await repository.add(users_data) == users_data
        assert await repository.get_one(quest_message_id=users_data[1]['quest_message_id']) is not None  # element exists
        await repository.delete(quest_message_id=users_data[1]['quest_message_id'])  # no exceptions
        assert await repository.get_one(quest_message_id=users_data[1]['quest_message_id']) is None  # element deleted

        await repository.delete()
        assert await repository.add(users_data) == users_data
        assert await repository.get_one(is_in_quest=users_data[1]['is_in_quest']) is not None  # element exists
        await repository.delete(is_in_quest=users_data[1]['is_in_quest'])  # no exceptions
        assert await repository.get_one(is_in_quest=users_data[1]['is_in_quest']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(users_data)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH USERS_DATA--------\n')
