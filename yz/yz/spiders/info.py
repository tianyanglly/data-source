from yz.spiders.base import BaseSpider, get_header, get_response_data
import scrapy
from urllib import parse


# 获取比赛或者盘口信息
class GameSpider(BaseSpider):
    name = 'info'

    def __init__(self, func=None, game_id=None, event_id=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.func = func
        self.game_id = game_id
        self.event_id = event_id

    def start_requests(self):
        if self.func == 'game_info':
            yield scrapy.Request(url=self.get_url(resource='game', func='info', pri_id=self.game_id),
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.detail_parse)
        elif self.func == 'bet_info':
            # 早盘
            yield scrapy.Request(url=self.get_url(resource='dynamic', func='game', game_id=self.game_id),
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse_bet)
        elif self.func == 'roll_bet_info':
            # 使用滚盘
            yield scrapy.Request(url=self.get_url(resource='roll', func='use_roll', event_id=self.event_id,
                                                  game_id=self.game_id),
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse_bet)

            # 获取滚盘比赛动态信息
            yield scrapy.Request(url=self.get_url(resource='roll', func='get_info', event_id=self.event_id,
                                                  game_id=self.game_id),
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse_bet)
