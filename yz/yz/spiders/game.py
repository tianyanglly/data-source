from yz.spiders.base import BaseSpider, get_header
import scrapy


# 所有游戏列表
# 建议频率:1 天/1 次
class GameSpider(BaseSpider):
    name = 'game'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url('event', 'events', event_id=1), method='GET', headers=get_header(),
                             callback=self.default_parse)
