import scrapy
from keep.spiders.base import BaseSpider, get_response_data


# 联赛列表
# 建议频率:1 天/1 次
class LeagueSpider(BaseSpider):
    name = 'league'

    def __init__(self, status=0, **kwargs):
        super().__init__(name=None, **kwargs)
        self.status = status

    def start_requests(self):
        yield scrapy.Request(url=self.get_url('/v1/competitions?sport=csgo&from=2020-01-01'), method='GET',
                             headers=self.get_header(),
                             callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data['competitions']:
                yield item
