from yz.spiders.base import BaseSpider, get_header, get_response_data
import scrapy


# 运营公告
# 建议频率:1 天/1 次
class GameSpider(BaseSpider):
    name = 'post'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url(resource='game', func='getAnnunciate'), method='GET', headers=get_header(),
                             callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data['list']:
            for item in data['list']:
                yield item
