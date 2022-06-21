import json
import sys
import threading
import time
import traceback
from datetime import datetime
from mootdx_rts import MootdxRTS, make_pid


def run(std, symbols):
    # 实时分时行情
    num = 0
    while num < len(symbols):
        try:
            items = symbols[num:num + 80]
            print(items)
            qdf = std.quotes(items)
            time.sleep(0.05)
            if qdf is not None:
                std.save(datetime.now().date(), qdf)
            num += 80
        except ConnectionError:
            traceback.print_exc()
            std = MootdxRTS.std()
        except Exception:
            traceback.print_exc()
            time.sleep(1)

    r_t01 = threading.Timer(10, run, args=(std, symbols,))
    r_t01.start()


def get_stock_symbols():
    result = []
    # '600', '601', '603', '688'
    # '000', '002', '300'
    with open(sys.path[0] + '/market/stocks.json', encoding='utf-8') as f1:
        json_stocks = json.load(f1)
        with open(sys.path[0] + '/redis-symbol.json', encoding='utf-8') as f2:
            json_symbols = json.load(f2)
            for stock in json_stocks:
                if stock['code'].startswith(tuple(json_symbols)):
                    result.append(stock['code'])
    return result


if __name__ == '__main__':
    # print("sys.path[0] =", sys.path[0])
    # print("sys.argv[0] =", sys.argv[0])
    # print("__file__ =", __file__)
    # print("os.path.abspath(__file__) =", os.path.abspath(__file__))
    # print("os.path.realpath(__file__) = ", os.path.realpath(__file__))
    # print("os.path.dirname(os.path.realpath(__file__)) =", os.path.dirname(os.path.realpath(__file__)))
    # print("os.path.split(os.path.realpath(__file__)) =", os.path.split(os.path.realpath(__file__)))
    # print("os.getcwd() =", os.getcwd())

    make_pid('mootdx_quotes')
    symbols = get_stock_symbols()
    total = len(symbols)
    batch = 0
    batch_size = int(total / 10)
    while batch < total:
        std = MootdxRTS.std()
        t01 = threading.Thread(target=run, args=(std, symbols[batch:batch + batch_size]))
        t01.start()
        batch += batch_size
