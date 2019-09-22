import os
import sys

TOKEN = os.environ.get('HEROKU_DEBUG') or sys.argv[1]
SITE = 'http://coreradio.ru'
FORCE_UPDATE = os.environ.get('FORCE_UPDATE') or sys.argv[2] or 0


class Configuration(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///utils/db.sqlite3?check_same_thread=False'
