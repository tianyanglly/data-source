import redis
import scrapy
from fj.spiders.base import BaseSpider, get_response_data


# 接口描述
# 此接口用于获取状态为【进行中】的比赛及其battle_id等相关信息
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：15秒/次
class MatchNowSpider(BaseSpider):
    name = 'match_live'

    r = None

    def start_requests(self):
        reqs = [self.get_url('/data-service/dota/match/live_score'),
                self.get_url('/data-service/csgo/match/live_score'),
                self.get_url('/data-service/kog/match/live_score'),
                self.get_url('/data-service/lol/match/live_score', 'version=2')]
        for req in reqs:
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse_detail)

    def parse_detail(self, response):
        data = get_response_data(response)
        game = self.get_game_name(response)
        if data:
            for item in data:
                item['game'] = game
                yield item
        else:
            # 清除redis缓存
            self.r = redis.Redis(host=self.settings.get('REDIS_HOST'), port=self.settings.get('REDIS_PORT'),
                                 decode_responses=True,
                                 password=self.settings.get('REDIS_AUTH'))
            redis_key = '{}{}_{}'.format(self.settings.get('COLLECTION_PREFIX'), game, 'match_live')
            self.r.delete(redis_key)

    def closed(self, reason):
        if self.r is not None:
            self.r.close()
