import scrapy
import json
from wikilistparser.classes.list_page import ListPage


class ListSpider(scrapy.Spider):

    name = 'list_of_lists'

    def __init__(self, **kwargs):
        with open('wikilistparser/playground/results_w_start_urls.json', 'r') as f:
            static_list_results = json.load(f)
            self.start_urls = static_list_results[0]['urls']
        super(ListSpider, self).__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        p = ListPage(response)
        p.set_title()
        p.append_lists_to_contents()
        if p.has_table_of_contents:
            yield { 'page_title': p.title, 'page_contents': p.contents }
        else:
            yield { 'page_title': p.title, 'page_lists': p.page_lists }