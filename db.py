from databases import Database


async def add_user(telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        await database.execute(
            "INSERT INTO user(telegram_id, state, draft_task_id) VALUES(:telegram_id, 'main', Null);",
            {'telegram_id': telegram_id})


async def add_task(title, telegram_id, description=None, image_blob=None):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        async with database.connection() as connection:
            async with connection.transaction():
                await connection.execute(
                    'INSERT INTO task(title, description, image, completed, telegram_id) VALUES(:title, :desc, :img, false, :teleg_id);',
                    {'title': title,
                     'desc': description,
                     'img': image_blob,
                     'teleg_id': telegram_id})
                return await connection.fetch_one(query="SELECT last_insert_rowid()")


async def get_draft_task_id(telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        query = 'select draft_task_id FROM user where telegram_id=:teleg_id'
        params = {
            'teleg_id': telegram_id
        }
        return await database.fetch_one(query=query, values=params)


async def set_draft_task_id(telegram_id, task_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        await database.execute('UPDATE user SET draft_task_id=:task_id WHERE telegram_id=:teleg_id;',
                               {'task_id': task_id, 'teleg_id': telegram_id})


async def mark_as_completed(task_id, telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        await database.execute('UPDATE task SET completed=true WHERE id=:task_id and telegram_id=:teleg_id;',
                               {'task_id': task_id, 'teleg_id': telegram_id})


async def update_task(task_id, telegram_id, title=None, description=None, image_blob=None):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        if title:
            await database.execute('UPDATE task SET title=:title WHERE id=:task_id and telegram_id=:teleg_id;',
                                   {'title': title,
                                    'task_id': task_id,
                                    'teleg_id': telegram_id})
        if description:
            await database.execute('UPDATE task SET description=:desc WHERE id=:task_id and telegram_id=:teleg_id;',
                                   {'desc': description,
                                    'task_id': task_id,
                                    'teleg_id': telegram_id})
        if image_blob:
            await database.execute('UPDATE task SET image=:img WHERE id=:task_id and telegram_id=:teleg_id;',
                                   {'img': image_blob,
                                    'task_id': task_id,
                                    'teleg_id': telegram_id})


async def list_user_tasks(telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        query = 'select * FROM task where telegram_id=:teleg_id'
        params = {
            'teleg_id': telegram_id
        }
        return await database.fetch_all(query=query, values=params)


async def get_task(task_id, telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        query = 'select * FROM task where telegram_id=:teleg_id and id=:task_id'
        params = {
            'teleg_id': telegram_id,
            'task_id': task_id
        }
        return await database.fetch_one(query=query, values=params)


async def delete_user_task(task_id, telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        await database.execute('DELETE FROM task WHERE id=:task_id and telegram_id=:teleg_id',
                               {'task_id': task_id, 'teleg_id': telegram_id})


async def get_user_state(telegram_id):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        query = 'select state FROM user where telegram_id=:teleg_id'
        params = {
            'teleg_id': telegram_id
        }
        return await database.fetch_one(query=query, values=params)


async def set_user_state(telegram_id, state):
    async with Database('sqlite+aiosqlite:///todo.db') as database:
        await database.execute('UPDATE user SET state=:state WHERE telegram_id=:teleg_id;',
                               {'state': state, 'teleg_id': telegram_id})
