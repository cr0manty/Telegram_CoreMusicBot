import os
import webbrowser

from telebot import TeleBot

from parsing import ParseSite
from config import SITE


class StartBot(TeleBot):
    web_hook_url = 'https://core-bot-telegram.herokuapp.com/'

    def __init__(self, server, token, debug=False):
        self.token = token
        super().__init__(token)
        self.parse = ParseSite()
        self.index = 0 * self.parse.page
        self.server = server
        self.DEBUG = bool(os.environ.get('HEROKU_DEBUG') or debug)
        self.WEB = bool('HEROKU_DEBUG' in list(os.environ.keys()))
        self.remove_webhook()

    def start(self):
        self.parse.set_info(SITE)
        if self.WEB:
            self.set_webhook(url=self.web_hook_url + self.token)
            self.server.run(host='0.0.0.0',
                            port=int(os.environ.get('PORT', 5000)),
                            debug=self.DEBUG)
        else:
            self.polling()

    def debug(self):
        return self.DEBUG

    def msg_error(self, chat_id, exception, command):
        self.send_message(chat_id, "Exception called in '{}' with text: '{}'".
                          format(command, exception)
                          )

    def send_post(self, chat_id, item, reply_markup=None):
        img = open(item.load_img(), 'rb')
        self.send_photo(chat_id, img, str(item), parse_mode='Markdown', reply_markup=reply_markup)
        img.close()

    def open_web_link(self):
        webbrowser.open(self.parse.items[self.index].get('download'))

    def get_item(self):
        return self.parse.items[self.index]

