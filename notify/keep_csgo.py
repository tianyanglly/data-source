import websocket
import ssl
import _thread as thread
import json
from multiprocessing import Process, log_to_stderr
import logging
import pymongo
import time
import redis
import requests
import os

# 线上
if os.getenv('FLASK_ENV') == 'production':
    CONFIG = {
        'redis_host': '127.0.0.1',
        'scrapyd_url': 'http://127.0.0.1:6800/schedule.json',
        'mongo_uri': 'mongodb://djOnline:xxwc4hlhcr7b1reu58@127.0.0.1:27017/djData?authMechanism=SCRAM-SHA-256'
    }
else:
    CONFIG = {
        'redis_host': '192.168.8.76',
        'scrapyd_url': 'http://192.168.8.76:6800/schedule.json',
        'mongo_uri': 'mongodb://dj:123456@192.168.8.76:27017/djData?authMechanism=SCRAM-SHA-256'
    }


def get_redis():
    r = redis.Redis(host=CONFIG['redis_host'], port=6379,
                    decode_responses=True,
                    max_connections=5,
                    password=None)
    return r


def push_scrapyd():
    params = {'project': 'keep', 'spider': 'live',
              'jobid': 'keep_csgo_{}'.format(time.strftime("%Y%m%d%H%M%S", time.localtime()))}

    requests.post(CONFIG['scrapyd_url'], data=params, timeout=2)


def on_message(ws, message):
    try:
        msg = json.loads(message)
        print(msg)
        if msg['type'] == 'auth':
            ws.send(
                b'{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYW5qaW5nIiwiaXNzIjoiR2FtZVNjb3Jla2VlcGVyIiwianRpIjoxNTIyNzUwOTg2MjAzMTE0MDEsImN1c3RvbWVyIjp0cnVlfQ.pQTeRnEAdNQgCULKewxZxTmGhrgLA42qneuF028Igwc"}')
        elif msg['type'] == 'pong':
            pass
        else:
            r = get_redis()
            r.rpush('keep_csgo_live', message)
    except Exception as e:
        print('message error:'.format(e.args))


def on_error(ws, error):
    print('websocket error:{}'.format(error))


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def ping(*args):
        while True:
            time.sleep(30)
            ws.send('ping')

    thread.start_new_thread(ping, ())


# 获取url后的赛事id
def get_match_id(url):
    i = url.rindex('/')
    return int(url[i + 1:])


def on_start(match_id):
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.gamescorekeeper.com/v1/liveapi/{}".format(match_id),
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def get_match_list():
    client = pymongo.MongoClient(CONFIG['mongo_uri'])
    db = client['djData']
    # 获取未开始的比赛
    timestamp = int((round(time.time() + 3600) * 1000))
    query = {'$or': [
        {'$and': [{'scheduledStartTime': {'$lt': timestamp}}, {'status': 'Scheduled'}]},
        {'status': 'Started'}
    ]}
    ids = []
    for row in db['keep_match'].find(query, {'_id': 0, 'id': 1}):
        ids.append(row['id'])
    client.close()
    return ids


pool = {}
if __name__ == "__main__":
    logger = log_to_stderr()
    logger.setLevel(logging.WARN)
    for match_id in get_match_list():
        p = Process(target=on_start, args=(match_id,))
        pool[match_id] = p
        p.start()

    while True:
        time.sleep(60)

        new_match_list = get_match_list()
        print(pool)
        print(new_match_list)
        # 清除结束的比赛
        del_id = []
        for match_id in pool:
            if match_id not in new_match_list:
                pool[match_id].terminate()
                del_id.append(match_id)
        for i in del_id:
            del pool[i]
        for match_id in new_match_list:
            # 新比赛
            if match_id not in pool.keys():
                p = Process(target=on_start, args=(match_id,))
                pool[match_id] = p
                p.start()
            else:
                if not pool[match_id].is_alive():
                    p = Process(target=on_start, args=(match_id,))
                    pool[match_id] = p
                    p.start()
