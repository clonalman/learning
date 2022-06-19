from datetime import datetime, time, timedelta
from pandas import DataFrame
from mootdx_rts import MootdxRTS

if __name__ == '__main__':

    std = MootdxRTS.std()
    cur_date = datetime(2022, 6, 17).date()
    # 实时分时行情
    qdf = std.quotes(['300033', '600745', '000635'])
    # 历史分时行情
    # qdf = tdx.minutes('300033', cur_date.strftime('%Y%m%d'))
    # 历史分笔
    # qdf = tdx.transactions('300033', cur_date.strftime('%Y%m%d'))

    print(qdf)

    if qdf is not None:
        std.saveToRts(qdf, cur_date)

        test_key = 'security:0:000635:' + cur_date.strftime("%Y%m%d")
        start_dt = datetime.combine(cur_date, time(0, 0, 0))
        end_dt = start_dt + timedelta(days=1)
        print('=========================================')
        print(test_key + "\t" + str(start_dt) + "\t" + str(end_dt))
        print('-----------------------------------------')

        rng = std.rtsCli.range(test_key, int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000))
        print(rng)
        print('-----------------------------------------')

        rdf = DataFrame([std.rtsCli.redis.hgetall(test_key + ":" + str(int(tick))) for ts, tick in rng])
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
#     ts             open close  high  ... bid_vol2 bid_vol3 bid_vol4 bid_vol5
# 0   1655443994184  9.36   9.4  9.43  ...      571       13       84       11
# 1   1655444006790  9.36   9.4  9.43  ...      546       13       78        1
# 2   1655444214402  9.36   9.4  9.43  ...       78      192      482       36
# 3   1655444232408  9.36   9.4  9.43  ...      192      482       30      214
# 4   1655444534190  9.36   9.4  9.43  ...      124      287      535       27
# 5   1655444643396  9.36   9.4  9.43  ...      287      535       27       45
# 6   1655444768796  9.36   9.4  9.43  ...      535       27       45      205
# 7   1655444894208  9.36   9.4  9.43  ...       27       45      202      475
# 8   1655445199602  9.36   9.4  9.43  ...       28       85      235      475
