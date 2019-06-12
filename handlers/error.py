import logging

logger = logging.getLogger('request.{0}'.format(__file__))


def handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)
