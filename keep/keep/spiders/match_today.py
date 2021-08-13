import scrapy
from keep.spiders.base import BaseSpider, get_response_data


# 当日比赛
# 建议频率:5 分钟/1 次
class MatchSpider(BaseSpider):
    name = 'match_today'
    page = 1

    def start_requests(self):
        yield scrapy.Request(
            url=self.get_url(
                '/v1/fixtures?sport=csgo&page={}'.format(self.page)),
            method='GET',
            headers=self.get_header(),
            callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data['fixtures']:
            for item in data['fixtures']:
                yield item

            # 判断是否还有下一页
            if len(data['fixtures']) < self.get_limit():
                return

            self.page += 1
            yield scrapy.Request(
                url=self.get_url(
                    '/v1/fixtures?sport=csgo&page={}'.format(self.page)),
                method='GET',
                headers=self.get_header(),
                callback=self.default_parse)
