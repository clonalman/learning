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

# Connected to pydev debugger (build 212.5457.46)
# RedisCluster<
# 192.168.1.12:7001, 192.168.1.12:7002, 192.168.1.12:7003, 192.168.1.12:7004, 192.168.1.12:7005, 192.168.1.12:7006
# >

# =========================================
# security:0:000635:20220617	2022-06-17 00:00:00	2022-06-18 00:00:00
# -----------------------------------------
# [(1655443994184, 1477.0), (1655444006790, 1480.0), (1655444214402, 1506.0),
#  (1655444232408, 1513.0), (1655444534190, 1551.0), (1655444643396, 1562.0),
#  (1655444768796, 1577.0), (1655444894208, 1594.0), (1655445199602, 1633.0),
#  (1655445252366, 1647.0), (1655445268512, 1656.0), (1655445363330, 1680.0)]
# -----------------------------------------
# ts  open close  high  ... bid_vol2 bid_vol3 bid_vol4 bid_vol5
# 0   1655443994184  9.36   9.4  9.43  ...      571       13       84       11
# 1   1655444006790  9.36   9.4  9.43  ...      546       13       78        1
# 2   1655444214402  9.36   9.4  9.43  ...       78      192      482       36
# 3   1655444232408  9.36   9.4  9.43  ...      192      482       30      214
# 4   1655444534190  9.36   9.4  9.43  ...      124      287      535       27
# 5   1655444643396  9.36   9.4  9.43  ...      287      535       27       45
# 6   1655444768796  9.36   9.4  9.43  ...      535       27       45      205
# 7   1655444894208  9.36   9.4  9.43  ...       27       45      202      475
# 8   1655445199602  9.36   9.4  9.43  ...       28       85      235      475
