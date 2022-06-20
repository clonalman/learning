import json
import threading
import traceback
from datetime import datetime
from mootdx_rts import MootdxRTS


def run(std, symbols):
    # 实时分时行情
    num = 0
    while num < len(symbols):
        try:
            items = symbols[num:num + 80]
            print(items)
            qdf = std.quotes(items)
            if qdf is not None:
                std.save(datetime.now().date(), qdf)
            num += 80
        except:
            traceback.print_exc()

    r_t01 = threading.Timer(3, run, args=(std, symbols,))
    r_t01.start()


if __name__ == '__main__':
    with open('market/stocks.a.json', encoding='utf-8') as f:
        stocks = json.load(f)
        symbols = [stock['code'] for stock in stocks]

        total = len(symbols)
        batch = 0
        batch_size = int(total / 10)
        while batch < total:
            std = MootdxRTS.std()
            t01 = threading.Thread(target=run, args=(std, symbols[batch:batch + batch_size]))
            t01.start()
            batch += batch_size
