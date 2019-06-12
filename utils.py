from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from models import Like, Message


def format_text(user, text):
    return '{0}\nSender: {1} {2}'.format(text or '', user.first_name or '', user.last_name or '')


def get_button(data, text, like_count):
    if like_count:
        button_text = '{0} {1}'.format(text, like_count)
    else:
        button_text = text
    return InlineKeyboardButton(button_text, callback_data=data)


def get_reply_markup(like_dict=None):
    if like_dict and isinstance(like_dict, dict):
        return InlineKeyboardMarkup([
            [get_button(data, text, like_dict.get(data)) for data, text in Like.BUTTON_LABELS[:2]],
            [get_button(data, text, like_dict.get(data)) for data, text in Like.BUTTON_LABELS[2:]]
        ])
    else:
        return InlineKeyboardMarkup([
            [get_button(data, text, None) for data, text in Like.BUTTON_LABELS[:2]],
            [get_button(data, text, None) for data, text in Like.BUTTON_LABELS[2:]]
        ])
