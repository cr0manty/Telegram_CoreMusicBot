from bot import site_view, bot_view

from utils.app import bot
from utils.updater import start_update
from utils.config import SITE, FORCE_UPDATE

if __name__ == '__main__':
    start_update(SITE, FORCE_UPDATE)
    bot.start()
