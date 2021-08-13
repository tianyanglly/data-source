import scrapy
from fj.spiders.base import BaseSpider, get_response_data
import redis
import fj.const as const


# 接口描述
# 此接口用于获取状态为【进行中】的比赛及其battle_id等相关信息
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：15秒/次
class MatchNowSpider(BaseSpider):
    name = 'match_now'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_ENABLED': False
    }

    r = None

    def start_requests(self):
        self.r = redis.Redis(host=self.settings.get('REDIS_HOST'), port=self.settings.get('REDIS_PORT'),
                             decode_responses=True,
                             password=self.settings.get('REDIS_AUTH'))

        for game in const.GAME_LIST:
            if game in [const.GAME_KOG]:
                # 王者荣耀没有实时数据，csgo单独处理
                continue
            redis_key = '{}{}_{}'.format(self.settings.get('COLLECTION_PREFIX'), game, 'match_live')
            match_list = self.r.hgetall(redis_key)
            if not match_list:
                continue
            ids = []
            for match_id in match_list:
                ids.append(str(match_id))
                battle_ids = match_list[match_id].split(',')
                # csgo地图，获取战役
                for battle_id in battle_ids:
                    # 此接口用于获取（通过battle_id访问）正在进行的对局中的详细比赛时间，如人头数、推塔数等。该接口赛后也将支持访问，并且会多一些统计字段，比如XX率等
                    # 注：
                    # 有实时数据的比赛：battle_id会在选手进入地图前后返回
                    # 没有实时数据的比赛：battle_id会在比赛结束一段时间后返回
                    # 没有详细对局数据的比赛：battle_id将会缺失
                    if game == const.GAME_DOTA:
                        req = self.get_url('/data-service/dota/match/battle', 'battle_id={}'.format(battle_id))
                    elif game == const.GAME_LOL:
                        req = self.get_url('/data-service/lol/match/live_battle',
                                           'battle_id={}&version=2'.format(battle_id))
                    elif game == const.GAME_CSGO:
                        req = self.get_url('/data-service/csgo/battle/live',
                                           'match_id={}&map_name={}'.format(match_id, battle_id))
                    else:
                        continue
                    yield scrapy.Request(url=req['url'],
                                         method='GET',
                                         headers=req['header'],
                                         callback=self.parse_detail)

            # 滚球指数
            ids_str = ','.join(ids)
            if game == const.GAME_DOTA:
                req_roll = self.get_url('/data-service/dota/match/bet_info/rolling',
                                        'match_id={}'.format(ids_str))
            elif game == const.GAME_LOL:
                req_roll = self.get_url('/data-service/lol/match/bet_info/rolling',
                                        'match_id={}&version=2'.format(ids_str))
            else:
                continue
            yield scrapy.Request(
                url=req_roll['url'],
                method='GET',
                headers=req_roll['header'],
                callback=self.default_parse)

    def closed(self, reason):
        self.r.close()

    def parse_detail(self, response):
        data = get_response_data(response)
        game = self.get_game_name(response)
        if data:
            data['game'] = game
            yield data
