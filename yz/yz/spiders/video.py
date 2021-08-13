from yz.spiders.base import BaseSpider, get_header
import scrapy


# 所有游戏列表
# 建议频率:1 天/1 次
class GameSpider(BaseSpider):
    name = 'video'

    def __init__(self, game_id=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.game_id = game_id

    def start_requests(self):
        yield scrapy.Request(url=self.get_url(resource='live', func='get_video', game_id=self.game_id), method='GET',
                             headers=get_header(),
                             callback=self.default_parse)
