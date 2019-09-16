import requests

from urllib import request

from bs4 import BeautifulSoup
from datetime import date


class Item:
    def __init__(self, context):
        self.items = context
        self.create_date()

    def get(self, index):
        return self.items.get(index)

    def song_str(self):
        string = ''
        for i in self.items.get('songs'):
            if i[-1] == '>':
                i = i[0:-5]
            string += '{}\n'.format(i)
        return string if string else 'Songs list is empty'

    def load_img(self):
        try:
            img_dir = 'utils/logo.png'
            file = open(img_dir, 'wb')
            file.write(request.urlopen(self.items.get('img')).read())
            file.close()
        except Exception:
            img_dir = 'utils/default.png'
        return img_dir

    def __str__(self):
        return '*{}*\n\nGenre: {}\n' \
               'Country: {}\nRelease date: {}\n\n' \
               'Song list:\n{}'.format(self.items.get('name'), self.items.get('genre'),
                                       self.items.get('country'), self.items.get('date'),
                                       self.song_str())

    @staticmethod
    def month_to_num(string):
        month = {
            'jan': 1, 'feb': 2, 'mar': 3,
            'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9,
            'oct': 10, 'nov': 11, 'dec': 12
        }
        month_abr = string.strip()[:3].lower()
        try:
            return month[month_abr]
        except:
            raise ValueError('Not a month')

    def create_date(self):
        try:
            if not self.items['date']:
                self.items['date'] = date.today()
            else:
                _date = self.items['date'].split(' ')
                day = int(_date[2][0:-1])
                month = self.month_to_num(_date[1])
                year = int(_date[3])
                self.items['date'] = date(year=year,
                                      month=month,
                                      day=day)
        except Exception as e:
            raise Exception("'create_date' error with '{}'".format(e))


class ParseSite:
    items = []
    index = 0
    page = 0

    @staticmethod
    def get_html(site):
        return requests.get(site).text

    @staticmethod
    def cut(string, begin_symbol=None, end_symbol=None):
        begin = 0 if begin_symbol is None else string.find(begin_symbol) + 1
        end = -1 if end_symbol is None else string.rfind(end_symbol)
        return string[begin:end]

    def set_info(self, site):
        try:
            soup = BeautifulSoup(self.get_html(site),
                             features='html.parser')
            item_list = soup.find_all('li', class_='tcarusel-item main-news')
            for i in item_list:
                info_link = i.find('a').get('href')
                self.items.append(Item(self.take_info(info_link)))
            self.index = len(self.items)
            self.page += 1
        except Exception as e:
            raise Exception("'set_info' error with '{}'".format(e))

    def take_info(self, url):
        context = dict()
        try:
            soup = BeautifulSoup(self.get_html(url), features='html.parser')
            main_content = soup.find('center').find('a')
            context['name'] = main_content.find('img').get('alt')
            context['img'] = main_content.find('img').get('src')
            context['download'] = self.cut(
                soup.find('div', class_='quote').find('a').get('href'),
                begin_symbol='='
            )
            context['date'] = self.cut(
                str(soup.find_all('div', class_='fullo-news-line')[3]),
                begin_symbol=':', end_symbol='.'
            )
            album_info = soup.find('div', class_='full-news-info').find_all('br')
            context['genre'] = str(album_info[0].previous_sibling)
            context['country'] = str(album_info[1].previous_sibling)
            songs = []
            for i in range(4, len(album_info)):
                songs.append(str(album_info[i].previous_sibling))
            context['songs'] = songs
        except Exception as e:
            raise Exception("'take_info' error with '{}'".format(e))
        return context

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index != 0:
            self.index -= 1
            return self.items[self.index]
        else:
            self.index = self.__len__()
            raise StopIteration

    def __getitem__(self, index):
        return self.items[index]
