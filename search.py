from parsing import ParseSite
from config import SITE


class SearchEngine:
    for_search = '/index.php?do=search&'\
                 'subaction=search&search_start={}'\
                 '&full_search=0&result_from={}&story={}'

    def __init__(self, site):
        self.site = site
        self.parser = ParseSite()
        self.result = 0

    def start(self, text):
        search_str = self.for_search.format(1, 1, text)
        self.result = int(self.parser.find_result(self.site + search_str))
        for i in range(0, round(self.result/20)):
            try:
                search_str = self.for_search.format(i + 1, 20 * i + 1, text.replace(' ', '+'))
                self.parser.get_page_elements(self.site + search_str)
            except:
                continue


if __name__ == '__main__':
    search = SearchEngine(SITE)
    search.start('bring')
