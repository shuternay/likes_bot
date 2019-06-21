import logging

from telegram.ext import MessageHandler, BaseFilter

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


filters = IncludeTagFilter()
handler = MessageHandler(filters, callback)
