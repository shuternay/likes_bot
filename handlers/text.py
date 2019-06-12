import logging

import peewee
from telegram.ext import MessageHandler, Filters, BaseFilter

from models import Message
from project import settings
from project.db import db
from utils import get_reply_markup, format_text

logger = logging.getLogger('request.{0}'.format(__file__))


class IncludeTagFilter(BaseFilter):
    def filter(self, message):
        caption = message.text or ''
        return any(('#{0}'.format(tag) in caption for tag in settings.INCLUDE_TAGS))


def callback(bot, update):
    reply_markup = get_reply_markup()
    text = format_text(update.message.from_user, update.message.text)
    kwargs = dict(chat_id=update.message.chat_id, reply_markup=reply_markup, text=text)
    bot_msg = bot.send_message(**kwargs)

    db.connect()
    try:
        Message.create(message_id=bot_msg.message_id, chat_id=update.message.chat_id, user_id=update.message.from_user.id)
    except peewee.PeeweeException as e:
        logger.error(e, exc_info=True)
    finally:
        db.close()

    bot.delete_message(update.message.chat_id, update.message.message_id)


filters = IncludeTagFilter()
handler = MessageHandler(filters, callback)
