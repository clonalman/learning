from collections import defaultdict
from functools import reduce
from typing import Mapping

from rediscluster import RedisCluster
from redistimeseries.client import Client
from datetime import datetime
import mootdx_std as tdx
import pandas as pd

# nodes = [
#     {'host': '172.27.175.4', 'port': 7001},
#     {'host': '172.27.175.4', 'port': 7002},
#     {'host': '172.27.175.4', 'port': 7003},
#     {'host': '172.27.175.4', 'port': 7004},
#     {'host': '172.27.175.4', 'port': 7005},
#     {'host': '172.27.175.4', 'port': 7006},
# ]

nodes = [
    {'host': '192.168.1.12', 'port': 7001},
    {'host': '192.168.1.12', 'port': 7002},
    {'host': '192.168.1.12', 'port': 7003},
    {'host': '192.168.1.12', 'port': 7004},
    {'host': '192.168.1.12', 'port': 7005},
    {'host': '192.168.1.12', 'port': 7006}
]

conn = RedisCluster(startup_nodes=nodes, decode_responses=True)
print(conn)

rts = Client(conn=conn)

qdf = tdx.quotes(['300033', '600745', '000635'])
# print(qdf)

columns = [
    'open', 'last_close', 'high', 'low', 'price', 'amount', 'volume', 's_vol', 'b_vol',
    'ask1', 'ask2', 'ask3', 'ask4', 'ask5', 'ask_vol1', 'ask_vol2', 'ask_vol3', 'ask_vol4', 'ask_vol5',
    'bid1', 'bid2', 'bid3', 'bid4', 'bid5', 'bid_vol1', 'bid_vol2', 'bid_vol3', 'bid_vol4', 'bid_vol5'
]

for index, row in qdf.iterrows():
    dt = datetime.combine(datetime.now().date(), datetime.strptime(row["servertime"], '%H:%M:%S.%f').time())
    cur_date = dt.date().strftime('%Y%m%d')
    key = 'security:' + str(row['market']) + ':' + str(row['code']) + ':' + cur_date

    if not rts.redis.exists(key):
        rts.create(key, labels={'market': row['market'], 'code': row['code'], 'date': cur_date},
                   retention_msecs=432000000, duplicate_policy='last')
    tick = row['active1']
    data = row[columns].rename({'last_close': 'close'})

    ts = int(dt.timestamp() * 1000)
    rts.add(key, ts, tick)
    rts.redis.hset(key + ":" + str(tick), 'ts', ts, data.to_dict())

key = 'security:0:000635:20220617'
s_dt = datetime(2022, 6, 17)
e_dt = datetime(2022, 6, 18)
print('=========================================')
print(key + "\t" + str(s_dt) + "\t" + str(e_dt))
print('-----------------------------------------')

rng = rts.range(key, int(s_dt.timestamp() * 1000), int(e_dt.timestamp() * 1000))
print(rng)
print('-----------------------------------------')
rdf = pd.DataFrame([rts.redis.hgetall(key + ":" + str(int(tick))) for ts, tick in rng])
print(rdf)

