import redis
import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import ho.const as const


# 接口描述
# 此接口用于获取状态为【进行中】的比赛及其battle_id等相关信息
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：15秒/次
class MatchNowSpider(BaseSpider):
    name = 'match_live'

    def start_requests(self):
        if self.game == const.GAME_DOTA:
            url = self.get_url('/dota/match/live_score')
        else:
            url = self.get_url('/lol/match/live_score?version=2')
        yield scrapy.Request(url=url,
                             method='GET',
                             headers=get_header(),
                             callback=self.parse_detail)

    def parse_detail(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item
        else:
            # 清除redis缓存
            r = redis.Redis(host=self.settings.get('REDIS_HOST'), port=self.settings.get('REDIS_PORT'),
                            decode_responses=True,
                            password=self.settings.get('REDIS_AUTH'))
            redis_key = '{}{}_{}'.format(self.settings.get('COLLECTION_PREFIX'), self.game, 'match_live')
            r.delete(redis_key)
            r.close()
