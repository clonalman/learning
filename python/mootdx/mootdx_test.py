import json
import os
import sys
import threading
from datetime import datetime, time, timedelta
from pandas import DataFrame
from mootdx_rts import MootdxRTS


def printStocks(std, cur_date):
    stock_path = 'market/' + cur_date.strftime("%Y%m%d")
    if not os.path.exists(stock_path):
        os.makedirs(stock_path)

    astocks = []
    for market in [0, 1]:
        qdf = std.stocks(market)
        rows = []
        for i, row in qdf.iterrows():
            item = row.to_dict()
            # 债券：900
            if item['code'].startswith(('600', '601', '603', '688', '000', '002', '300')):
                astocks.append(item)
            rows.append(item)

        with open(stock_path + '/stocks.' + str(market) + '.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(rows, ensure_ascii=False))

    print("A股: " + str(len(astocks)))
    with open(stock_path + '/stocks.a.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(astocks, ensure_ascii=False))


def printQuotes(std, cur_date):
    # 实时分时行情
    qdf = std.quotes(['300033', '600745', '000635'])
    # 历史分时行情
    # qdf = tdx.minutes('300033', cur_date.strftime('%Y%m%d'))
    # 历史分笔
    # qdf = tdx.transactions('300033', cur_date.strftime('%Y%m%d'))

    print(qdf)

    if qdf is not None:
        std.save(cur_date, qdf)

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


def run():
    std = MootdxRTS.std()
    today = datetime(2022, 6, 20).date()
    # printStocks(std, today)
    printQuotes(std, today)

    r_t01 = threading.Timer(10, run)
    r_t01.start()


if __name__ == '__main__':
    t01 = threading.Thread(target=run)
    t01.start()