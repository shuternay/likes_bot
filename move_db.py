import initdb
import logging.config
import os
import sqlite3

from models import Message, Like
from project import settings
from project.db import db as peewee_db

logger = logging.getLogger('main')

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


def move_db() -> None:
    logging_settings = settings.LOGGING
    logging_settings['loggers']['peewee']['level'] = 'INFO'
    logging.config.dictConfig(settings.LOGGING)

    sqlite_db = get_db()

    initdb.create_tables()
    with peewee_db:
        cur = sqlite_db.execute('select count(*) AS cnt from messages')
        messages_count = cur.fetchone()['cnt']
        cur = sqlite_db.execute('select chat_id, message_id, user_id from messages')

        logger.info('moving %s messages', messages_count)
        for index, row in enumerate(cur):
            if index % 100 == 0:
                logger.info('%s messages...', index)
            Message.get_or_create(
                chat_tg_id=row['chat_id'],
                message_tg_id=row['message_id'],
                user_tg_id=row['user_id'],
            )

        cur = sqlite_db.execute('select count(*) AS cnt from likes')
        likes_count = cur.fetchone()['cnt']
        cur = sqlite_db.execute('select chat_id, message_id, user_id, like_type from likes')

        logger.info('moving %s likes', likes_count)
        for index, row in enumerate(cur):
            if index % 100 == 0:
                logger.info('%s likes...', index)
            msg, _ = Message.get_or_create(
                chat_tg_id=row['chat_id'],
                message_tg_id=row['message_id'],
                defaults={'user_tg_id': -1},
            )

            like = Like.filter(
                Like.message_id == msg.id,
                Like.user_tg_id == row['user_id'],
            ).first()

            if like:
                like.type = row['like_type']
                like.save()
            else:
                Like.create(
                    message_id=msg.id,
                    user_tg_id=row['user_id'],
                    type=row['like_type'],
                )


if __name__ == '__main__':
    move_db()
