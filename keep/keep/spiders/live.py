from keep.spiders.base import BaseSpider, get_response_data
import scrapy


# 实时数据
class GameSpider(BaseSpider):
    name = 'live'

    def start_requests(self):
        url = 'http://127.0.0.1:21001/keep/live'
        yield scrapy.Request(url=url, method='GET', headers=self.get_header(),
                             callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data['code'] == 200 and data['data']:
            for item in data['data']:
                item['fixtureId'] = item['payload']['fixtureId']
                yield item
