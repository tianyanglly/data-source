import scrapy
from fj.spiders.base import BaseSpider, get_response_data, cut
import fj.const as const

STATUS_ALL = 'all'  # 所有状态
STATUS_NOT = 'not'  # 未开赛和进行中
STATUS_SPECIAL = 'special'  # 删除/延迟


# scrapy crawl league -a status=all
# 此接口用于获取所有的联赛，包含未开赛，进行中，已结束，延迟，删除等所有状态的的联赛
# 限制说明
# 频率限制: 1次/每秒
# 建议更新频率：6小时/次
class LeagueSpider(BaseSpider):
    name = 'league'
    status = 'special'

    def __init__(self, game=None, status=0, **kwargs):
        super().__init__(game=game, **kwargs)
        self.status = status

    def start_requests(self):
        if self.status == STATUS_ALL:
            # 联赛列表（所有状态） 1天/次
            reqs = [self.get_url('/data-service/kog/league/list', self.get_page_str()),
                    self.get_url('/data-service/dota/league/list', self.get_page_str()),
                    self.get_url('/data-service/csgo/league/list', self.get_page_str()),
                    self.get_url('/data-service/lol/league/list', self.get_page_str(True))]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.parse_page)
        elif self.status == STATUS_NOT:
            # 此接口用于获取近期未开赛和进行中联赛列表 6小时/次

            reqs = [self.get_url('/data-service/dota/league/recently'),
                    self.get_url('/data-service/kog/league/recently'),
                    self.get_url('/data-service/csgo/league/recently'),
                    self.get_url('/data-service/lol/league/recently', 'version=2')]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.parse)
        else:
            # 此接口用于获取联赛列表，返回状态是【已删除】【已延期】的联赛，数据按比赛日期倒序返回 15分钟/次
            reqs = [self.get_url('/data-service/dota/league/special'),
                    self.get_url('/data-service/kog/league/special'),
                    self.get_url('/data-service/csgo/league/special'),
                    self.get_url('/data-service/lol/league/special')]
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.default_parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            game = self.get_game_name(response)
            for item in data:
                item['game'] = game
                ids.append(str(item['league_id']))
                yield item

            game = self.get_game_name(response)
            if len(ids) > self.get_limit():  # 是否需要分页获取
                ids_p = cut(ids, self.get_limit())
            else:
                ids_p = [ids]
            # 获取详情

            reqs = []
            if game == const.GAME_DOTA:
                for i in ids_p:
                    reqs.append(
                        self.get_url('/data-service/dota/league/basic_info', 'league_id={}'.format(','.join(i))))
            elif game == const.GAME_KOG:
                for i in ids_p:
                    reqs.append(self.get_url('/data-service/kog/league/basic_info', 'league_id={}'.format(','.join(i))))
            elif game == const.GAME_LOL:
                for i in ids_p:
                    reqs.append(self.get_url('/data-service/lol/league/basic_info',
                                             'league_id={}&version=2'.format(','.join(i))))
            elif game == const.GAME_CSGO:
                for i in ids_p:
                    reqs.append(
                        self.get_url('/data-service/csgo/league/basic_info', 'league_id={}'.format(','.join(i))))
            else:
                return
            for req in reqs:
                yield scrapy.Request(url=req['url'],
                                     method='GET',
                                     headers=req['header'],
                                     callback=self.default_parse)

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
                req = self.get_url('/data-service/dota/league/list', self.get_page_str())
            elif game == const.GAME_LOL:
                req = self.get_url('/data-service/lol/league/list', self.get_page_str(True))
            elif game == const.GAME_KOG:
                req = self.get_url('/data-service/kog/league/list', self.get_page_str())
            elif game == const.GAME_CSGO:
                req = self.get_url('/data-service/csgo/league/list', self.get_page_str())
            else:
                return
            yield scrapy.Request(url=req['url'],
                                 method='GET',
                                 headers=req['header'],
                                 callback=self.parse_page)

    # 子联赛暂时用不着，不用获取
    # def parse_detail(self, response):
    #     data = get_response_data(response)
    #     if data:
    #         for item in data:
    #             if len(item['sub_list']) > 0:
    #                 ids = []
    #                 for sub in item['sub_list']:
    #                     ids.append(str(sub['sub_id']))
    #                 # 子联赛详情
    #                 ids_str = ','.join(ids)
    #                 req = self.get_url('/data-service/dota/league/subLeague', 'sub_id={}'.format(ids_str))
    #                 yield scrapy.Request(url=req['url'],
    #                                      method='GET',
    #                                      headers=req['header'],
    #                                      callback=self.parse_detail_sub)
    #             yield item
    #
    # def parse_detail_sub(self, response):
    #     data = get_response_data(response)
    #     if data:
    #         item = {}
    #         if type(data) == list:
    #             item['sub_list'] = data
    #             item['league_id'] = data[0]['league_id']
    #         else:
    #             item['sub_list'] = [data]
    #             item['league_id'] = data['league_id']
    #         yield item
