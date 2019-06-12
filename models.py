from collections import defaultdict

import peewee

from project.db import db


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = peewee.IntegerField(verbose_name='id в Telegram')


class Message(BaseModel):
    chat_id = peewee.IntegerField(verbose_name='id чата')
    message_id = peewee.IntegerField(verbose_name='id сообщения')
    user_id = peewee.IntegerField(verbose_name='id пользователя')
    # user = peewee.ForeignKeyField(User, backref='messages')

    def get_likes_by_type(self):
        query = self.likes.select(Like.type, peewee.fn.COUNT(Like.id).alias('like_count')).group_by(Like.type)
        data = defaultdict(int)
        for e in query:
            data[e.type] = e.like_count
        return data


class Like(BaseModel):
    message = peewee.ForeignKeyField(Message, backref='likes')
    user_id = peewee.IntegerField(verbose_name='id пользователя')
    # user = peewee.ForeignKeyField(User, backref='likes')

    LIKE = 1
    DISLIKE = 2
    OLD = 3
    CLASSIC = 4

    TYPE_CHOICES = (
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дислайк'),
        (OLD, 'Баян'),
        (CLASSIC, 'Классика'),
    )

    type = peewee.IntegerField(verbose_name='тип', choices=TYPE_CHOICES)

    BUTTON_LABELS = (
        (LIKE, '\U0001F44D'),
        (DISLIKE, '\U0001F44E'),
        (CLASSIC, '\U0001F44D [:||||:]'),
        (OLD, '\U0001F44E [:||||:]'),
    )
