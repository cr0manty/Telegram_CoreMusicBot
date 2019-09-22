from app import db
from parsing import ParseSite
from models import Album

from threading import Thread
from time import sleep


# TODO:
# - search engine
# - optimize db update

def to_sec(time):
    time = time.split(':')
    if time[1] == 'min':
        return int(time[0]) * 60
    elif time[1] == 'hour':
        return int(time[0]) * 3600
    elif time[1] == 'day':
        return int(time[0]) * 3600 * 24
    else:
        return int(time[0])


class Updater(Thread):
    page = '/page/{}/'

    def __init__(self, parse, site, full_update):
        Thread.__init__(self, daemon=True)
        self.parse = parse
        self.site = site
        self.last_page = self.parse.last_page(self.site)
        self.end_page = self.last_page
        self.full_update = full_update

    def check_for_update(self):
        if self.full_update:
            self.end_page = 1
            return True

        db_elements = Album.query.count()
        per_page = len(self.parse.get_elements(self.site))
        last_elements = len(self.parse.get_elements(
            self.site + self.page.format(self.last_page)))
        site_elements = (self.last_page - 1) * per_page + last_elements
        if site_elements == db_elements:
            return False
        elif site_elements > db_elements:
            self.end_page = int((site_elements - db_elements) / 20)
            return True

    def run(self):
        while True:
            if self.check_for_update():
                for i in range(self.end_page, 0, -1):
                    try:
                        self.parse.set_info(self.site + self.page.format(i))
                    except Exception as e:
                        print("Exception called from Updater:\n'{}'".format(e))
                        i += 1
                sleep(to_sec('12:hour'))


class Saver(Thread):
    def __init__(self, parse):
        Thread.__init__(self, daemon=True)
        self.parse = parse
        self.last_save = Album.query.count()

    def run(self):
        sleep(to_sec('0:min'))
        while True:
            for i in range(self.last_save, len(self.parse)):
                album = Album.query.filter_by(name=self.parse[i]['name']).first()
                if album is None:
                    try:
                        album = Album(self.parse[i])
                        db.session.add(album)
                        self.last_save += 1
                    except Exception as e:
                        pass
                if not i % 50:
                    db.session.commit()
            sleep(to_sec('0:min'))


class UpdateDB(Thread):
    def __init__(self, site, full_update):
        Thread.__init__(self, daemon=True)
        self.parse = ParseSite()
        self.site = site
        self.full_update = full_update

    def run(self):
        parsing = Updater(self.parse, self.site, self.full_update)
        saver = Saver(self.parse)
        parsing.start()
        saver.start()
        saver.join()


def start_update(site, full_update=False):
    update = UpdateDB(site, full_update)
    update.start()
