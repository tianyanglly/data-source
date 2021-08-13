import scrapy
from fj.spiders.base import BaseSpider, get_response_data
import fj.const as const


# 接口描述
# 此接口用于获取所有的战队的列表
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：1月/次
class TeamSpider(BaseSpider):
    name = 'team'

    def start_requests(self):
        reqs = [self.get_url('/data-service/dota/team/list', self.get_page_str()),
                self.get_url('/data-service/csgo/team/list', self.get_page_str()),
                self.get_url('/data-service/kog/team/list', self.get_page_str()),
                self.get_url('/data-service/lol/team/list', self.get_page_str(True))]
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
                ids.append(str(item['team_id']))
                yield item

            ids_str = ','.join(ids)
            if game == const.GAME_DOTA:
                req = self.get_url('/data-service/dota/team/basic_info', 'team_id={}'.format(ids_str))
                req_player = self.get_url('/data-service/dota/team/players', 'team_id={}'.format(ids_str))
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/team/basic_info', 'team_id={}'.format(ids_str))
                req_player = self.get_url('/data-service/csgo/team/players', 'team_id={}'.format(ids_str))
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/team/basic_info', 'team_id={}'.format(ids_str))
                req_player = self.get_url('/data-service/kog/team/players', 'team_id={}'.format(ids_str))
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/team/basic_info', 'team_id={}&version=2'.format(ids_str))
                req_player = self.get_url('/data-service/lol/team/players', 'team_id={}&version=2'.format(ids_str))
            else:
                return

            # 获取详情
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.default_parse)

            # 战队成员列表
            yield scrapy.Request(url=req_player['url'],
                                 method='GET',
                                 headers=req_player['header'],
                                 callback=self.default_parse)

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return
            self.page += 1

            if game == const.GAME_DOTA:
                req = self.get_url('/data-service/dota/team/list', self.get_page_str())
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/team/list', self.get_page_str())
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/team/list', self.get_page_str())
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/team/list', self.get_page_str(True))
            else:
                return
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse)
