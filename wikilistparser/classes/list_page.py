from wikilistparser.classes.page import Page, PageParseException
from wikilistparser.utilities.parse_utility import soup_attribute_exists

class PageTypeException(Exception):
    pass


class ListPage(Page):

    _BASE_URL = 'https://en.wikipedia.org'
    _parsed_items = []
    page_lists = []
    page_list_urls = []

    def __init__(self, scrapy_response, request_response=None):
        super().__init__(scrapy_response, request_response)
        try:
            self.set_contents()
        except PageParseException as e:
            if self._has_lists() and e.parse_error == 'Table of Contents not found':
                self._set_page_lists()

    def append_lists_to_contents(self):
        for section in self.contents:
            self._parse_lists_by_section(section)

    def _has_lists(self):
        body = self.soup.find('div', id='bodyContent')
        return soup_attribute_exists(body, 'ul')

    def _parse_lists_by_section(self, section):
        if section['subsections'] == []:
            items = self.soup.find('span', id=section['id']).find_next('ul')
            section['lists'] = self._parse_items(items)
        else:
            for subsection in section['subsections']:
                self._parse_lists_by_section(subsection)
                    
    def _parse_list_item(self, item):
        url = ''
        link = item.find('a').get('href')
        if link is not None and link.startswith('/wiki'):
            url = self._BASE_URL + item.find('a').get('href')
        result = {
            "title": item.find('a').text,
            "url": url
        }
        return result

    def _parse_items(self, items):
        lists = []
        for item in items.find_all('li'):
            parsed_item = self._parse_list_item(item)
            if parsed_item['title'] in self._parsed_items:
                continue
            if len(item.text.split('\n')) == 1:
                self._append_and_update_page_lists(lists, parsed_item)
            elif len(item.text.split('\n')) > 1:
                parsed_item['sublists'] = self._parse_items(item.find_next('ul'))
                self._append_and_update_page_lists(lists, parsed_item)
        return lists

    def _append_and_update_page_lists(self, lists, item):
        lists.append(item)
        self._parsed_items.append(item['title'])
        if item['url'] != '':
            self.page_list_urls.append(item['url'])
    
    def _set_page_lists(self):
        if soup_attribute_exists(self.soup, 'div', 'mw-hidden-catlinks', 'id'):
            self.soup.find('div', id='mw-hidden-catlinks').decompose()
        sections = self.soup.find('div', id='bodyContent').find_all('ul')
        for section in sections:
            self.page_lists.extend(self._parse_items(section))
        