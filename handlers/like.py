import logging

import telegram
from telegram.ext import CallbackQueryHandler

from models import Message, Like
from project import settings
from project.db import db
from utils import get_reply_markup

logger = logging.getLogger('request.{0}'.format(__file__))


def callback(bot: telegram.Bot, update: telegram.Update):
    query = update.callback_query
    like_type = query.data

    if settings.DEBUG:
        logger.debug('update: %s', update)

    chat_tg_id = query.message.chat_id
    message_tg_id = query.message.message_id
    user_tg_id = query.from_user.id

    try:
        with db:
            msg, created = Message.get_or_create(
                chat_tg_id=chat_tg_id,
                message_tg_id=message_tg_id,
                defaults={'user_tg_id': -1},
            )
            if created:
                logger.warning('missing message: chat_id = %s, msg_id = %s', chat_tg_id, message_tg_id)

            like = msg.likes.filter(Like.user_tg_id == user_tg_id).first()
            if like:
                if like_type == str(like.type):
                    like.delete_instance()
                else:
                    like.type = like_type
                    like.save()
            else:
                if user_tg_id == msg.user_tg_id:
                    like_dict = msg.get_likes_by_type()
                    if like_type == str(Like.DISLIKE) and like_dict[Like.LIKE] < settings.DELETE_THRESHOLD:
                        bot.delete_message(chat_tg_id, message_tg_id)
                    query.answer()
                    return
                else:
                    Like.create(message_id=msg.id, user_tg_id=user_tg_id, type=like_type)

            like_dict = msg.get_likes_by_type()

            if like_dict[Like.LIKE] + settings.DELETE_THRESHOLD <= like_dict[Like.DISLIKE] + like_dict[Like.OLD]:
                bot.delete_message(chat_tg_id, message_tg_id)
            else:
                reply_markup = get_reply_markup(like_dict)
                kwargs = dict(chat_id=chat_tg_id, message_id=message_tg_id, reply_markup=reply_markup)
                if query.message.text:
                    bot.edit_message_text(text=query.message.text, **kwargs)
                else:
                    bot.edit_message_caption(caption=query.message.caption, **kwargs)
    except Exception:
        logger.exception('exception while adding like %s', update)
    query.answer()


handler = CallbackQueryHandler(callback)
