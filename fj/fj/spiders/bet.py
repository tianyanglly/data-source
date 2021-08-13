import scrapy
from fj.spiders.base import BaseSpider, get_response_data
import fj.const as const


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
        reqs = [self.get_url('/data-service/dota/match/recently', self.get_page_str()),
                self.get_url('/data-service/csgo/match/recently', self.get_page_str()),
                self.get_url('/data-service/kog/match/recently', self.get_page_str()),
                self.get_url('/data-service/lol/match/recently', self.get_page_str(True))]
        for req in reqs:
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            game = self.get_game_name(response)
            for item in data:
                item['game'] = game
                ids.append(str(item['match_id']))
                yield item
            ids_str = ','.join(ids)
            # 早盘指数
            if game == const.GAME_DOTA:
                req = self.get_url('/data-service/dota/match/bet_info', 'match_id={}'.format(ids_str))
                req_detail = self.get_url('/data-service/dota/match/basic_info', 'match_id={}'.format(ids_str))
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/match/bet_info', 'match_id={}'.format(ids_str))
                req_detail = self.get_url('/data-service/kog/match/basic_info', 'match_id={}'.format(ids_str))
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/match/bet_info', 'match_id={}'.format(ids_str))
                req_detail = self.get_url('/data-service/csgo/match/basic_info', 'match_id={}'.format(ids_str))
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/match/bet_info',
                                   'match_id={}&version=2'.format(ids_str))
                req_detail = self.get_url('/data-service/lol/match/basic_info', 'match_id={}&version=2'.format(ids_str))
            else:
                return
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.default_parse)

            # 获取详情
            yield scrapy.Request(url=req_detail['url'],
                                 method='GET',
                                 headers=req_detail['header'],
                                 callback=self.default_parse)

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return
            self.page += 1
            if game == const.GAME_DOTA:
                req = self.get_url('/data-service/dota/match/recently', self.get_page_str())
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/match/recently', self.get_page_str())
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/match/recently', self.get_page_str())
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/match/recently', self.get_page_str(True))
            else:
                return
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse)
