import scrapy
from keep.spiders.base import BaseSpider, get_response_data, get_yesterday, get_time_to


# 未开始比赛列表
# 建议频率:1 小时/1 次
class MatchSpider(BaseSpider):
    name = 'match'
    page = 1

    def start_requests(self):
        yield scrapy.Request(
            url=self.get_url(
                '/v1/fixtures?sport=csgo&to={}&page={}'.format(get_time_to(), self.page)),
            method='GET',
            headers=self.get_header(),
            callback=self.default_parse)

    def default_parse(self, response):
        data = get_response_data(response)
        if data['fixtures']:
            for item in data['fixtures']:
                yield item

                # 获取详情
                yield scrapy.Request(
                    url=self.get_url('/v1/fixtures/{}'.format(item['id'])),
                    method='GET',
                    headers=self.get_header(),
                    callback=self.parse_detail)

            # 判断是否还有下一页
            if len(data['fixtures']) < self.get_limit():
                return

            self.page += 1
            yield scrapy.Request(
                url=self.get_url(
                    '/v1/fixtures?sport=csgo&from={}&to={}&page={}'.format(get_yesterday(), get_time_to(), self.page)),
                method='GET',
                headers=self.get_header(),
                callback=self.default_parse)
