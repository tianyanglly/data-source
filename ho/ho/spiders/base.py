import json
import scrapy


def get_header():
    return {'Content-Type': 'application/json'}


def get_response_data(response):
    body = json.loads(response.body)
    if body['code'] == 200:
        return body['data']
    else:
        return False


class BaseSpider(scrapy.Spider):
    allowed_domains = ['34.96.253.12']
    start_urls = []
    page = 1
    game = 'lol'  # 当前游戏

    def __init__(self, game=None, **kwargs):
        super().__init__(name=None, **kwargs)
        if game:
            self.game = game

    def default_parse(self, response):
        body = json.loads(response.body)
        if body['code'] == 200:
            for item in body['data']:
                yield item

    def get_url(self, path):
        return self.settings.get('API_HOST') + path

    def get_page_str(self):
        limit = self.settings.get('REQ_LIMIT')
        offset = (self.page - 1) * limit
        return 'offset={}&limit={}'.format(offset, limit)

    def get_limit(self):
        return self.settings.get('REQ_LIMIT')
