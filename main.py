#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import database

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, BaseFilter, CallbackQueryHandler, MessageHandler, Filters
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


BUTTONS = [
    (u'\U0001F44D', '1'),
    (u'\U0001F44E', '2'),
    (u'\U0001F44D [:||||:]', '4'),
    (u'\U0001F44E [:||||:]', '3')
]


def format_message_text(user, caption):
    return '{0}\nSender: {1}'.format(
        caption or '',
        (user.first_name or '') + ' ' + (user.last_name or '')
    )


def echo(bot, update):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in BUTTONS[:2]],
        [InlineKeyboardButton(text, callback_data=data) for text, data in BUTTONS[2:]]])

    if update.message.photo:
        text = format_message_text(update.message.from_user, update.message.caption)
        bot_msg = bot.send_photo(
            chat_id=update.message.chat_id, reply_markup=reply_markup,
            caption=text, photo=update.message.photo[-1].file_id)
    elif update.message.video:
        text = format_message_text(update.message.from_user, update.message.caption)
        bot_msg = bot.send_video(
            chat_id=update.message.chat_id, reply_markup=reply_markup,
            caption=text, video=update.message.video.file_id)
    elif update.message.document:
        text = format_message_text(update.message.from_user, update.message.caption)
        bot_msg = bot.send_document(
            chat_id=update.message.chat_id, reply_markup=reply_markup,
            caption=text, document=update.message.document.file_id)
    else:
        text = format_message_text(update.message.from_user, update.message.text)
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

    button_text = [(text if len(likes[int(data)]) == 0 else '{0} {1}'.format(text, len(likes[int(data)])), data)
                   for text, data in BUTTONS]

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in button_text[:2]],
        [InlineKeyboardButton(text, callback_data=data) for text, data in button_text[2:]]])
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

    dp.add_handler(MessageHandler(Filters.photo | Filters.video | Filters.document, echo))
    # dp.add_handler(CommandHandler("likes", echo))
    dp.add_handler(MessageHandler(PastaFilter(), echo))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)

    updater.start_polling(poll_interval=1.0)

    updater.idle()


if __name__ == '__main__':
    main()
