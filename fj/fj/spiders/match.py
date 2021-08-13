import scrapy
from fj.spiders.base import BaseSpider, get_response_data
import fj.const as const

STATUS_HISTORY = 'all'  # 已结束历史数据
STATUS_SPECIAL = 'del'  # 删除/延迟
STATUS_TODAY = 'today'  # 当日结束


# scrapy crawl match -a status=all
# 比赛列表
# 频率限制: 1次/每秒
# 建议更新频率：15分钟/次
class MatchSpider(BaseSpider):
    name = 'match'
    status = 'today'
    day = '1'

    def __init__(self, game=None, status='today', day='1', **kwargs):
        super().__init__(game=game, **kwargs)
        self.status = status
        self.day = day

    def start_requests(self):
        # 5分钟/次 此接口用于获取状态为【已结束】的比赛及相关信息（时间倒序），可以用作历史数据库，获取历史数据
        if self.status == STATUS_HISTORY:
            reqs = [self.get_url('/data-service/dota/match/final_score',
                                 '{}&day={}'.format(self.get_page_str(), self.day)),
                    self.get_url('/data-service/csgo/match/final_score',
                                 '{}&day={}'.format(self.get_page_str(), self.day)),
                    self.get_url('/data-service/kog/match/final_score',
                                 '{}&day={}'.format(self.get_page_str(), self.day)),
                    self.get_url('/data-service/lol/match/final_score',
                                 '{}&day={}'.format(self.get_page_str(True), self.day))]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.parse_page)
        elif self.status == STATUS_SPECIAL:
            # 15分钟/次 删除/延迟
            reqs = [self.get_url('/data-service/dota/match/special', 'day=7'),
                    self.get_url('/data-service/kog/match/special', 'day=7'),
                    self.get_url('/data-service/csgo/match/special', 'day=7'),
                    self.get_url('/data-service/lol/match/special', 'day=7')]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.default_parse)
        else:
            # 1分钟/次 用于获取前一日19点至今天24点，比赛状态为【已结束】的比赛列表
            reqs = [self.get_url('/data-service/dota/match/today/end'),
                    self.get_url('/data-service/csgo/match/today/end'),
                    self.get_url('/data-service/kog/match/today/end'),
                    self.get_url('/data-service/lol/match/today/end')]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.parse)

    def parse_page(self, response):
        data = get_response_data(response)
        if data:
            game = self.get_game_name(response)
            for item in data:
                item['game'] = game
                yield item

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return

            self.page += 1
            if game == const.GAME_DOTA:
                req = self.get_url('/data-service/dota/match/final_score',
                                   '{}&day={}'.format(self.get_page_str(), self.day))
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/match/final_score',
                                   '{}&day={}'.format(self.get_page_str(True), self.day))
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/match/final_score',
                                   '{}&day={}'.format(self.get_page_str(), self.day))
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/match/final_score',
                                   '{}&day={}'.format(self.get_page_str(), self.day))
            else:
                return
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse_page)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            game = self.get_game_name(response)
            for item in data:
                item['game'] = game
                yield item
