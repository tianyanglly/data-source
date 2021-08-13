# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import pymysql
from itemadapter import ItemAdapter
from keep.util import *


# 数据源数据存储
class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'djData')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = get_collection_name(spider, item)
        prefix = spider.settings.get('COLLECTION_PREFIX')
        ret = self.db[prefix + data['collection']].update(
            data['spec'], {'$set': ItemAdapter(item).asdict()}, True)

        if ret['updatedExisting'] and ret['nModified'] == 0:  # 数据存在，且数据没有变化
            return None

        if data['collection'] == 'match':
            # 保存战队信息
            for team in item['participants']:
                if team['id'] is None:
                    continue
                self.db[prefix + 'team'].update(
                    {'id': team['id']}, {'$set': team}, True)
            # return get_match_item(item)
        return None


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
        if 'bet_id' in item.keys():
            collection = 'bet'
            spec = {'bet_id': item['bet_id'], 'match_id': item['match_id']}
        elif 'match_id' in item.keys():
            collection = 'match'
            spec = {'match_id': item['match_id']}
        else:
            return
        prefix = spider.settings.get('COLLECTION_PREFIX')
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
