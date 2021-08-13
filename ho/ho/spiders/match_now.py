import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import redis
import ho.const as const


# 接口描述
# 此接口用于获取状态为【进行中】的比赛及其battle_id等相关信息
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：15秒/次
class MatchNowSpider(BaseSpider):
    name = 'match_now'

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'RETRY_ENABLED': False
    }

    r = None

    def start_requests(self):
        self.r = redis.Redis(host=self.settings.get('REDIS_HOST'), port=self.settings.get('REDIS_PORT'),
                             decode_responses=True,
                             password=self.settings.get('REDIS_AUTH'))
        redis_key = '{}{}_{}'.format(self.settings.get('COLLECTION_PREFIX'), self.game, 'match_live')
        match_list = self.r.hgetall(redis_key)
        for match_id in match_list:
            battle_ids = match_list[match_id].split(',')
            # 滚球指数
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/bet_info/rolling?match_id={}'.format(match_id))
            else:
                url = self.get_url('/lol/match/bet_info/rolling?match_id={}&version=2'.format(match_id))
            yield scrapy.Request(
                url=url,
                method='GET',
                headers=get_header(),
                callback=self.default_parse)

            for battle_id in battle_ids:
                # 此接口用于获取（通过battle_id访问）正在进行的对局中的详细比赛时间，如人头数、推塔数等。该接口赛后也将支持访问，并且会多一些统计字段，比如XX率等
                # 注：
                # 有实时数据的比赛：battle_id会在选手进入地图前后返回
                # 没有实时数据的比赛：battle_id会在比赛结束一段时间后返回
                # 没有详细对局数据的比赛：battle_id将会缺失
                if self.game == const.GAME_DOTA:
                    url = self.get_url('/dota/match/battle?battle_id={}'.format(battle_id))
                else:
                    url = self.get_url('/lol/match/live_battle?battle_id={}&version=2'.format(battle_id))
                yield scrapy.Request(url=url,
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.parse_detail)

    def closed(self, reason):
        self.r.close()

    def parse_detail(self, response):
        data = get_response_data(response)
        if data:
            yield data
