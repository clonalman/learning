import json
import sys
import threading
import time
import traceback
from datetime import datetime

from pytdx.parser.base import ResponseHeaderRecvFails, ResponseRecvFails
from mootdx_rts import MootdxRTS, make_pid


def get_stock_symbols():
    result = []
    # ["600", "601", "603", "688", "000", "002", "300"]
    with open(sys.path[0] + '/market/stocks.json', encoding='utf-8') as f1:
        json_stocks = json.load(f1)
        with open(sys.path[0] + '/redis-symbol.json', encoding='utf-8') as f2:
            json_symbols = json.load(f2)
            for stock in json_stocks:
                if stock['code'].startswith(tuple(json_symbols)):
                    result.append(stock['code'])
    print('Now:', time.strftime('%H:%M:%S', time.localtime()), "Thread:", threading.current_thread().ident, "Total symbols:", len(result))
    print("================================")
    return result


def createTimer(std, symbols):
    global thread
    thread = threading.Timer(0.2, repeat, args=(std, symbols,))
    thread.start()


def repeat(std, symbols):
    print('Now:', time.strftime('%H:%M:%S', time.localtime()), "Thread:", threading.current_thread().ident, "Symbols:", len(symbols))
    print("--------------------------------")
    # 实时分时行情
    num = 0
    while num < len(symbols):
        start_dt = datetime.now()
        try:
            items = symbols[num:num + 80]
            print(items)
            qdf = std.quotes(items)
            if qdf is not None:
                std.save(datetime.now().date(), qdf)

            end_dt = datetime.now()
            num = num + 80
            print('cost: %dms' % ((end_dt - start_dt).seconds * 1000 + (end_dt - start_dt).microseconds / 1000))
        except (ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
                ResponseRecvFails,
                ResponseHeaderRecvFails):
            traceback.print_exc()
            end_dt = datetime.now()
            print('cost: %dms(error)' % ((end_dt - start_dt).seconds * 1000 + (end_dt - start_dt).microseconds / 1000))
            std = MootdxRTS.std()
            time.sleep(1)
        except Exception:
            traceback.print_exc()
            end_dt = datetime.now()
            print('cost: %dms(exception)' % (
                    (end_dt - start_dt).seconds * 1000 + (end_dt - start_dt).microseconds / 1000))
            time.sleep(1)

    createTimer(std, symbols)


if __name__ == '__main__':
    make_pid('mootdx_quotes')

    num_timer = 7

    stock_symbols = get_stock_symbols()
    total = len(stock_symbols)
    batch = 0
    batch_size = int(total / num_timer) if total % num_timer == 0 else int(total / num_timer) + 1
    while batch < total:
        createTimer(MootdxRTS.std(), stock_symbols[batch:batch + batch_size])
        batch += batch_size
