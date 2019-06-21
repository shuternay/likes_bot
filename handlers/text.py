import logging

import telegram
from telegram.ext import MessageHandler

from filters import ExcludeSelfForwardFilter, IncludeTagFilter
from models import Message
from project import settings
from project.db import db
from utils import get_reply_markup, format_text

logger = logging.getLogger('request.{0}'.format(__file__))


def callback(bot: telegram.Bot, update: telegram.Update):
    if settings.DEBUG:
        logger.debug('update: %s', update)

    reply_markup = get_reply_markup()
    text = format_text(update.message.from_user, update.message.text)
    kwargs = dict(chat_id=update.message.chat_id, reply_markup=reply_markup, text=text)
    bot_msg = bot.send_message(**kwargs)

    try:
        with db:
            Message.create(
                message_tg_id=bot_msg.message_id,
                chat_tg_id=update.message.chat_id,
                user_tg_id=update.message.from_user.id
            )
        bot.delete_message(update.message.chat_id, update.message.message_id)
    except Exception:
        logger.exception('exception while adding text message %s', update)


filters = IncludeTagFilter() & ExcludeSelfForwardFilter()
handler = MessageHandler(filters, callback)
