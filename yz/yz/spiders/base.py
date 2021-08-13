import json
import scrapy
import time
import hashlib
from urllib.parse import urlencode
from urllib import parse


def get_response_data(response):
    body = json.loads(response.body)
    if 'error_code' in body.keys():
        print(body)
        return
    if body['code'] == 200:
        return body['data']
    else:
        raise Exception('{}:{}'.format(body['code'], body['msg']))


def get_header():
    return {'Content-Type': 'application/json'}


class BaseSpider(scrapy.Spider):
    allowed_domains = ['34.96.253.12']
    start_urls = []

    def default_parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item

    # 赔率
    def parse_bet(self, response):
        data = get_response_data(response)
        if data:
            if data['guess']:
                params = parse.parse_qs(parse.urlparse(response.url).query)
                for guess in data['guess']:
                    guess['game_id'] = params['game_id'][0]
                    guess['event_id'] = params['event_id'][0]
                    yield guess

    # 赛事详情
    def detail_parse(self, response):
        data = get_response_data(response)
        if data:
            data['data_type'] = 'detail'
            yield data

    def get_url(self, resource, func, event_id=None, pri_id=None, game_id=None, news_id=None):
        params = {
            'app_key': self.settings.get('APP_KEY'),
            'app_secret': self.settings.get('APP_SECRET'),
            'func': func,
            'resource': resource,
            'timestamp': int(round(time.time() * 1000)),
        }
        if pri_id is not None:
            params['id'] = pri_id
        if event_id is not None:
            params['event_id'] = event_id
        if game_id is not None:
            params['game_id'] = game_id
        if news_id is not None:
            params['news_id'] = news_id
        p = sorted(params.items(), key=lambda x: x[0])
        new_params = {}
        for i in p:
            new_params[i[0]] = i[1]
        path = urlencode(new_params)
        m = hashlib.md5()
        m.update(path.encode('utf-8'))
        sign = m.hexdigest()
        url = self.settings.get('API_HOST') + path + "&sign=" + sign
        return url
