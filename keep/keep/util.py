from keep.items import Match
import time
import requests


# 获取插入集合名和集合唯一限制条件
def get_collection_name(spider, item):
    if spider.name == 'game':
        return {
            'collection': 'game',
            'spec': {'alias': item['alias']}
        }
    elif spider.name == 'league':
        return {
            'collection': 'league',
            'spec': {'id': item['id']}
        }
    elif spider.name == 'team':
        return {
            'collection': 'team',
            'spec': {'id': item['id']}
        }
    elif spider.name == 'live':
        return {
            'collection': 'match_live',
            'spec': {'sortIndex': item['sortIndex'], 'type': item['type'], 'fixtureId': item['fixtureId']}
        }
    elif spider.name in ['match', 'match_today']:
        return {
            'collection': 'match',
            'spec': {'id': item['id']}
        }
    else:
        return None


# 数据源数据 -> 游戏元数据 比赛结构
def get_csgo_match_item(item):
    match = Match()
    match['game_id'] = 4
    match['league_id'] = item['match_id']
    match['match_id'] = item['game_id']
    match['league_name'] = item['match_name']
    match['round_name'] = item['match_stage']
    match['start_time'] = format_timestamp(item['begin_time'])
    match['bo'] = item['bo']
    match['status'] = item['game_status']
    match['battle_ids'] = []
    if 'team_a_info' in item.keys():
        match['team_a_id'] = item['team_a_info']['team_id']
        match['team_a_name'] = item['team_a_info']['name']
        match['team_a_logo'] = item['team_a_info']['icon']
        match['team_b_id'] = item['team_b_info']['team_id']
        match['team_b_name'] = item['team_b_info']['name']
        match['team_b_logo'] = item['team_b_info']['icon']
    else:
        match['team_a_id'] = item['team_a']['team_id']
        match['team_a_name'] = item['team_a']['name']
        match['team_a_logo'] = item['team_a']['icon']
        match['team_b_id'] = item['team_b']['team_id']
        match['team_b_name'] = item['team_b']['name']
        match['team_b_logo'] = item['team_b']['icon']
    match['team_a_score'] = item['score_a']
    match['team_b_score'] = item['score_b']
    match['address'] = ''
    return match


def format_timestamp(date):
    # 转换成时间数组
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    return time.mktime(timeArray)


def upload_dfs(filename):
    url = 'https://img.catdog88.com/group1/upload'
    files = {'file': open('./{}'.format(filename), 'rb')}
    options = {'path': 'keep/csgo', 'output': 'json', filename: filename}  # 参阅浏览器上传的选项
    r = requests.post(url, data=options, files=files)
    res = r.json()
    if 'url' in res.keys():
        return res['url']
    else:
        return ''
