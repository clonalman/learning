import json
import os
from datetime import datetime
from mootdx_rts import MootdxRTS


def fetch(std, cur_date):
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

    with open('market/stocks.a.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(astocks, ensure_ascii=False))


if __name__ == '__main__':
    fetch(MootdxRTS.std(), datetime.now().date())
