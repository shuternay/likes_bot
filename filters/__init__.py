import telegram
from telegram.ext import BaseFilter

from project import settings


class ExcludeSelfForwardFilter(BaseFilter):
    def filter(self, message: telegram.Message):
        return not (message.forward_from and message.forward_from.id == message.bot.id)


class ExcludeTagFilter(BaseFilter):
    def filter(self, message: telegram.Message):
        caption = message.caption or ''
        return all(('#{0}'.format(tag) not in caption for tag in settings.EXCLUDE_TAGS))


class IncludeTagFilter(BaseFilter):
    def filter(self, message: telegram.Message):
        caption = message.text or ''
        return any(('#{0}'.format(tag) in caption for tag in settings.INCLUDE_TAGS))