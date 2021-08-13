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


# 比赛指数
class Bet(scrapy.Item):
    bet_id = scrapy.Field()  # 竞猜ID
    game_id = scrapy.Field()  # 游戏id
    match_id = scrapy.Field()  # 比赛ID
    # 风险等级 A:极高， B:高: C:中 D:低 E:极低，用法说明:风险等级越 高，假赛的几率越大，
    # 盘口爆冷几率越高，需 要客户这边的限额越严 格，单笔的投注限定额度越小。
    risk_level = scrapy.Field()
    title = scrapy.Field()  # 标题
    end_time = scrapy.Field()  # 停止竞猜时间
    status = scrapy.Field()  # 状态
    source = scrapy.Field()  # 来源网站
    result_id = scrapy.Field()  # 竞猜结果
    options = scrapy.Field()  # 竞猜选项
    bet_type = scrapy.Field()  # 赔率类型
    board_num = scrapy.Field()  # 局数


class Option(scrapy.Item):
    option_id = scrapy.Field()  # 投注项id
    odds = scrapy.Field()  # 赔率
    odds_name = scrapy.Field()  # 投注项名
    odds_status = scrapy.Field()  # 建议投注状态 0关闭，1开放，3 暂停
