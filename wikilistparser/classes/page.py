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
        for section in toc.find('ul').find_all('li', 'toclevel-1'):
            top_section = self._parse_section(section)
            if (self._has_subsection(section)):
                top_section['subsections'] = self._parse_subsections(section)
            self.contents.append(top_section)

    def _get_soup(self, scrapy_response):
        return BeautifulSoup(scrapy_response.body, features='lxml')

    def _has_subsection(self, section):
        if (len(section.find_all('li')) > 0):
            return True
        else:
            return False
    
    def _get_subsection_list(self, section):
        subsection_class = section.find('li').get('class')[0]
        return section.find_all('li', subsection_class)

    def _parse_subsections(self, section):
        subsections = self._get_subsection_list(section)
        parsed_subsections = []
        for subsection in subsections:
            parsed_section = self._parse_section(subsection)
            if (self._has_subsection(subsection)):
                parsed_section['subsections'] = self._parse_subsections(subsection)
            parsed_subsections.append(parsed_section)
        return parsed_subsections

    def _parse_section(self, section):
        result = {
            "section": section.find('span', 'toctext').text,
            "number": section.find('span', 'tocnumber').text,
            "id": section.find('a').get('href').replace('#', ''),
            "subsections": []
        }
        return result
