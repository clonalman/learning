#!/usr/bin/python
# coding:utf-8
import json
import sys

from rediscluster import RedisCluster

with open(sys.path[0] + '/redis-cluster.json') as f:
    nodes = json.load(f)
    print(nodes)
    redis_cli = RedisCluster(startup_nodes=nodes, decode_responses=True)
    ps = redis_cli.pubsub()
    ps.subscribe('security')

    for item in ps.listen():
        print(item)

