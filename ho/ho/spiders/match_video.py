import scrapy
from ho.spiders.base import BaseSpider, get_header
import redis
import ho.const as const


# 接口描述
# 此接口用于获取赛事直播地址
# 注：该接口返回的是第三方直播平台链接，不保证每场比赛都有直播链接数据，如有需要请另寻资源购买
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：5分钟/次
class MatchNowSpider(BaseSpider):
    name = 'match_video'

    r = None

    def start_requests(self):
        self.r = redis.Redis(host=self.settings.get('REDIS_HOST'), port=self.settings.get('REDIS_PORT'),
                             decode_responses=True,
                             password=self.settings.get('REDIS_AUTH'))
        redis_key = '{}{}_{}'.format(self.settings.get('COLLECTION_PREFIX'), self.game, 'match_live')
        match_ids = self.r.hkeys(redis_key)
        if match_ids:
            # 获取直播地址
            ids_str = ','.join(match_ids)
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/live_video?match_id={}'.format(ids_str))
            else:
                url = self.get_url('/lol/match/live_video?match_id={}&version=2'.format(ids_str))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

    def closed(self, reason):
        self.r.close()
