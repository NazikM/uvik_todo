import contextlib
import sqlite3


def create_tables():
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS user(
            telegram_id INTEGER NOT NULL, 
            state text NOT NULL,
            draft_task_id INTEGER
            );''')
            # data = cur.fetchone()

        with con as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS task(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, 
            description TEXT, 
            image BLOB, 
            completed INTEGER, 
            telegram_id INTEGER NOT NULL)''')


def add_user(telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('INSERT INTO user(telegram_id, state, draft_task_id) VALUES(?, ?, Null);', (telegram_id, 'main'))


def add_task(title, telegram_id, description=None, image_blob=None):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with contextlib.closing(con.cursor()) as cur:
            cur.execute('INSERT INTO task(title, description, image, completed, telegram_id) VALUES(?, ?, ?, false, ?);', (title, description, image_blob, telegram_id))
            con.commit()
            return cur.lastrowid


def get_draft_task_id(telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with contextlib.closing(con.cursor()) as cur:
            cur.execute('select draft_task_id FROM user where telegram_id=?', (telegram_id,))
            return cur.fetchone()[0]


def set_draft_task_id(telegram_id, task_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('UPDATE user SET draft_task_id=? WHERE telegram_id=?;', (task_id, telegram_id))


def mark_as_completed(task_id, telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('UPDATE task SET completed=true WHERE id=(?) and telegram_id=?;', (task_id, telegram_id))


def update_task(task_id, telegram_id, title=None, description=None, image_blob=None):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            if title:
                cur.execute('UPDATE task SET title=(?) WHERE id=(?) and telegram_id=(?);', (title, task_id, telegram_id))
            if description:
                cur.execute('UPDATE task SET description=(?) WHERE id=(?) and telegram_id=(?);', (description, task_id, telegram_id))
            if image_blob:
                cur.execute('UPDATE task SET image=(?) WHERE id=(?) and telegram_id=(?);', (image_blob, task_id, telegram_id))


def list_user_tasks(telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with contextlib.closing(con.cursor()) as cur:
            cur.execute('select * FROM task where telegram_id=?', (telegram_id,))
            data = cur.fetchall()
            return data


def get_task(task_id, telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with contextlib.closing(con.cursor()) as cur:
            cur.execute('select * FROM task where telegram_id=? and id=?', (telegram_id, task_id))
            data = cur.fetchall()
            return data[0]


def delete_user_task(task_id, telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('DELETE FROM task WHERE id=? and telegram_id=?', (task_id, telegram_id))


def get_user_state(telegram_id):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with contextlib.closing(con.cursor()) as cur:
            cur.execute('select state FROM user where telegram_id=?', (telegram_id,))
            state = cur.fetchone()[0]
    return state


def set_user_state(telegram_id, state):
    with contextlib.closing(sqlite3.connect('todo.db')) as con:
        with con as cur:
            cur.execute('UPDATE user SET state=(?) WHERE telegram_id=(?);', (state, telegram_id))
