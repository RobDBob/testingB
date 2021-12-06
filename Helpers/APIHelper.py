from datetime import datetime, timedelta
import pandas as pd
from Helpers import const
from time import time
from binanceHelper.bFinanceAPIFunctions import getClient
import pandas as pd

from datetime import datetime
from Helpers import const

# Environment settings: 
# pd.set_option('display.max_column', None)
pd.set_option('display.max_rows', None)
# pd.set_option('display.max_seq_items', None)
# pd.set_option('display.max_colwidth', 500)
# pd.set_option('expand_frame_repr', True)

def get_account(client):
    """
    on occassion server can be behind a sec
    """
    return client.get_account(timestamp=(time()*1000)-2000)


def get_historical_data(symbol, timeWindowMinutes, kline_interval):
    client = getClient(False)
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.utcnow()
    sinceThisDate = untilThisDate - timedelta(minutes = timeWindowMinutes)
    # Execute the query from binance - timestamps must be converted to strings !
    candles = client.get_historical_klines(symbol, kline_interval, str(sinceThisDate), str(untilThisDate))
    
    # df = rewrite_data_cleanup(candle)
    df = pd.DataFrame().from_records(candles)
    df.columns = const.all_columns
    df = df.drop(const.columns_to_drop, axis=1)

    # # as timestamp is returned in ms, let us convert this back to proper timestamps.
    # df.set_index('timeStamp', drop=False, inplace=True)
    # df.timeStamp = pd.to_datetime(df.timeStamp, unit='ms').dt.strftime(const.date_time_format)
    return df

def get_klines(symbol, limit=500, interval="1m"):
    client = getClient(False)
    # Execute the query from binance - timestamps must be converted to strings !
    candles = client.get_klines(symbol=symbol, limit=limit, interval=interval)
    
    # df = rewrite_data_cleanup(candle)
    df = pd.DataFrame().from_records(candles)
    df.columns = const.all_columns
    df = df.drop(const.columns_to_drop, axis=1)

    # # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.set_index('timeStamp', drop=False, inplace=True)
    df.timeStamp = pd.to_datetime(df.timeStamp, unit='ms').dt.strftime(const.date_time_format)
    return df


def test():
    symbol = "ALPACAUSDT"
    df = get_klines(symbol)
    print(df)