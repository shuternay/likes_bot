import logging

import peewee
from telegram.ext import CallbackQueryHandler

from models import Message, Like
from project import settings
from project.db import db
from utils import get_reply_markup

logger = logging.getLogger('request.{0}'.format(__file__))


def callback(bot, update):
    query = update.callback_query
    like_type = query.data

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = query.from_user.id

    db.connect()
    try:
        msg = Message.filter(Message.chat_id == chat_id, Message.message_id == message_id).get()
        like = msg.likes.filter(Like.user_id == user_id).first()
        if like:
            if like_type == str(like.type):
                like.delete_instance()
            else:
                like.type = like_type
                like.save()
        else:
            if user_id == msg.user_id:
                if like_type == str(Like.DISLIKE):
                    bot.delete_message(chat_id, message_id)
                query.answer()
                return
            else:
                Like.create(message_id=msg.id, user_id=user_id, type=like_type)
    except peewee.PeeweeException as e:
        logger.error(e, exc_info=True)
    else:
        like_dict = msg.get_likes_by_type()

        if like_dict[Like.LIKE] + settings.THRESHOLD <= like_dict[Like.DISLIKE] + like_dict[Like.OLD]:
            bot.delete_message(chat_id, message_id)
        else:
            reply_markup = get_reply_markup(like_dict)
            kwargs = dict(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
            if query.message.text:
                bot.edit_message_text(text=query.message.text, **kwargs)
            else:
                bot.edit_message_caption(caption=query.message.caption, **kwargs)
    finally:
        db.close()
    query.answer()


handler = CallbackQueryHandler(callback)
