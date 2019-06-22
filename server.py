import initdb
import logging.config

from telegram.ext import Updater

from handlers import echo, error, like, text
from project import settings

logger = logging.getLogger('main')


def main():
    logging.config.dictConfig(settings.LOGGING)
    updater = Updater(settings.TELEGRAM_TOKEN)

    initdb.create_tables()

    dp = updater.dispatcher
    dp.add_handler(echo.handler)
    dp.add_handler(text.handler)
    dp.add_handler(like.handler)
    dp.add_error_handler(error.handler)

    updater.start_polling(poll_interval=settings.POLL_INTERVAL)
    logger.info('Бот запущен.')
    updater.idle()
    logger.info('Бот остановлен.')


if __name__ == '__main__':
    main()
