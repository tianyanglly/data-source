import scrapy
from ho.spiders.base import BaseSpider, get_header


# 此接口用于获取所有召唤师技能元数据
# 限制说明
# 频率限制: 1次/每分钟
# 建议更新频率：1月/次
class SkillSpider(BaseSpider):
    name = 'skill'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url('/lol/raw/skills?version=2'),
                             method='GET',
                             headers=get_header(),
                             callback=self.default_parse)
