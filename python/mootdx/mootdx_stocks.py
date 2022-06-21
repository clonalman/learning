import json
import os
import sys
from datetime import datetime
from mootdx_rts import MootdxRTS, make_pid, kill_pid


def fetch(std, cur_date):
    if not os.path.exists('market'):
        os.makedirs('market')

    stocks_all = []
    for market in [0, 1]:
        qdf = std.stocks(market)
        for i, row in qdf.iterrows():
            stocks_all.append(row.to_dict())

    with open(sys.path[0] + '/market/stocks.' + cur_date.strftime("%Y%m%d") + '.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(stocks_all, ensure_ascii=False))
    with open(sys.path[0] + '/market/stocks.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(stocks_all, ensure_ascii=False))

    print("通达信全市场指数量: " + str(len(stocks_all)))


if __name__ == '__main__':
    make_pid('mootdx_stocks')
    fetch(MootdxRTS.std(), datetime.now().date())
    kill_pid('mootdx_stocks')
