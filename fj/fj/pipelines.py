# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import redis
import pymysql
from itemadapter import ItemAdapter
from fj.util import *


# 数据源数据存储
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

        if spider.name == 'match_live':
            self.redis = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True,
                                     password=self.redis_auth)

    def close_spider(self, spider):
        self.client.close()
        if spider.name == 'match_live':
            self.redis.close()

    def process_item(self, item, spider):
        data = get_collection_name(spider.name, item)
        if spider.name == 'match_live':
            redis_key = '{}{}_{}'.format(spider.settings.get('COLLECTION_PREFIX'), item['game'], spider.name)
            self.redis.delete(redis_key)
            if 'map_names' in item.keys():
                # csgo 进行中比赛
                if item['map_names']:
                    self.redis.hset(redis_key, item['match_id'], ','.join(item['map_names']))
            elif 'battle_ids' in item.keys():
                if item['battle_ids']:
                    ids = [str(x) for x in item['battle_ids']]
                    self.redis.hset(redis_key, item['match_id'], ','.join(ids))

        ret = self.db[spider.settings.get('COLLECTION_PREFIX') + data['collection']].update(
            data['spec'], {'$set': ItemAdapter(item).asdict()}, True)

        # if ret['updatedExisting'] and ret['nModified'] == 0:  # 数据存在，且数据没有变化
        # return None

        if 'team' in data['collection']:
            return get_team_item(item)
        elif 'league' in data['collection']:
            return get_league_item(item)
        elif 'match' in data['collection']:
            return get_match_item(item)
        elif 'bet' in data['collection']:
            return get_bet_item(item)
        return None


# 数据不存在
# {'n': 1, 'nModified': 0, 'upserted': ObjectId('5f9958f6413227432459b376'), 'ok': 1.0, 'updatedExisting': False}
# 数据存在 未更新
# {'n': 1, 'nModified': 0, 'ok': 1.0, 'updatedExisting': True}


# 数据源 -> 游戏元数据
class MapPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB_STABLE', 'djDataStable'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if item is None:
            return
        keys = item.keys()
        prefix = 'game_'
        if 'bet_id' in keys:
            collection = 'bet'
            spec = {'bet_id': item['bet_id'], 'game_id': item['game_id']}
        elif 'match_id' in keys:
            collection = 'match'
            spec = {'match_id': item['match_id'], 'game_id': item['game_id']}
        elif 'league_id' in keys:
            collection = 'league'
            spec = {'league_id': item['league_id'], 'game_id': item['game_id']}
        elif 'team_id' in keys:
            collection = 'team'
            spec = {'team_id': item['team_id'], 'game_id': item['game_id']}
        else:
            return
        ret = self.db[prefix + collection].update(
            spec, {'$set': ItemAdapter(item).asdict()}, True)
        print(ret)


# 游戏元数据 -> 真实数据
class MySQLPipeline(object):

    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_pwd):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_pwd = mysql_pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_pwd=crawler.settings.get('MYSQL_PWD'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
        )

    def open_spider(self, spider):
        # 连接数据库
        self.connect = pymysql.connect(
            host=self.mysql_host,  # 数据库地址
            port=self.mysql_port,  # 数据库端口
            db=self.mysql_db,  # 数据库名
            user=self.mysql_user,  # 数据库用户名
            passwd=self.mysql_pwd,  # 数据库密码
            charset='utf8',  # 编码方式
            use_unicode=True)
        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

    def process_item(self, item, spider):
        self.cursor.execute(
            """insert into mingyan(tag, cont)
            value (%s, %s)""",  # 纯属python操作mysql知识，不熟悉请恶补
            (item['tag'],  # item里面定义的字段和表字段对应
             item['cont'],))
        # 提交sql语句
        self.connect.commit()
        return item  # 必须实现返回
