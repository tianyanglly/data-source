# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# 比赛数据结构
class Match(scrapy.Item):
    game_id = scrapy.Field()  # 游戏id
    match_id = scrapy.Field()  # 比赛id
    league_id = scrapy.Field()  # 联赛id
    league_name = scrapy.Field()  # 联赛名
    status = scrapy.Field()  # 比赛状态
    start_time = scrapy.Field()  # 开始时间
    address = scrapy.Field()  # 举办地
    round_name = scrapy.Field()  # 轮次比赛
    bo = scrapy.Field()  # 赛制
    battle_ids = scrapy.Field()  # 对局id
    team_a_score = scrapy.Field()  # 主队得分
    team_a_id = scrapy.Field()  # 主队id
    team_a_name = scrapy.Field()  # 主队名
    team_a_logo = scrapy.Field()  # 主队logo
    team_b_score = scrapy.Field()  # 客队得分
    team_b_id = scrapy.Field()  # 客队id
    team_b_name = scrapy.Field()  # 客队名
    team_b_logo = scrapy.Field()  # 客队logo


# 比赛辅助数据源结构
class MatchToMaster(scrapy.Item):
    match_id = scrapy.Field()
    league_id = scrapy.Field()
    status = scrapy.Field()
    team_a_score = scrapy.Field()
    team_b_id = scrapy.Field()
