from random import randint

from database.repositories.token import TokenRepository
from database.tests.test_data import tokens

from database.repositories.user_data import UserDataRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH TOKENS---------')

    async with SessionLocal() as session:
        repository_user_data = UserDataRepository(session)
        users_data = await repository_user_data.get_all()
        len_scripts = len(users_data) - 1
        for token in tokens:
            if 'is_active' not in token.keys():
                token['is_active'] = False
            elif not token['is_active']:
                token['tg_chat_id'] = users_data[randint(0, len_scripts)]['tg_chat_id']

        repository = TokenRepository(session)

        # adding items does not throw exceptions
        assert await repository.add(tokens) == tokens  # no exceptions

        # updating all data for all parameters does not throw exceptions
        for token in tokens:
            if not token['is_active']:
                token = token
                break
        old_uid = (await repository.get_one(tg_chat_id=token['tg_chat_id']))['uid']
        old_is_active = (await repository.get_one(tg_chat_id=token['tg_chat_id']))['is_active']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert (await repository.get_one(tg_chat_id=token['tg_chat_id']))['tg_chat_id'] == token['tg_chat_id']
        await repository.update(uid=old_uid)
        assert (await repository.get_one(tg_chat_id=token['tg_chat_id']))['tg_chat_id'] == token['tg_chat_id']
        await repository.update(new_tg_chat_id=123)
        assert await repository.get_one(tg_chat_id=123) is None  # no update is performed without input data

        await repository.update(uid=old_uid, new_is_active=not old_is_active)
        assert await repository.get_one(uid=old_uid, is_active=not old_is_active) is not None  # updating by uid

        await repository.update(uid=old_uid, is_active=not old_is_active, new_tg_chat_id=users_data[10]['tg_chat_id'])
        assert await repository.get_one(tg_chat_id=users_data[10]['tg_chat_id']) is not None  # updating by is_admin

        await repository.update(tg_chat_id=users_data[10]['tg_chat_id'], new_tg_chat_id=users_data[11]['tg_chat_id'])
        assert await repository.get_one(tg_chat_id=users_data[11]['tg_chat_id']) is not None  # updating by tg_chat_id

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(tg_chat_id=1)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        await repository.delete()
        assert await repository.add(tokens) == tokens
        old_uid = (await repository.get_one(tg_chat_id=token['tg_chat_id']))['uid']
        assert await repository.get_one(uid=old_uid) is not None  # element exists
        await repository.delete(uid=old_uid)  # no exceptions
        assert await repository.get_one(uid=old_uid) is None  # element deleted
        del old_uid

        assert await repository.add(token) == token
        assert await repository.get_one(is_active=token['is_active']) is not None  # element exists
        await repository.delete(is_active=token['is_active'])  # no exceptions
        assert await repository.get_one(is_active=token['is_active']) is None  # element deleted

        assert await repository.add(token) == token
        assert await repository.get_one(tg_chat_id=token['tg_chat_id']) is not None  # element exists
        await repository.delete(tg_chat_id=token['tg_chat_id'])  # no exceptions
        assert await repository.get_one(tg_chat_id=token['tg_chat_id']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(tokens)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH TOKENS--------\n')
