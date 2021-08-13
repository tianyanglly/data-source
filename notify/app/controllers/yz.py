from flask import Blueprint, current_app, request
import json
import requests
import time
import hashlib
from urllib.parse import urlencode
from app.utils.core import mongo

yezhi = Blueprint("yz", __name__, url_prefix='/yz')

COLLECTION_PREFIX = 'yz_'

APP_KEY = '4CKrQmvj'
APP_SECRET = 'GKLRulI3rL7bfjucv8Y7cjxTLG8Ez5M4'
API_HOST = 'http://34.96.253.12:36001/?'


@yezhi.route('/callback', methods=['GET', 'POST'])
def yz():
    try:
        keys = request.headers.keys()
        if 'Xxe-Request' not in keys or 'Xxe-Sign' not in keys:
            return 'success'
        params = 'app_secret={}&'.format(APP_SECRET) + request.headers['Xxe-Request']
        m = hashlib.md5()
        m.update(params.encode('utf-8'))
        # 验证签名
        if m.hexdigest() != request.headers['Xxe-Sign']:
            current_app.logger.warning('sign err to data:{}'.format(request.data))
            return 'success'

        data = json.loads(request.data)
        params = {'project': 'yz', 'spider': 'info',
                  'jobid': 'yz_{}_{}'.format(data['func'], format_time(data['update_time'])),
                  'game_id': data['game_id'], 'event_id': data['event_id'], 'func': data['func']}

        requests.post(current_app.config['SCRAPYD_URL'], data=params, timeout=2)
        return 'success'
    except Exception as e:
        current_app.logger.error('yz exception:{}:data:{}'.format(e, request.data))
        return 'success'


def format_time(timestamp):
    time_local = time.localtime(timestamp)
    return time.strftime("%m-%d-%H-%M-%S", time_local)


# 保存至mongo
def save_mongo(item, func):
    ret = mongo.db[COLLECTION_PREFIX + get_collection_name(func)].update_one(
        {'game_id': item['game_id']}, {'$set': item}, True)
    if ret.raw_result['updatedExisting'] and ret.raw_result['nModified'] == 0:  # 数据存在，且数据没有变化
        return None
    print('next')


# 获取url
def get_url(resource, func, event_id=None, pri_id=None, game_id=None):
    params = {
        'app_key': APP_KEY,
        'app_secret': APP_SECRET,
        'func': func,
        'resource': resource,
        'timestamp': int(round(time.time() * 1000)),
    }
    if pri_id is not None:
        params['id'] = pri_id
    if event_id is not None:
        params['event_id'] = event_id
    if game_id is not None:
        params['game_id'] = game_id
    p = sorted(params.items(), key=lambda x: x[0])
    new_params = {}
    for i in p:
        new_params[i[0]] = i[1]
    path = urlencode(new_params)
    m = hashlib.md5()
    m.update(path.encode('utf-8'))
    sign = m.hexdigest()
    url = API_HOST + path + "&sign=" + sign
    return url


# 获取插入集合名
def get_collection_name(func):
    if func == 'bet_info':
        return 'bet'
    elif func == 'game_info':
        return 'match'
    elif func == 'roll_bet_info':
        return 'bet_roll'
    else:
        return None
