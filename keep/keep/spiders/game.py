from keep.spiders.base import BaseSpider, get_response_data
import scrapy


# 所有游戏列表
# 建议频率:1 天/1 次
class GameSpider(BaseSpider):
    name = 'game'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url('/v1/sports'), method='GET', headers=self.get_header(),
                             callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data['sports']:
                yield item
