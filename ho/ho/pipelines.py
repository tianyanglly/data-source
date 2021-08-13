# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import redis
from itemadapter import ItemAdapter
from ho.util import get_collection_name


class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db, redis_host, redis_port, redis_auth):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_auth = redis_auth

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'djData'),
            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT'),
            redis_auth=crawler.settings.get('REDIS_AUTH'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        self.redis = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True,
                                 password=self.redis_auth)

    def close_spider(self, spider):
        self.client.close()
        self.redis.close()

    def process_item(self, item, spider):
        data = get_collection_name(spider.name, item)
        if spider.name == 'match_live':
            ids = [str(x) for x in item['battle_ids']]
            redis_key = '{}{}_{}'.format(spider.settings.get('COLLECTION_PREFIX'), spider.game, spider.name)
            self.redis.delete(redis_key)
            self.redis.hset(redis_key,
                            item['match_id'],
                            ','.join(ids))
        ret = self.db[
            '{}{}_{}'.format(spider.settings.get('COLLECTION_PREFIX'), spider.game, data['collection'])].update(
            data['spec'], {
                '$set': ItemAdapter(item).asdict()}, True)
        print(ret)
