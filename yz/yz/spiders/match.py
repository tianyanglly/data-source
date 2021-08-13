import scrapy
from yz.spiders.base import BaseSpider, get_header, get_response_data


# 未开始比赛列表
# 建议频率:1 小时/1 次
class MatchSpider(BaseSpider):
    name = 'match'

    def start_requests(self):
        yield scrapy.Request(url=self.get_url(resource='game', func='lists'), method='GET',
                             headers=get_header(),
                             callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item
                # 比赛详情
                yield scrapy.Request(url=self.get_url(resource='game', func='info', pri_id=item['game_id']),
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.detail_parse)

                # 早盘
                yield scrapy.Request(url=self.get_url(resource='dynamic', func='game', event_id=item['event_id'],
                                                      game_id=item['game_id']),
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.parse_bet)

                if item['have_roll'] == 1:
                    # 使用滚盘
                    yield scrapy.Request(url=self.get_url(resource='roll', func='use_roll', event_id=item['event_id'],
                                                          game_id=item['game_id']),
                                         method='GET',
                                         headers=get_header(),
                                         callback=self.parse_bet)

                    # 获取滚盘比赛动态信息
                    yield scrapy.Request(url=self.get_url(resource='roll', func='get_info', event_id=item['event_id'],
                                                          game_id=item['game_id']),
                                         method='GET',
                                         headers=get_header(),
                                         callback=self.parse_bet)
