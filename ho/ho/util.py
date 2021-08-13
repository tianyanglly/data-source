def get_collection_name(spider_name, item):
    if spider_name in ['league']:
        return {
            'collection': 'league',
            'spec': {'league_id': item['league_id']}
        }
    elif spider_name in ['match', 'match_live', 'match_video']:
        return {
            'collection': 'match',
            'spec': {'match_id': item['match_id']}
        }
    elif spider_name in ['match_now']:
        if 'battle_id' in item.keys():
            return {
                'collection': 'match_battle',
                'spec': {'battle_id': item['battle_id']}
            }
        else:
            return {
                'collection': 'bet',
                'spec': {'bet_id': item['bet_id']}
            }
    elif spider_name in ['team']:
        if 'player_id' in item.keys():
            return {
                'collection': 'player',
                'spec': {'player_id': item['player_id']}
            }
        else:
            return {
                'collection': 'team',
                'spec': {'team_id': item['team_id']}
            }
    elif spider_name == 'hero':
        return {
            'collection': 'hero',
            'spec': {'hero_id': item['hero_id']}
        }
    elif spider_name == 'item':
        return {
            'collection': 'item',
            'spec': {'item_id': item['item_id']}
        }
    elif spider_name == 'skill':
        return {
            'collection': 'skill',
            'spec': {'skill_id': item['skill_id']}
        }
    elif spider_name == 'rune':
        return {
            'collection': 'rune',
            'spec': {'rune_id': item['rune_id']}
        }
    elif spider_name == 'bet':
        if 'bet_id' in item.keys():
            return {
                'collection': 'bet',
                'spec': {'bet_id': item['bet_id']}
            }
        else:
            return {
                'collection': 'match',
                'spec': {'match_id': item['match_id']}
            }
    else:
        return None
