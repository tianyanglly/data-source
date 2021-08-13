import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import ho.const as const

STATUS_ALL = 'all'  # 所有状态
STATUS_NOT = 'not'  # 未开赛和进行中
STATUS_SPECIAL = 'special'  # 删除/延迟


# scrapy crawl league -a game=dota -a status=all
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
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/league/list?{}'.format(self.get_page_str()))
            else:
                url = self.get_url('/lol/league/list?{}&version=2'.format(self.get_page_str()))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse_page)
        elif self.status == STATUS_NOT:
            # 此接口用于获取近期未开赛和进行中联赛列表 6小时/次
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/league/recently')
            else:
                url = self.get_url('/lol/league/recently?version=2')
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse)
        else:
            # 此接口用于获取联赛列表，返回状态是【已删除】【已延期】的联赛，数据按比赛日期倒序返回 15分钟/次
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/league/special')
            else:
                url = self.get_url('/lol/league/special')
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            for item in data:
                ids.append(str(item['league_id']))
                yield item

            # 获取详情
            ids_str = ','.join(ids)
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/league/basic_info?league_id={}'.format(ids_str))
                yield scrapy.Request(url=url,
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.parse_detail)
            else:
                url = self.get_url('/lol/league/basic_info?league_id={}&version=2'.format(ids_str))
                yield scrapy.Request(url=url,
                                     method='GET',
                                     headers=get_header(),
                                     callback=self.default_parse)

    def parse_page(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                yield item

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return

            self.page += 1
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/league/list?{}'.format(self.get_page_str()))
            else:
                url = self.get_url('/lol/league/list?{}&version=2'.format(self.get_page_str()))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

    def parse_detail(self, response):
        data = get_response_data(response)
        if data:
            for item in data:
                if len(item['sub_list']) > 0:
                    ids = []
                    for sub in item['sub_list']:
                        ids.append(str(sub['sub_id']))
                    # 子联赛详情
                    ids_str = ','.join(ids)
                    url = self.get_url('/dota/league/subLeague?sub_id={}'.format(ids_str))
                    yield scrapy.Request(url=url,
                                         method='GET',
                                         headers=get_header(),
                                         callback=self.parse_detail_sub)
                yield item

    def parse_detail_sub(self, response):
        data = get_response_data(response)
        if data:
            item = {}
            if type(data) == list:
                item['sub_list'] = data
                item['league_id'] = data[0]['league_id']
            else:
                item['sub_list'] = [data]
                item['league_id'] = data['league_id']
            yield item
