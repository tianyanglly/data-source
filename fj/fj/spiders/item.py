import scrapy
from fj.spiders.base import BaseSpider


# 此接口用于获取所有，英雄，装备，符文，召唤师技能元数据
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：1月/次
class ItemSpider(BaseSpider):
    name = 'item'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1
    }

    def start_requests(self):
        reqs = [
            # dota
            # 装备
            self.get_url('/data-service/dota/raw/items'),
            # 英雄
            self.get_url('/data-service/dota/raw/heroes'),
            # lol
            # 装备
            self.get_url('/data-service/lol/raw/items', 'version=2'),
            # 英雄
            self.get_url('/data-service/lol/raw/heroes', 'version=2'),
            # 符文
            self.get_url('/data-service/lol/raw/runes', 'version=2'),
            # 召唤师技能
            self.get_url('/data-service/lol/raw/skills', 'version=2'),
            # kog
            # 英雄
            self.get_url('/data-service/kog/raw/heroes'),
            # 装备
            self.get_url('/data-service/kog/raw/items'),
            # 召唤师技能
            self.get_url('/data-service/kog/raw/skills')
        ]
        for req in reqs:
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.default_parse)
