from yz.spiders.base import BaseSpider, get_header, get_response_data
import scrapy


# 所有资讯列表
# 建议频率:1 天/1 次
class GameSpider(BaseSpider):
    name = 'news'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url(resource='news', func='lists'), method='GET', headers=get_header(),
                             callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item
                yield scrapy.Request(url=self.get_url(resource='news', func='info', news_id=item['news_id']),
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.parse_detail)

    def parse_detail(self, response):
        data = get_response_data(response)
        if data:
            yield data
