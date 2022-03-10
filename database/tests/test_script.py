from tests.test_data import scripts

from repositories.script import ScriptRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH SCRIPTS---------')

    async with SessionLocal() as session:
        repository = ScriptRepository(session)

        # adding items does not throw exceptions
        assert await repository.add(scripts) == scripts  # no exceptions

        # updating all data for all parameters does not throw exceptions
        old_uid = (await repository.get_one(title=scripts[1]['title']))['uid']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert (await repository.get_one(title=scripts[1]['title']))['title'] == scripts[1]['title']
        assert (await repository.get_one(title=scripts[1]['title']))['text'] == scripts[1]['text']
        await repository.update(uid=old_uid)
        assert (await repository.get_one(title=scripts[1]['title']))['title'] == scripts[1]['title']
        assert (await repository.get_one(title=scripts[1]['title']))['text'] == scripts[1]['text']
        await repository.update(new_title='100000000')
        assert await repository.get_one(title='100000000') is None  # no update is performed without input data

        await repository.update(uid=old_uid, new_title='new title')
        assert await repository.get_one(title='new title') is not None  # updating by uid

        await repository.update(title='new title', new_text='new text')
        assert await repository.get_one(text='new text') is not None  # updating by title

        await repository.update(text='new text', new_text='the newest text')
        assert await repository.get_one(text='the newest text') is not None  # updating by text

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(title='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(scripts[1]) == scripts[1]
        assert await repository.get_one(uid=old_uid) is not None  # element exists
        await repository.delete(uid=old_uid)  # no exceptions
        assert await repository.get_one(uid=old_uid) is None  # element deleted
        del old_uid

        assert await repository.add(scripts[1]) == scripts[1]
        assert await repository.get_one(title=scripts[1]['title']) is not None  # element exists
        await repository.delete(title=scripts[1]['title'])  # no exceptions
        assert await repository.get_one(title=scripts[1]['title']) is None  # element deleted

        assert await repository.add(scripts[1]) == scripts[1]
        assert await repository.get_one(text=scripts[1]['text']) is not None  # element exists
        await repository.delete(text=scripts[1]['text'])  # no exceptions
        assert await repository.get_one(text=scripts[1]['text']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(scripts)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH SCRIPTS--------\n')
