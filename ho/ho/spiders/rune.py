import scrapy
from ho.spiders.base import BaseSpider, get_header


# 此接口用于获取所有符文数据
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：1月/次
class RuneSpider(BaseSpider):
    name = 'rune'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url('/lol/raw/runes?version=2'),
                             method='GET',
                             headers=get_header(),
                             callback=self.default_parse)
