#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import database

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, BaseFilter, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
import logging

import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


LIKE_TEXT = '👍'
DISLIKE_TEXT = '👎'
BAYAN_TEXT = '[:||||:]'


def echo(bot, update):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(LIKE_TEXT, callback_data='1'),
                                          InlineKeyboardButton(DISLIKE_TEXT, callback_data='2'),
                                          InlineKeyboardButton(BAYAN_TEXT, callback_data='3')]])

    if update.message.photo:
        text = '{1}\nSender: {0}'.format((update.message.from_user.first_name or '') + ' ' + (update.message.from_user.last_name or ''),
                                         update.message.caption or '')
        bot_msg = bot.send_photo(
            chat_id=update.message.chat_id, reply_markup=reply_markup,
            caption=text, photo=update.message.photo[-1].file_id)
    elif update.message.document:
        text = '{1}\nSender: {0}'.format((update.message.from_user.first_name or '') + ' ' + (update.message.from_user.last_name or ''),
                                         update.message.caption or '')
        bot_msg = bot.send_document(
            chat_id=update.message.chat_id, reply_markup=reply_markup,
            caption=text, document=update.message.document.file_id)
    else:
        text = '{1}\nSender: {0}'.format((update.message.from_user.first_name or '') + ' ' + (update.message.from_user.last_name or ''),
                                         update.message.text)
        bot_msg = bot.send_message(chat_id=update.message.chat_id, reply_markup=reply_markup, text=text)

    database.add_message(bot_msg.message_id, update.message.chat_id, update.message.from_user.id)

    bot.delete_message(update.message.chat_id, update.message.message_id)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def button(bot, update):
    query = update.callback_query

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = query.from_user.id

    like_type = int(query.data)
    likes = database.get_likes(chat_id, message_id)

    modified = False
    if user_id in likes[like_type]:
        for k, v in likes.items():
            if user_id in v:
                database.remove_like(chat_id, message_id, user_id, k)
                v.remove(user_id)
                modified = True
    else:
        for k, v in likes.items():
            if user_id in v:
                database.remove_like(chat_id, message_id, user_id, k)
                v.remove(user_id)
                modified = True
        if user_id != database.get_message_author(message_id, chat_id):
            database.add_like(chat_id, message_id, user_id, like_type)
            likes[like_type].append(user_id)
            modified = True

    if len(likes[1]) + 3 <= len(likes[2]) + len(likes[3]):
        bot.delete_message(chat_id, message_id)
        query.answer()
        return

    like_text = LIKE_TEXT if len(likes[1]) == 0 else '{0} {1}'.format(LIKE_TEXT, len(likes[1]))
    dislike_text = DISLIKE_TEXT if len(likes[2]) == 0 else '{0} {1}'.format(DISLIKE_TEXT, len(likes[2]))
    bayan_text = BAYAN_TEXT if len(likes[3]) == 0 else '{0} {1}'.format(BAYAN_TEXT, len(likes[3]))

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(like_text, callback_data='1'),
                                          InlineKeyboardButton(dislike_text, callback_data='2'),
                                          InlineKeyboardButton(bayan_text, callback_data='3')]])
    if modified:
        if query.message.text:
            bot.edit_message_text(
                text=query.message.text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup)
        else:
            bot.edit_message_caption(
                caption=query.message.caption,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup)

    query.answer()


class PastaFilter(BaseFilter):
    def filter(self, message):
        return '#паста' in (message.text or '') or '#мем' in (message.text or '')


def main():
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher

    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.photo | Filters.document, echo))
    # dp.add_handler(CommandHandler("likes", echo))
    dp.add_handler(MessageHandler(PastaFilter(), echo))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
