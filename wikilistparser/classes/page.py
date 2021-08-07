from bs4 import BeautifulSoup


class Page:

    title = ''
    contents = []

    def __init__(self, scrapy_response):
        self.url = scrapy_response.url
        self.soup = self._get_soup(scrapy_response)

    def get_title(self):
        try:
            return self.soup.find('title').text
        except AttributeError:
            return ''

    def get_contents(self):
        toc = self.soup.find('div', 'toc')
        

    def _get_soup(self, scrapy_response):
        return BeautifulSoup(scrapy_response.body, features='lxml')

    def _has_subsection(self):
        pass 