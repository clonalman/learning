from rediscluster import RedisCluster
from redistimeseries.client import Client
from datetime import datetime, date
from pandas import DataFrame
from mootdx.quotes import Quotes
from mootdx import consts
import json


class MootdxRTS(object):
    @staticmethod
    def std():
        with open('redis-cluster.json') as f:
            nodes = json.load(f)
            print(nodes)
            redis_cli = RedisCluster(startup_nodes=nodes, decode_responses=True)
            rtsCli = Client(conn=redis_cli)
        # 标准市场
        tdxCli = Quotes.factory(market='std', multithread=True, heartbeat=True)
        return MootdxCli(tdxCli, rtsCli)


class MootdxCli(object):
    # 使用字段
    __columns = [
        'open', 'last_close', 'high', 'low', 'price', 'amount', 'volume', 's_vol', 'b_vol',
        'ask1', 'ask2', 'ask3', 'ask4', 'ask5', 'ask_vol1', 'ask_vol2', 'ask_vol3', 'ask_vol4', 'ask_vol5',
        'bid1', 'bid2', 'bid3', 'bid4', 'bid5', 'bid_vol1', 'bid_vol2', 'bid_vol3', 'bid_vol4', 'bid_vol5'
    ]
    # 字段更正映射
    __renames = {'last_close': 'close'}

    def __init__(self, tdxCli, rtsCli):
        self.tdxCli = tdxCli
        self.rtsCli = rtsCli

    def stocks(self, market):
        return self.tdxCli.stocks(market=market)


    def quotes(self, symbol):
        # 实时行情
        return self.tdxCli.quotes(symbol=symbol)

    def bars(self, symbol):
        # k 线数据
        self.tdxCli.bars(symbol=symbol, frequency=9, offset=10)

    def index(self, symbol, frequency=9):
        # 指数
        self.tdxCli.index(symbol=symbol, frequency=frequency)

    def minutes(self, symbol, date, **kwargs):
        # 历史分时
        self.tdxCli.minutes(symbol=symbol, date=date, **kwargs)

    def transaction(self, symbol, start=0, offset=10):
        # 当前分笔
        self.tdxCli.transaction(symbol=symbol, start=start, offset=offset)

    def transactions(self, symbol, date, start=0, offset=10):
        # 当前分笔
        self.tdxCli.transactions(symbol=symbol, date=date, start=start, offset=offset)



    def save(self, cur_dt: date, df: DataFrame):
        for i, row in df.iterrows():
            dt = datetime.combine(cur_dt, datetime.strptime(row["servertime"], '%H:%M:%S.%f').time())
            key = 'security:' + str(row['market']) + ':' + str(row['code']) + ':' + cur_dt.strftime('%Y%m%d')
            if not self.rtsCli.redis.exists(key):
                labels = {'market': row['market'], 'code': row['code'], 'date': cur_dt.strftime('%Y%m%d')}
                self.rtsCli.create(key, labels=labels, retention_msecs=432000000, duplicate_policy='last')
            tick = row['active1']

            row = row[self.__columns].rename(self.__renames)

            ts = int(dt.timestamp() * 1000)
            self.rtsCli.add(key, ts, tick)
            self.rtsCli.redis.hset(key + ":" + str(tick), 'ts', ts, row.to_dict())
            # self.rtsCli.redis.publish("security", key)
