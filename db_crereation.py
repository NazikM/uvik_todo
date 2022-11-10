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

        with con as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS task(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, 
            description TEXT, 
            image BLOB, 
            completed INTEGER, 
            telegram_id INTEGER NOT NULL)''')
