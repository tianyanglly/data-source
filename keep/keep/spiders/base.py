import json
import scrapy
import datetime


def get_response_data(response):
    if response.status == 200:
        return json.loads(response.body)
    else:
        raise Exception('err:{}'.format(response.body))


# 昨日日期
def get_yesterday():
    today = datetime.date.today()
    diff = datetime.timedelta(days=1)
    yesterday = today - diff
    return yesterday


#  15天后时间
def get_time_to():
    today = datetime.date.today()
    diff = datetime.timedelta(days=15)
    yesterday = today + diff
    return yesterday


class BaseSpider(scrapy.Spider):
    allowed_domains = ['gamescorekeeper.com']
    start_urls = []

    def parse_detail(self, response):
        data = get_response_data(response)
        if data:
            yield data

    def get_header(self):
        return {'Authorization': 'Bearer ' + self.settings.get('APP_TOKEN'), 'Content-Type': 'application/json'}

    def get_url(self, path):
        return self.settings.get("API_HOST") + path

    def get_limit(self):
        return 50
