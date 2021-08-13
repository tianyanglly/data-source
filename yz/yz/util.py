from yz.items import Match, Bet, Option
import yz.const as const
import time


# 获取插入集合名和集合唯一限制条件
def get_collection_name(spider, item):
    if spider.name == 'game':
        return {
            'collection': 'game',
            'spec': {'event_id': item['event_id']}
        }
    elif spider.name == 'news':
        return {
            'collection': 'news',
            'spec': {'news_id': item['news_id']}
        }
    elif spider.name == 'post':
        return {
            'collection': 'post',
            'spec': {'game_ids': item['game_ids']}
        }
    elif spider.name == 'league':
        if 'special_id' in item.keys():
            return {
                'collection': 'league_detail',
                'spec': {'special_id': item['special_id']}
            }
        else:
            return {
                'collection': 'league',
                'spec': {'match_id': item['match_id']}
            }
    elif spider.name == 'match':
        if 'data_type' in item.keys():
            return {
                'collection': 'match_detail',
                'spec': {'game_id': item['game_id']}
            }
        elif 'bet_id' in item.keys():
            return {
                'collection': 'bet',
                'spec': {'bet_id': item['bet_id'], 'game_id': item['game_id']}
            }
        else:
            return {
                'collection': 'match',
                'spec': {'game_id': item['game_id']}
            }
    elif spider.name == 'info':
        if spider.func == 'game_info':
            return {
                'collection': 'match_detail',
                'spec': {'game_id': item['game_id']}
            }
        elif spider.func in ['bet_info', 'roll_bet_info']:
            return {
                'collection': 'bet',
                'spec': {'bet_id': item['bet_id'], 'game_id': item['game_id']}
            }
    elif spider.name == 'video':
        return {
            'collection': 'video',
            'spec': {'game_id': item['game_id']}
        }
    else:
        return None


# 数据源数据 -> 游戏元数据 比赛结构
def get_match_item(item):
    if item['event_id'] not in const.GAME_ID_LIST:
        return None
    match = Match()
    match['game_id'] = const.GAME_ID_LIST[item['event_id']]
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


# 数据源数据 -> 游戏元数据 指数
def get_bet_item(item):
    bet = Bet()
    bet['bet_id'] = item['bet_id']
    bet['game_id'] = item['event_id']
    bet['match_id'] = item['game_id']
    bet['title'] = item['bet_title']
    bet['end_time'] = 0
    bet['risk_level'] = item['risk_level'] if 'risk_level' in item.keys() else ''
    bet['status'] = 0
    bet['source'] = 'yz'
    bet['result_id'] = 0
    bet['options'] = get_bet_option_item(item['items'])
    bet['bet_type'] = 0
    bet['board_num'] = item['num']
    return bet


# 投注项
def get_bet_option_item(items):
    options = []
    for item in items:
        option = Option()
        option['option_id'] = item['bet_num']
        option['odds'] = item['odds']
        option['odds_name'] = item['odds_name']
        option['odds_status'] = item['odds_status']
        options.append(option)
    return options


def format_timestamp(date):
    # 转换成时间数组
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    return time.mktime(timeArray)
