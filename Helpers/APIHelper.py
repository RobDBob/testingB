from Helpers.PandaFunctions import convert_to_numeric
from datetime import datetime, timedelta
import pandas as pd
from Helpers import const
from time import time
from binance import ThreadedWebsocketManager
from binanceHelper.bFinanceAPIFunctions import getClient
import pandas as pd

from datetime import datetime
from Helpers import const, APIHelper

def get_account(client):
    """
    on occassion server can be behind a sec
    """
    client.get_account(timestamp=(time()*1000)-2000)


def get_historical_data(client, symbol, timeWindowMinutes, kline_interval):
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.utcnow()
    sinceThisDate = untilThisDate - timedelta(minutes = timeWindowMinutes)
    # Execute the query from binance - timestamps must be converted to strings !
    candles = client.get_historical_klines(symbol, kline_interval, str(sinceThisDate), str(untilThisDate))
    
    # df = rewrite_data_cleanup(candle)
    df = pd.DataFrame().from_records(candles)
    df.columns = const.all_columns
    df = convert_to_numeric(df, const.columns_to_keep)
    # # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.set_index('dateTime', drop=False, inplace=True)
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(const.date_time_format)

    # Get rid of columns we do not need
    df = df.drop(const.columns_to_drop, axis=1)
    
    
    return df


def start_web_socket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, timeWindowMinutes=60, kline_interval=args.interval)
    ## data_updater = HQBrain(kline_interval=args.interval, historic_data=historic_data)
    callback = None

    twm = ThreadedWebsocketManager(testnet=args.test_net)
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=callback, symbol=args.symbol) # data_updater.do_stuff_with_klline, symbol=args.symbol)
    twm.join(timeout=args.timeout)