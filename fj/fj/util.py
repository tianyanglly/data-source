from fj.items import League, Match, Team, Bet, Option
import fj.const as const
import requests


# 获取插入集合名和集合唯一限制条件
def get_collection_name(spider_name, item):
    if spider_name in ['league']:
        return {
            'collection': item['game'] + '_league',
            'spec': {'league_id': item['league_id']}
        }
    elif spider_name in ['match', 'match_live', 'match_video']:
        return {
            'collection': item['game'] + '_match',
            'spec': {'match_id': item['match_id']}
        }
    elif spider_name in ['match_now']:
        if 'map_name' in item.keys():
            return {
                'collection': item['game'] + '_match_map',
                'spec': {'map_name': item['map_name'], 'match_id': item['match_id']}
            }
        if 'battle_id' in item.keys():
            return {
                'collection': item['game'] + '_match_battle',
                'spec': {'battle_id': item['battle_id']}
            }
        else:
            return {
                'collection': item['game'] + '_bet',
                'spec': {'bet_id': item['bet_id']}
            }
    elif spider_name in ['team']:
        if 'player_id' in item.keys():
            return {
                'collection': item['game'] + '_player',
                'spec': {'player_id': item['player_id']}
            }
        else:
            return {
                'collection': item['game'] + '_team',
                'spec': {'team_id': item['team_id']}
            }
    elif spider_name == 'item':
        keys = item.keys()
        if 'item_id' in keys:
            return {
                'collection': item['game'] + '_item',
                'spec': {'item_id': item['item_id']}
            }
        elif 'skill_id' in keys:
            return {
                'collection': item['game'] + '_skill',
                'spec': {'skill_id': item['skill_id']}
            }
        elif 'rune_id' in keys:
            return {
                'collection': item['game'] + '_rune',
                'spec': {'rune_id': item['rune_id']}
            }
        elif 'hero_id' in keys:
            return {
                'collection': item['game'] + '_hero',
                'spec': {'hero_id': item['hero_id']}
            }
    elif spider_name == 'bet':
        if 'bet_id' in item.keys():
            return {
                'collection': item['game'] + '_bet',
                'spec': {'bet_id': item['bet_id']}
            }
        else:
            return {
                'collection': item['game'] + '_match',
                'spec': {'match_id': item['match_id']}
            }
    else:
        return None


# 数据源数据 -> 游戏元数据 联赛结构
def get_league_item(item):
    league = League()
    league['game_id'] = const.GAME_ID_LIST[item['game']]
    league['league_id'] = item['league_id']
    league['name'] = item['name']
    league['name_en'] = item['name_en'] if 'name_en' in item.keys() else ''
    league['short_name'] = item['short_name'] if 'short_name' in item.keys() else ''
    league['start_time'] = int(item['start_time'] / 1000)
    league['end_time'] = int(item['end_time'] / 1000)
    league['organizer'] = item['organizer'] if 'organizer' in item.keys() else ''
    league['logo'] = item['logo']
    league['address'] = item['location'] if item['game'] in [const.GAME_DOTA, const.GAME_CSGO] else item['address']
    league['status'] = item['status']
    return league


# 数据源数据 -> 游戏元数据 比赛结构
def get_match_item(item):
    match = Match()
    keys = item.keys()
    if 'team_a' not in keys or 'team_b' not in keys:
        return None
    match['game_id'] = const.GAME_ID_LIST[item['game']]
    match['league_id'] = item['league_id']
    match['league_name'] = item['league']['name'] if 'league' in keys else ''
    match['match_id'] = item['match_id']
    match['status'] = item['status']
    match['round_name'] = item['round_name'] if 'round_name' in keys else ''
    match['start_time'] = int(item['match_time'] / 1000) if item['game'] in [const.GAME_DOTA, const.GAME_CSGO] else int(
        item['start_time'] / 1000)
    match['bo'] = item['bo']
    match['battle_ids'] = item['battle_ids'] if 'battle_ids' in keys else []
    match['team_a_id'] = item['team_a_id']
    match['team_a_score'] = item['team_a_score']
    match['team_b_id'] = item['team_b_id']
    match['team_b_score'] = item['team_b_score']
    match['team_a_name'] = item['team_a']['name']
    match['team_a_logo'] = item['team_a']['logo']
    match['team_b_name'] = item['team_b']['name']
    match['team_b_logo'] = item['team_b']['logo']
    match['address'] = item['address'] if 'address' in keys else ''
    return match


# 数据源数据 -> 游戏元数据 战队结构
def get_team_item(item):
    team = Team()
    team['game_id'] = const.GAME_ID_LIST[item['game']]
    team['team_id'] = item['team_id']
    team['name_en'] = item['name_en'] if 'name_en' in item.keys() else ''
    team['name'] = item['name']
    team['short_name'] = item['short_name'] if 'short_name' in item.keys() else ''
    team['logo'] = item['logo']
    team['introduction'] = item['introduction'] if 'introduction' in item.keys() else ''
    return team


# 数据源数据 -> 游戏元数据 指数
def get_bet_item(item):
    bet = Bet()
    bet['game_id'] = const.GAME_ID_LIST[item['game']]
    bet['bet_id'] = item['bet_id']
    bet['match_id'] = item['match_id']
    bet['title'] = item['title']
    bet['end_time'] = item['end_time']
    bet['status'] = item['status']
    bet['source'] = item['source']
    bet['result_id'] = item['result_id']
    bet['options'] = get_bet_option_item(item['options'])
    bet['bet_type'] = item['bet_type']
    bet['board_num'] = item['board_num']
    return bet


# 投注项
def get_bet_option_item(items):
    options = []
    for item in items:
        option = Option()
        option['option_id'] = item['bet_item_id']
        option['odds'] = item['odds']
        option['team_id'] = item['team_id'] if 'team_id' in item.keys() else ''
        option['odds_name'] = item['name']
        option['odds_status'] = 0
        options.append(option)
    return options


def upload_dfs():
    url = 'http://34.96.253.12:22000/group1/upload'
    files = {'file': open('report.xls', 'rb')}
    options = {'output': 'json', 'path': '', 'scene': ''}  # 参阅浏览器上传的选项
    r = requests.post(url, data=options, files=files)
    print(r.text)
