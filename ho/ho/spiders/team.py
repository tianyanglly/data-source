import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import ho.const as const

# 接口描述
# 此接口用于获取所有的战队的列表
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：1月/次
class TeamSpider(BaseSpider):
    name = 'team'

    def start_requests(self):
        if self.game == const.GAME_DOTA:
            url = self.get_url('/dota/team/list?{}'.format(self.get_page_str()))
        else:
            url = self.get_url('/lol/team/list?{}&version=2'.format(self.get_page_str()))
        yield scrapy.Request(url=url,
                             method='GET',
                             headers=get_header(),
                             callback=self.parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            for item in data:
                ids.append(str(item['team_id']))
                yield item

            # 获取详情
            ids_str = ','.join(ids)
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/team/basic_info?team_id={}'.format(ids_str))
            else:
                url = self.get_url('/lol/team/basic_info?team_id={}&version=2'.format(ids_str))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

            # 战队成员列表
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/team/players?team_id={}&version=2'.format(ids_str))
            else:
                url = self.get_url('/lol/team/players?team_id={}&version=2'.format(ids_str))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse_player)

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return
            self.page += 1
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/team/list?{}'.format(self.get_page_str()))
            else:
                url = self.get_url('/lol/team/list?{}&version=2'.format(self.get_page_str()))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse)


    def parse_player(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            for item in data:
                ids.append(str(item['player_id']))
                yield item

            # 战队选手详情
            ids_str = ','.join(ids)
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/player/basic_info?player_id={}&version=2'.format(ids_str))
            else:
                url = self.get_url('/lol/player/basic_info?player_id={}&version=2'.format(ids_str))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)
