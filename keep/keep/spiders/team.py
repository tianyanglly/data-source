from keep.spiders.base import BaseSpider
import scrapy
import pymongo
from keep.util import upload_dfs
import os


# 获取战队图片
# 建议频率:10 天/1 次
class GameSpider(BaseSpider):
    name = 'team'

    def start_requests(self):
        self.client = pymongo.MongoClient(self.settings.get('MONGODB_URI'))
        self.db = self.client[self.settings.get('MONGODB_DB', 'djData')]
        # 获取未开始的比赛
        for row in self.db[self.settings.get('COLLECTION_PREFIX') + 'team'].find():
            yield scrapy.Request(url=self.get_img_url(row['id']), method='GET', headers=self.get_img_header(),
                                 callback=self.parse_img)

    def get_img_header(self):
        return {'Authorization': 'Bearer ' + self.settings.get('APP_TOKEN')}

    def get_img_url(self, team_id):
        return self.settings.get('IMG_HOST') + '/logo/participant/{}'.format(team_id)

    def parse_img(self, response):
        text = str(response.body)
        if '<Error>' in text:
            return
        elif 'PNG' in text:
            ext = 'png'
        elif 'JPEG' in text:
            ext = 'jpg'
        elif '<svg' in text:
            ext = 'svg'
        else:
            return
        url = response.url
        i = url.rindex('/')
        filename = '{}.{}'.format(url[i + 1:], ext)
        with open('./{}'.format(filename), 'wb')as fp:
            fp.write(response.body)
        img_url = upload_dfs(filename)
        if img_url:
            os.remove('./{}'.format(filename))
            yield {'logo': img_url, 'id': int(url[i + 1:])}

    def close(self, reason):
        self.client.close()
