from wikilistparser.classes.page import Page, PageParseException


class PageTypeException(Exception):
    pass


class ListPage(Page):

    _BASE_URL = 'https://en.wikipedia.org'
    _parsed_items = []
    page_lists = []

    def __init__(self, scrapy_response):
        super().__init__(scrapy_response)
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
        if body.find_all('ul') is None:
            return False
        else:
            return True

    def _parse_lists_by_section(self, section):
        if section['subsections'] == []:
            items = self.soup.find('span', id=section['id']).find_next('ul')
            section['lists'] = self._parse_items(items)
        else:
            for subsection in section['subsections']:
                self._parse_lists_by_section(subsection)
                    
    def _parse_list_item(self, item):
        url = ''
        if item.find('a').get('href') is not None:
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
                self._append_and_update_master_list(lists, parsed_item)
            elif len(item.text.split('\n')) > 1:
                parsed_item['sublists'] = self._parse_items(item.find_next('ul'))
                self._append_and_update_master_list(lists, parsed_item)
        return lists

    def _append_and_update_master_list(self, lists, item):
        lists.append(item)
        self._parsed_items.append(item['title'])
    
    def _set_page_lists(self):
        self.soup.find('div', id='mw-hidden-catlinks').decompose()
        sections = self.soup.find('div', id='bodyContent').find_all('ul')
        for section in sections:
            self.page_lists.extend(self._parse_items(section))
        