import scrapy
from yz.spiders.base import BaseSpider, get_header, get_response_data
from yz.const import GAME_LIST
from urllib import parse

STATUS_ALL = 'all'
STATUS_NOT = 'not'


# 联赛列表
# 建议频率:1 天/1 次
class LeagueSpider(BaseSpider):
    name = 'league'

    def __init__(self, status=0, **kwargs):
        super().__init__(name=None, **kwargs)
        self.status = status

    def start_requests(self):
        for game_id in GAME_LIST:
            if self.status == STATUS_ALL:
                # 建议频率:1 天/1 次
                yield scrapy.Request(url=self.get_url(resource='event', func='matches', event_id=game_id), method='GET',
                                     headers=get_header(),
                                     callback=self.default_parse)
            else:
                # 2h/1 次 项目未开始和进行中的赛事专题列表
                yield scrapy.Request(url=self.get_url(resource='special', func='lists', event_id=game_id), method='GET',
                                     headers=get_header(),
                                     callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            params = parse.parse_qs(parse.urlparse(response.url).query)
            event_id = params['event_id'][0]
            for item in data:
                item['event_id'] = event_id
                yield item

                yield scrapy.Request(url=self.get_url(resource='special', func='info', pri_id=item['match_id']),
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data:
            yield data
