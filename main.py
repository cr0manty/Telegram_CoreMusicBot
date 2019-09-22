import bot_view
import site_view

from app import bot
from updater import start_update
from config import SITE, FORCE_UPDATE

if __name__ == '__main__':
    start_update(SITE, FORCE_UPDATE)
    bot.start()
