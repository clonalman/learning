import sys

from redis import Redis
from rediscluster import RedisCluster
from redistimeseries.client import Client
from datetime import datetime, date
from pandas import DataFrame
from mootdx.quotes import Quotes
from mootdx import consts
import json
import os


def make_pid(name):
    if not os.path.exists(sys.path[0] + '/pids'):
        os.makedirs(sys.path[0] + '/pids')
    with open(sys.path[0] + '/pids/' + name + '.pid', 'w', encoding='utf-8') as f:
        f.write(str(os.getpid()))


def kill_pid(name):
    with open(sys.path[0] + '/pids/' + name + '.pid', encoding='utf-8') as f:
        os.kill(int(f.readline(16)), 9)


class MootdxRTS(object):
    @staticmethod
    def std():
        with open(sys.path[0] + '/redis-cluster.json') as f:
            nodes = json.load(f)
            print(nodes)
            redisCli = RedisCluster(startup_nodes=nodes, decode_responses=True)
            # redisCli = Redis(host=nodes[0]['host'], port=nodes[0]['port'], decode_responses=True)
            rtsCli = Client(conn=redisCli.pipeline())
        # 标准市场
        tdxCli = Quotes.factory(market='std', multithread=True, heartbeat=True)
        return MootdxCli(tdxCli, rtsCli, redisCli)


class MootdxCli(object):
    # 使用字段
    __columns = [
        'code', 'open', 'last_close', 'high', 'low', 'price', 'amount', 'volume', 's_vol', 'b_vol',
        'ask1', 'ask2', 'ask3', 'ask4', 'ask5', 'ask_vol1', 'ask_vol2', 'ask_vol3', 'ask_vol4', 'ask_vol5',
        'bid1', 'bid2', 'bid3', 'bid4', 'bid5', 'bid_vol1', 'bid_vol2', 'bid_vol3', 'bid_vol4', 'bid_vol5'
    ]
    # 字段更正映射
    __renames = {'last_close': 'close'}

    def __init__(self, tdxCli, rtsCli, redisCli):
        self.tdxCli = tdxCli
        self.rtsCli = rtsCli
        self.redisCli = redisCli

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
        retention_msecs = 604800000
        rows = []
        for i, row in df.iterrows():
            dt = datetime.combine(cur_dt, datetime.strptime(row["servertime"], '%H:%M:%S.%f').time())
            key = 'SECU:' + str(row['market']) + ':' + str(row['code']) + ':' + cur_dt.strftime('%Y%m%d')
            labels = {'market': row['market'], 'code': row['code'], 'date': cur_dt.strftime('%Y%m%d')}

            # if not self.redisCli.exists(key):
            #     labels = {'market': row['market'], 'code': row['code'], 'date': cur_dt.strftime('%Y%m%d')}
            #     self.rtsCli.create(key, labels=labels, retention_msecs=retention_msecs, duplicate_policy='last')

            tick = row['active1']
            row = row[self.__columns].rename(self.__renames)

            ts = int(dt.timestamp() * 1000)
            key_tick = key + ":" + str(tick)

            dic = {'ts': ts }
            dic.update(row.to_dict())

            self.rtsCli.add(key, ts, tick, labels=labels, retention_msecs=retention_msecs, duplicate_policy='last')
            self.rtsCli.redis.hset(key_tick, mapping=dic)
            self.rtsCli.redis.pexpire(key_tick, retention_msecs)
            rows.append(dic)

        self.rtsCli.redis.execute()
        self.redisCli.publish("security", json.dumps(rows))
