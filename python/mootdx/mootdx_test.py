import json
import os
import sys
import threading
from datetime import datetime, time, timedelta
from re import split

from pandas import DataFrame
from rediscluster import ClusterDownError

from mootdx_rts import MootdxRTS
import mootdx_quotes
import mootdx_stocks


def printQuotes(std, code, cur_date):
    test_key = 'SECU:' + code + ':' + cur_date.strftime("%Y%m%d")
    print('=========================================')
    print(std.quotes(code))
    start_dt = datetime.combine(cur_date, time(0, 0, 0))
    end_dt = start_dt + timedelta(days=1)
    print('=========================================')
    print(test_key + "\t" + str(start_dt) + "\t" + str(end_dt))
    print('-----------------------------------------')

    rng = std.rtsCli.range(test_key, int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000))
    print(rng)
    print('-----------------------------------------')

    # if rng is not None:
    #     rdf = DataFrame([std.rtsCli.redis.hgetall(test_key + ":" + str(int(tick))) for ts, tick in rng])
    #     print(rdf)


def rename(std):
    keys = std.rtsCli.redis.keys()
    # keys = ["SECU:0:000555:20220701:1800", "SECU:0:000555:20220701:1801"]
    for key in keys:
        items = key.decode("utf-8").split(':')
        newKey = items[0]
        if items[1] == "0" or items[1] == "1" or items[1] == "9":
            if items[1] == "0":
                newKey += ":" + items[2] + ".SZ"
            if items[1] == "1":
                newKey += ":" + items[2] + ".SH"
            if items[1] == "9":
                newKey += ":" + items[2] + ".SF"

            if len(items) > 3:
                newKey += ":" + items[3]
            if len(items) > 4:
                newKey += ":" + items[4]
            if std.rtsCli.redis.exists(key):
                print(key, "=>", newKey)
                std.rtsCli.redis.rename(key, newKey, replace=True)


def renameKeys():
    running = True
    while running:
        try:
            rename(MootdxRTS.std(False))
            running = False
        except ClusterDownError as error:
            print(error)
            continue


if __name__ == '__main__':
    # std = MootdxRTS.std(False)
    # today = datetime(2022, 7, 2).date()
    # //{"host": "47.92.239.29", "port": 7777}
    # mootdx_stocks.fetch(std, today)
    # printQuotes(std, 0, '300033', today)
    # print(mootdx_quotes.get_stock_symbols())
    # df = std.quotes(['002984', '002985', '002986', '002987', '002988', '002989', '002990', '002991', '002992', '002993', '002995', '002996', '002997', '002998', '002999', '300001', '300002', '300003', '300004', '300005', '300006', '300007', '300008', '300009', '300010', '300011', '300012', '300013', '300014', '300015', '300016', '300017', '300018', '300019', '300020', '300021', '300022', '300023', '300024', '300025', '300026', '300027', '300029', '300030', '300031', '300032', '300033', '300034', '300035', '300036', '300037', '300038', '300039', '300040', '300041', '300042', '300043', '300044', '300045', '300046', '300047', '300048', '300049', '300050', '300051', '300052', '300053', '300054', '300055', '300056', '300057', '300058', '300059', '300061', '300062', '300063', '300064', '300065', '300066', '300067'])
    # for i, row in df.iterrows():
    #     print(row)
    # std.replay('600745.SH', today)
    renameKeys()