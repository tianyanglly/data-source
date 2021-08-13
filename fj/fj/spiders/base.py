import json
import scrapy
import time
import hashlib
from urllib import parse
import fj.const as const


def get_response_data(response):
    body = json.loads(response.body)
    if body['code'] == 200:
        return body['data']
    else:
        raise Exception('{}:{}:{}'.format(body['code'], body['message'], response.request))


# 按指定长度切割数组
def cut(obj, sec):
    return [obj[i:i + sec] for i in range(0, len(obj), sec)]


class BaseSpider(scrapy.Spider):
    allowed_domains = ['esportsapi.feijing88.com']
    start_urls = []
    page = 1

    def default_parse(self, response):
        data = get_response_data(response)
        if data:
            game = self.get_game_name(response)
            if type(data) == dict:
                data['game'] = game
                yield data
            else:
                for item in data:
                    item['game'] = game
                    yield item

    def get_url(self, path, params=''):
        return {
            'url': '{}{}?{}'.format(self.settings.get('API_HOST'), path, params),
            'header': self.get_header(path)
        }

    # 获取当前游戏名
    def get_game_name(self, response):
        path = parse.urlparse(response.url).path
        path_arr = path.split('/')
        for p in path_arr:
            if p in const.GAME_LIST:
                return p
        return

    def get_page_str(self, version=False):
        limit = self.settings.get('REQ_LIMIT')
        offset = (self.page - 1) * limit
        params = '&offset={}&limit={}'.format(offset, limit)
        if version:
            params = params + '&version=2'
        return params

    def get_limit(self):
        return self.settings.get('REQ_LIMIT')

    def get_header(self, path):
        now = int(round(time.time() * 1000))
        sign = self.sign(now, path)
        return {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept-ApiAccess': self.settings.get('ACCESS_KEY'),
            'Accept-ApiSign': sign,
            'Accept-ClientTime': now
        }

    def sign(self, now, path):
        sign_str = '{}|{}|{}'.format(self.settings.get('SECRET_KEY'), now, path)
        m = hashlib.md5()
        m.update(sign_str.encode('utf-8'))
        sign = m.hexdigest()
        return sign.upper()
