import scrapy
from ho.spiders.base import BaseSpider, get_response_data, get_header
import ho.const as const

STATUS_HISTORY = 'all'  # 已结束历史数据
STATUS_SPECIAL = 'del'  # 删除/延迟
STATUS_TODAY = 'today'  # 当日结束

# scrapy crawl match -a game=dota -a status=all
# 比赛列表
# 频率限制: 1次/每秒
# 建议更新频率：15分钟/次
class MatchSpider(BaseSpider):
    name = 'match'
    status = 'today'
    day = '1'

    def __init__(self, game=None, status='today', day='1', **kwargs):
        super().__init__(game=game, **kwargs)
        self.status = status
        self.day = day

    def start_requests(self):
        # 5分钟/次 此接口用于获取状态为【已结束】的比赛及相关信息（时间倒序），可以用作历史数据库，获取历史数据
        if self.status == STATUS_HISTORY:
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/final_score?{}&day={}'.format(self.get_page_str(), self.day))
            else:
                url = self.get_url('/lol/match/final_score?{}&day={}&version=2'.format(self.get_page_str(), self.day))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse)
        elif self.status == STATUS_SPECIAL:
            # 15分钟/次 删除/延迟
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/special?day=7')
            else:
                url = self.get_url('/lol/match/special?day=7')
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)
        else:
            # 1分钟/次 用于获取前一日19点至今天24点，比赛状态为【已结束】的比赛列表
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/today/end')
            else:
                url = self.get_url('/lol/match/today/end')
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

    def parse(self, response):
        data = get_response_data(response)
        if data:
            ids = []
            for item in data:
                ids.append(str(item['match_id']))
                yield item

            # 获取详情
            ids_str = ','.join(ids)
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/basic_info?match_id={}'.format(ids_str))
            else:
                url = self.get_url('/lol/match/basic_info?match_id={}&version=2'.format(ids_str))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.default_parse)

            # 判断是否还有下一页
            if len(data) < self.get_limit():
                return
            self.page += 1
            if self.game == const.GAME_DOTA:
                url = self.get_url('/dota/match/final_score?{}&day={}'.format(self.get_page_str(), self.day))
            else:
                url = self.get_url('/lol/match/final_score?{}&day={}&version=2'.format(self.get_page_str(), self.day))
            yield scrapy.Request(url=url,
                                 method='GET',
                                 headers=get_header(),
                                 callback=self.parse)
