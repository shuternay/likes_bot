import os
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

current_config_path = os.path.join(BASE_DIR, 'conf', 'current.conf')
default_config_path = os.path.join(BASE_DIR, 'conf', 'default.conf')

if os.path.exists(current_config_path):
    config_path = current_config_path
else:
    config_path = default_config_path

config = ConfigParser()
config.read(config_path)

# Main
DEBUG = config.getboolean('main', 'DEBUG')
DELETE_THRESHOLD = config.getint('main', 'DELETE_THRESHOLD')
INCLUDE_TAGS = [x.strip() for x in config.get('main', 'INCLUDE_TAGS').split(',')]
EXCLUDE_TAGS = [x.strip() for x in config.get('main', 'EXCLUDE_TAGS').split(',')]

# Telegram
POLL_INTERVAL = config.getfloat('telegram', 'POLL_INTERVAL')
TELEGRAM_TOKEN = config.get('telegram', 'TOKEN')

# Database
DB_ENGINE = config.get('db', 'ENGINE')
DB_PARAMS = {
    'database': config.get('db', 'NAME'),
    'user': config.get('db', 'USER', fallback=None),
    'password': config.get('db', 'PASSWORD', fallback=None),
    'host': config.get('db', 'HOST', fallback=None),
    'port': config.getint('db', 'PORT', fallback=None),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(module)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'facility': 'user',
        },
    },
    'loggers': {
        'request': {
            'handlers': ['console', 'syslog', ],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': True,
        },
        'peewee': {
            'handlers': ['console', 'syslog', ],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['console', 'syslog', ],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
