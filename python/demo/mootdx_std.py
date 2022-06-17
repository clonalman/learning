from mootdx.quotes import Quotes

# 标准市场
client = Quotes.factory(market='std', multithread=True, heartbeat=True)


def quotes(symbol):
    # 实时行情
    return client.quotes(symbol=symbol)


def bars(symbol):
    # k 线数据
    client.bars(symbol=symbol, frequency=9, offset=10)


def index(symbol, frequency=9):
    # 指数
    client.index(symbol=symbol, frequency=frequency)


def minutes(symbol, date, **kwargs):
    # 历史分时
    client.minutes(symbol=symbol, date=date, **kwargs)


if __name__ == '__main__':
    df = quotes(symbol=["300033", "600745", "000635", "002638"]);
    print(df)
