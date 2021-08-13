import scrapy
from fj.spiders.base import BaseSpider
import fj.const as const


# 接口描述
# 此接口用于获取赛事直播地址
# 注：该接口返回的是第三方直播平台链接，不保证每场比赛都有直播链接数据，如有需要请另寻资源购买
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：5分钟/次
class MatchNowSpider(BaseSpider):
    name = 'match_video'

    def __init__(self, game=None, match_id=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.game = game
        self.match_id = match_id

    def start_requests(self):
        if self.game == const.GAME_DOTA:
            req = self.get_url('/data-service/dota/match/live_video', 'match_id={}'.format(self.match_id))
        elif self.game == const.GAME_CSGO:
            req = self.get_url('/data-service/csgo/match/live_video', 'match_id={}'.format(self.match_id))
        elif self.game == const.GAME_KOG:
            req = self.get_url(' /data-service/kog/match/live_video', 'match_id={}'.format(self.match_id))
        elif self.game == const.GAME_LOL:
            req = self.get_url('/data-service/lol/match/live_video', 'match_id={}&version=2'.format(self.match_id))
        else:
            return
        yield scrapy.Request(url=req['url'],
                             method='GET',
                             headers=req['header'],
                             callback=self.default_parse)

