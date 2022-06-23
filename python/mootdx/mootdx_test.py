import json
import os
import sys
import threading
from datetime import datetime, time, timedelta
from pandas import DataFrame
from mootdx_rts import MootdxRTS
import mootdx_quotes
import mootdx_stocks


def printQuotes(std, market, code, cur_date):
    test_key = 'SECU:' + str(market) + ':' + code + ':' + cur_date.strftime("%Y%m%d")
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


if __name__ == '__main__':
    std = MootdxRTS.std()
    today = datetime(2022, 6, 23).date()
    # mootdx_stocks.fetch(std, today)
    printQuotes(std, 0, '300033', today)
    # print(mootdx_quotes.get_stock_symbols())
