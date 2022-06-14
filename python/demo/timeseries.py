from rediscluster import RedisCluster
from redistimeseries.client import Client
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
    {'host': '192.168.1.12', 'port': 7006},
]

conn = RedisCluster(startup_nodes=nodes, decode_responses=True)
print(conn)

rts = Client(conn=conn)
# rts.create('last-upsert', labels={'Time': 'Series'}, duplicate_policy='last')
# rts.add('last-upsert', 1548149181, 10.0)
# rts.add('last-upsert', 1548149210, 5.0)
# # should output [(1, 5.0)]
# print(rts.range('last-upsert', 1548149180, 1548149210))

rts.create('temperature:3:11', labels={"sensor_id": 2, "area_id": 32}, retention_msecs=60)
rts.add('temperature:3:11', 1548149181, 30)
rts.add('temperature:3:11', 1548149191, 42)
rts.add('temperature:3:11', 1548149201, 51)
print(rts.range('temperature:3:11', 1548149180, 1548149210, aggregation_type='avg', bucket_size_msec=5))
