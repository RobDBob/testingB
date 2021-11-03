from Helpers.PandaFunctions import convert_to_numeric
from datetime import datetime, timedelta
import pandas as pd
import json
from Helpers import const
from time import time

def get_account(client):
    """
    on occassion server can be behind a sec
    """
    client.get_account(timestamp=(time()*1000)-2000)


def get_historical_data(client, symbol, howLongMinutes, kline_interval):
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.utcnow()
    sinceThisDate = untilThisDate - timedelta(minutes = howLongMinutes)
    # Execute the query from binance - timestamps must be converted to strings !
    candles = client.get_historical_klines(symbol, kline_interval, str(sinceThisDate), str(untilThisDate))
    
    # df = rewrite_data_cleanup(candle)
    df = pd.DataFrame().from_records(candles)
    df.columns = const.all_columns
    
    # # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.set_index('dateTime', drop=False, inplace=True)
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(const.date_time_format)

    # Get rid of columns we do not need
    df = df.drop(const.columns_to_drop, axis=1)
    df = convert_to_numeric(df, ['open', 'high', 'low', 'close', 'volume'])
    
    return df


def get_datetime_single(date_time_stamp_ms):
    return datetime.utcfromtimestamp((int(date_time_stamp_ms)/1000)).strftime(const.date_time_format)