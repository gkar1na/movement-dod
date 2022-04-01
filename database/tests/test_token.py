from random import randint

from database.repositories.token import TokenRepository, TokenDB
from database.tests.test_data import tokens

from database.repositories.user_data import UserDataRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH TOKENS---------')

    async with SessionLocal() as session:
        repository_user_data = UserDataRepository(session)
        users_data = await repository_user_data.get_all()
        len_tokens = len(users_data) - 1
        for token in tokens:
            if token.is_active == '':
                token.is_active = False
            elif not token.is_active:
                token.tg_chat_id = users_data[randint(2, len_tokens)].tg_chat_id

        repository = TokenRepository(session)

        # adding items does not throw exceptions
        load_tokens = await repository.add(tokens)
        assert all(tokens[i] <= load_tokens[i] for i in range(len(tokens)))  # no exceptions

        # updating all data for all parameters does not throw exceptions
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(tokens[1]) >= tokens[1]
        await repository.update(tokens[1])
        assert await repository.get_one(tokens[1]) >= tokens[1]
        new_token = TokenDB(tg_chat_id=users_data[0].tg_chat_id)
        await repository.update(new_token=new_token)
        assert await repository.get_one(new_token) is None  # no update is performed without input data

        new_token = TokenDB(
            is_active=False,
            tg_chat_id=users_data[0].tg_chat_id
        )
        await repository.update(request_token=tokens[1], new_token=new_token)
        assert await repository.get_one(new_token) >= new_token  # updating by TokenDB
        assert len(await repository.get_all(new_token)) == 1

        # return of modified data
        await repository.update(request_token=new_token, new_token=tokens[1])
        assert await repository.get_one(tokens[1]) >= tokens[1]
        assert len(await repository.get_all(tokens[1])) == 1
        assert await repository.get_one(new_token) is None
        assert len(await repository.get_all(new_token)) == 0

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(new_token)  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed

        # deletes by parameter
        await repository.delete()
        load_tokens = await repository.add(tokens)
        assert all(tokens[i] <= load_tokens[i] for i in range(len(tokens)))
        assert await repository.get_one(tokens[1]) >= tokens[1]  # element exists
        await repository.delete(tokens[1])  # no exceptions
        assert await repository.get_one(tokens[1]) is None  # element deleted
        assert old_number - 1 == len(await repository.get_all())
        del new_token, old_number

        # return of modified data
        await repository.delete()
        await repository.add(tokens)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH TOKENS--------\n')
