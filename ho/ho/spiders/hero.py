import scrapy
from ho.spiders.base import BaseSpider, get_header
import ho.const as const


# 此接口用于获取所有英雄数据
# 限制说明
# 频率限制: 1次/每分钟
# 建议更新频率：1月/次
class HeroSpider(BaseSpider):
    name = 'hero'

    def start_requests(self):
        if self.game == const.GAME_DOTA:
            url = self.get_url('/dota/raw/heroes')
        else:
            url = self.get_url('/lol/raw/heroes?version=2')
        yield scrapy.Request(url=url,
                             method='GET',
                             headers=get_header(),
                             callback=self.default_parse)
