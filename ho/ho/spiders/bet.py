import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import ho.const as const


# 早盘指数
# 此接口用于获取某场比赛的赔率数据，这些赔率数据都是早盘赔率，即比赛开始前，指数会正常更新，比赛开始后，指数停止更新
# 注意：该接口所有数据均同步自对应的官方竞猜平台，仅推荐展示使用
# 滚球指数
# 此接口用于获取比赛开始后，即时变化的赔率数据
# 注意：该接口所有数据均同步自对应的官方竞猜平台，仅推荐展示使用
# 建议更新频率：15分钟/次
class BetSpider(BaseSpider):
    name = 'bet'

    def start_requests(self):
        # 未开赛：15分钟/次
        if self.game == const.GAME_DOTA:
            url = self.get_url('/dota/match/recently?{}'.format(self.get_page_str()))
        else:
            url = self.get_url('/lol/match/recently?{}&version=2'.format(self.get_page_str()))
        yield scrapy.Request(url=url,
                             method='GET',
                             headers=get_header(),
                             callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item
                # 早盘指数
                if self.game == const.GAME_DOTA:
                    url = self.get_url('/dota/match/bet_info?match_id={}'.format(item['match_id']))
                else:
                    url = self.get_url('/lol/match/bet_info?match_id={}&version=2'.format(item['match_id']))
                yield scrapy.Request(url=url,
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.default_parse)

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return
            self.page += 1
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/recently?{}'.format(self.get_page_str()))
            else:
                url = self.get_url('/lol/match/recently?{}&version=2'.format(self.get_page_str()))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse)
