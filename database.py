import os
import sqlite3

DATABASE = os.environ.get('DATABASE')


def connect_db():
    print(DATABASE)
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


sqlite_db = None


def get_db():
    global sqlite_db
    if sqlite_db is None:
        sqlite_db = connect_db()
    return sqlite_db


def init_db():
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def close_db(error):
    global sqlite_db
    if sqlite_db is not None:
        sqlite_db.close()
        sqlite_db = None


def add_like(chat_id, message_id, user_id, like_type):
    # TODO: check if like exists
    db = get_db()
    db.execute('insert into likes (chat_id, message_id, user_id, like_type) values (?, ?, ?, ?)',
               (chat_id, message_id, user_id, int(like_type)))
    db.commit()


def remove_like(chat_id, message_id, user_id, like_type):
    db = get_db()
    db.execute('delete from likes where chat_id = ? and message_id = ? and user_id = ? and like_type = ?',
               (chat_id, message_id, user_id, int(like_type)))
    db.commit()


def get_likes(chat_id, message_id):
    db = get_db()
    likes = {}
    for like_type in [1, 2, 3, 4]:
        cur = db.execute('select user_id from likes where chat_id = ? and message_id = ? and like_type = ?',
                         (chat_id, message_id, like_type))
        entries = cur.fetchall()
        likes[like_type] = [x['user_id'] for x in entries]

    return likes


def get_all_likes(chat_id):
    db = get_db()
    cur = db.execute('select user_id, message_id, like_type from likes where chat_id = ?',
                     (chat_id, ))
    entries = cur.fetchall()
    likes = [(x['message_id'], x['user_id'], x['like_type']) for x in entries]
    return likes


def add_message(message_id, chat_id, user_id):
    db = get_db()
    db.execute('insert into messages (message_id, chat_id, user_id) values (?, ?, ?)',
               (message_id, chat_id, user_id))
    db.commit()


def get_message_author(message_id, chat_id):
    db = get_db()
    cur = db.execute('select user_id from messages where chat_id = ? and message_id = ?',
                     (chat_id, message_id))
    entries = cur.fetchall()

    if len(entries) > 0:
        return entries[0]['user_id']
    else:
        return None


if __name__ == '__main__':
    init_db()
    print('Initialized the database.')
