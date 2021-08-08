from wikilistparser.classes.page import Page 


class ListPage(Page):

    _BASE_URL = 'https://en.wikipedia.org'
    _parsed_items = []

    def __init__(self, scrapy_response):
        super().__init__(scrapy_response)
        self.get_title()
        self.get_contents()

    def set_lists(self):
        for section in self.contents:
            self._parse_lists_by_section(section)

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