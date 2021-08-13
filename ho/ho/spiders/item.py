import scrapy
from ho.spiders.base import BaseSpider, get_header
import ho.const as const


# 此接口用于获取所有装备元数据
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：1月/次
class ItemSpider(BaseSpider):
    name = 'item'

    def start_requests(self):
        if self.game == const.GAME_DOTA:
            url = self.get_url('/dota/raw/items')
        else:
            url = self.get_url('/lol/raw/items?version=2')
        yield scrapy.Request(url=url,
                             method='GET',
                             headers=get_header(),
                             callback=self.default_parse)
