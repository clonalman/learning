from threading import Thread
from time import sleep

from redis import Redis
from rediscluster import RedisCluster
from redistimeseries.client import Client
from datetime import datetime, date, time
from pandas import DataFrame
from mootdx.quotes import Quotes
from mootdx import consts
import json
import sys
import os


def make_pid(name):
    if not os.path.exists(sys.path[0] + '/pids'):
        os.makedirs(sys.path[0] + '/pids')
    with open(sys.path[0] + '/pids/' + name + '.pid', 'w', encoding='utf-8') as f:
        f.write(str(os.getpid()))


def kill_pid(name):
    with open(sys.path[0] + '/pids/' + name + '.pid', encoding='utf-8') as f:
        os.kill(int(f.readline(16)), 9)

def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class MootdxRTS(object):
    @staticmethod
    def std(decode_responses=True):
        with open(sys.path[0] + '/redis-cluster.json', encoding="utf-8") as f:
            startup_nodes = json.load(f)
            print(startup_nodes)

            if len(startup_nodes) > 1:
                conn = RedisCluster(startup_nodes=startup_nodes, decode_responses=decode_responses)
            else:
                conn = Redis(host=startup_nodes[0]['host'], port=startup_nodes[0]['port'],
                             decode_responses=decode_responses)

            rtsCli = Client(conn=conn)
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

    __markets = {'0': 'SZ', '1': 'SH', '9': 'SF'}

    __prefix = 'SECU'

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

    def mktKey(self, code, mkt):
        return str(code) + "." + self.__markets.get(str(mkt))

    def replay(self, code, cur_dt: date):
        cur_key = self.__prefix + ':' + str(code) + ':' + cur_dt.strftime('%Y%m%d')
        from_time = datetime.combine(cur_dt, time(0, 0, 0))
        to_time = datetime.combine(cur_dt, time(23, 59, 59))
        rng = self.rtsCli.range(cur_key, int(from_time.timestamp() * 1000), int(to_time.timestamp() * 1000))
        # print(rng)
        if rng is not None:
            rows = [self.rtsCli.redis.hgetall(cur_key + ":" + tick) for ts, tick in rng]
            index = 0
            while index < len(rows):
                rs = rows[index:index + 80]
                print(rs)
                self.rtsCli.redis.publish("security", json.dumps(rs))
                sleep(0.5)
                index += 80

    #@async_call
    def save(self, cur_dt: date, df: DataFrame):
        retention_msecs = 604800000
        ktv_tuples = []
        dic_tuples = []
        for i, row in df.iterrows():
            dt = datetime.combine(cur_dt, datetime.strptime(row["servertime"], '%H:%M:%S.%f').time())
            ts = int(dt.timestamp() * 1000)
            code = self.mktKey(row['code'], row['market'])
            tick = row['active2']

            key = self.__prefix + ':' + code + ':' + cur_dt.strftime('%Y%m%d')

            dic = {'code': code, 'tick': tick}
            dic.update(row[self.__columns].rename(self.__renames).to_dict())
            dic.update({'timestamp': ts})

            labels = dict(code=row['code'], market=row['market'], date=cur_dt.strftime('%Y%m%d'))
            params = dict(labels=labels, retention_msecs=retention_msecs, duplicate_policy='last')
            ktv_tuples.append(([key, ts, tick], params))
            dic_tuples.append((key + ":" + str(tick), dic))

        if len(ktv_tuples) > 0 and len(dic_tuples) > 0:

            for ktv_tuple in ktv_tuples:
                ktv = ktv_tuple[0]
                params = ktv_tuple[1]
                self.rtsCli.add(ktv[0], ktv[1], ktv[2], **params)

            with self.rtsCli.redis as redis, self.rtsCli.redis.pipeline() as pipe:
                rows = []
                for dic_tuple in dic_tuples:
                    pipe.hset(dic_tuple[0], mapping=dic_tuple[1])
                    pipe.pexpire(dic_tuple[0], retention_msecs)
                    rows.append(dic_tuple[1])
                pipe.execute()
                # redis-py-cluster bug
                redis.publish("security", json.dumps(rows))
