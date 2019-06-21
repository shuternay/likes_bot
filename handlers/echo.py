import logging

from telegram.ext import MessageHandler, Filters, BaseFilter

from models import Message
from project import settings
from project.db import db
from utils import get_reply_markup, format_text

logger = logging.getLogger('request.{0}'.format(__file__))


class ExcludeTagFilter(BaseFilter):
    def filter(self, message):
        caption = message.caption or ''
        return all(('#{0}'.format(tag) not in caption for tag in settings.EXCLUDE_TAGS))


def callback(bot, update):
    if settings.DEBUG:
        logger.debug('update: %s', update)

    reply_markup = get_reply_markup()
    text = format_text(update.message.from_user, update.message.caption)
    kwargs = dict(chat_id=update.message.chat_id, reply_markup=reply_markup, caption=text)

    if update.message.photo:
        bot_msg = bot.send_photo(**kwargs, photo=update.message.photo[-1].file_id)
    elif update.message.video:
        bot_msg = bot.send_video(**kwargs, video=update.message.video.file_id)
    elif update.message.document:
        bot_msg = bot.send_document(**kwargs, document=update.message.document.file_id)
    else:
        return

    try:
        with db:
            Message.create(
                message_tg_id=bot_msg.message_id,
                chat_tg_id=update.message.chat_id,
                user_tg_id=update.message.from_user.id
            )
        bot.delete_message(update.message.chat_id, update.message.message_id)
    except Exception:
        logger.exception('exception while adding message %s', update)


filters = (Filters.photo | Filters.video | Filters.document) & ExcludeTagFilter()
handler = MessageHandler(filters, callback)
