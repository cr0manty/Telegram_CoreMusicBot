import requests

from bs4 import BeautifulSoup
from datetime import date
from urllib import request


class Item:
    def __init__(self, context):
        self.info = context
        self.create_date()

    def song_str(self):
        if not self.info.get('songs'):
            return 'Songs list is empty'
        string = ''
        for i in self.info.get('songs'):
            if i[-1] == '>':
                i = i[0:-5]
            string += '{}\n'.format(i)
        return string

    def __str__(self):
        return '*{}*\n\nGenre: {}\n' \
               'Country: {}\nRelease date:\n{}\n\n' \
               'Song list:\n{}'.format(self.info.get('name'), self.info.get('genre'),
                                       self.info.get('country'),
                                       self.info.get('date').strftime('%d %B %Y'),
                                       self.song_str())

    def __getitem__(self, index):
        return self.info[index]

    def load_img(self):
        try:
            img_dir = 'utils/logo.png'
            file = open(img_dir, 'wb')
            file.write(request.urlopen(self.info.get('img')).read())
            file.close()
        except Exception as e:
            img_dir = 'utils/default.png'
        return img_dir

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
            _date = self.info.get('date').split(' ')
            day = int(_date[2][0:-1])
            month = self.month_to_num(_date[1])
            year = int(_date[3])
            self.info['date'] = date(year=year, month=month,
                                     day=day)
        except Exception as e:
            try:
                self.info['date'] = date.today()
            except Exception as e:
                raise Exception("'create_date' error with '{}'".format(e))


class ParseSite:
    items = []
    length = 0

    @staticmethod
    def get_html(site):
        return requests.get(site).text

    @staticmethod
    def cut(string, begin_symbol=None, end_symbol=None):
        begin = 0 if begin_symbol is None else string.find(begin_symbol) + 1
        end = -1 if end_symbol is None else string.rfind(end_symbol)
        return string[begin:end]

    def page_info(self, site):
        soup = BeautifulSoup(self.get_html(site),
                             features='html.parser')
        return soup.find_all('li', class_='tcarusel-item main-news')

    def get_page_elements(self, site):
        try:
            item_list = self.page_info(site)
            for i in item_list:
                info_link = i.find('a').get('href')
                self.items.append(Item(self.album_info(info_link)))
        except Exception as e:
            raise Exception("'set_info' error with '{}'".format(e))

    def try_add_date(self, info):
        for i in info:
            if str(i).find('Date:') != -1:
                return self.cut(str(i), begin_symbol=':', end_symbol='.')
        return ' '

    def album_info(self, url):
        try:
            context = dict()
            context['info'] = url
            soup = BeautifulSoup(self.get_html(url), features='html.parser')
            main_content = soup.find_all('a')
            for i in reversed(main_content):
                i = i.find('img')
                if i:
                    main_content = i
                    break
            context['name'] = main_content.get('alt')
            context['img'] = main_content.get('src')
            download_link = soup.find('div', class_='quote')
            if download_link:
                context['download'] = self.cut(download_link.find('a').get('href'),
                                               begin_symbol='=')
            else:
                context['download'] = 'https://google.com/'
            context['date'] = self.try_add_date(
                soup.find_all('div', class_='fullo-news-line'))
            album_info = soup.find('div', class_='full-news-info').find_all('br')
            context['genre'] = str(album_info[0].previous_sibling) if album_info else ' '
            context['country'] = str(album_info[1].previous_sibling) if album_info else ' '
            songs = []
            try:
                for i in range(4, len(album_info)):
                    songs.append(str(album_info[i].previous_sibling))
                context['songs'] = songs or None
            except Exception:
                pass
            self.length += 1
            return context
        except Exception as e:
            raise Exception("'take_info' error with '{}'".format(e))

    def find_result(self, site):
        soup = BeautifulSoup(self.get_html(site),
                             features='html.parser')
        return soup.find('div', class_='s-block-content').text.split(' ')[1]

    def last_page(self, url):
        soup = BeautifulSoup(self.get_html(url), features='html.parser')
        page = soup.find('div', class_='navigation').find_all('a')[9].text
        return int(page)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return self

    def __next__(self):
        if self.length != 0:
            self.length -= 1
            return self.items[self.length]
        else:
            self.length = self.__len__()
            raise StopIteration

    def __getitem__(self, index):
        return self.items[index]
