from datetime import datetime
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
        std.save(cur_date, qdf)

