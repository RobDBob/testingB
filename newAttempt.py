from Helpers.ScriptArguments import CreateScriptArgs
from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
from datetime import datetime
import pandas_ta as ta
from MathFunctions.TATesting import TATester
from Helpers import PandaFunctions, const, APIHelper, DateHelper
import logging
from pprint import pprint
from GetLogger import create_logger

logger_name_detail = "WebSocketPriceUpdaterTester_detail"
create_logger(logger_name_detail, "TestRecords_detail.log")

logger_name_high_level = "WebSocketPriceUpdaterTester"
create_logger(logger_name_high_level, "TestRecords.log")

class TAAnalyzer:
    def __init__(self, kline_interval, historic_data=None):
        self.kline_interval = kline_interval

        if historic_data is None:
            self.df = pd.DataFrame()
        else:
            self.df = historic_data

        self.logger = logging.getLogger(logger_name_high_level)
        self.taTester = TATester(logger_name_detail)
    
    def _get_datetime_series(self, date_time_stamps_ms):
        # print(f"---- type: {type(date_time_stamps_ms)}, value: {date_time_stamps_ms}")
        return pd.to_datetime(date_time_stamps_ms, unit='ms').dt.strftime(const.date_time_format)

    def do_stuff(self, msg):
        if (self.update_test_data(msg)):
            buy = []
            sell = []
            buy.append(self.taTester.rsi_test(ta.rsi(self.df["close"], length=12), buy=True))
            sell.append(self.taTester.rsi_test(ta.rsi(self.df["close"], length=12), buy=False))

            buy.append(self.taTester.stoch_test(ta.stoch(self.df["high"], self.df["low"], self.df["close"]), buy=True))
            sell.append(self.taTester.stoch_test(ta.stoch(self.df["high"], self.df["low"], self.df["close"]), buy=False))

            buy.append(self.taTester.bb_test(self.df, buy=True))
            sell.append(self.taTester.bb_test(self.df, buy=False))
            
            self.logger.info(f"Close: . BUY: {all(buy)}, SELL: {all(sell)}")

            if all(buy):
                print(f"SELL action, at close price: {self.df.loc[self.df.index[-1], 'close']} ")
                # self.buy()

            if all(sell):
                print(f"BUY action, at close price: {self.df.loc[self.df.index[-1], 'close']} ")
                # self.sell()

    def buy(self):
        # order = self.client.create_order(symbol=self.symbol, side="BUY", type="MARKET", quantity=0.0001)
        # self.logger(pprint(order))
        return

    def sell(self):
        # order = self.client.create_order(symbol=self.symbol, side="SELL", type="MARKET", quantity=0.0001)
        # self.logger(pprint(order))
        return

    def callback_update_to_df_from_kline(self, msg):
        data = {
            "dateTime": [msg['E']], 
            "open": [float(msg['k']['o'])], 
            "high": [float(msg['k']['h'])], 
            "low": [float(msg['k']['l'])], 
            "close": [float(msg['k']['c'])], 
            "volume": [float(msg['k']['v'])]}
        df = self.convert_to_df(data)
        self.update_test_data(df)

        # ds = pd.Series(data=data, index="dateTime")
        # columns_to_keep = ['dateTime', 'open', 'high', 'low', 'close', 'volume']

    def convert_to_df(self, data):
        """
        data: dict
        key: string: column names
        value: list: column values
        """
        df = pd.DataFrame(data)
        df.set_index('dateTime', drop=False, inplace=True)
        df.dateTime = DateHelper.get_datetime_single(df.dateTime)
        return df

    def update_test_data(self, df):
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.utcfromtimestamp(df.index[-1]/1000) > datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.locked = True
            try:
                self.df = self.df.append(df)

                print(f"Updated: {df.loc[df.index[-1], 'dateTime']}, new price: {df.loc[df.index[-1], 'close']}")

            except Exception as e:
                print(e)
                return False
                
            finally:
                self.locked = False
                return True

        else:
            # print(f"Updated: FALSE: {self._get_datetime_single(msg['E'])} > {counted}")
            print(f"ping________________________ {df.loc[df.index[-1], 'dateTime']}")
            return False


def start_web_socket(args, data_updater):
    twm = ThreadedWebsocketManager(testnet=args.test_net)
    twm.daemon = True
    twm.start()
    #twm.start_symbol_miniticker_socket(callback=data_frame.update_df, symbol=data_frame.symbol)
    twm.start_kline_socket(callback=data_updater.callback_update_to_df_from_kline, symbol=args.symbol)
    twm.join(timeout=args.timeout)

def run_test_on_existind_data(args):
    df = pd.read_pickle("2weekWorthBTCUSDT3m.pkl")
    initial_df = df[:60]
    later_df = df[60:]
    data_updater = TAAnalyzer(kline_interval=args.interval, historic_data=initial_df)
    
    for dx in range(len(later_df)):
        data_updater.update_test_data(later_df.iloc[dx])
    return

def run_of_websocket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, howLongMinutes=60, kline_interval=args.interval)
    data_updater = TAAnalyzer(kline_interval=args.interval, historic_data=historic_data)
    start_web_socket(args, data_updater)


if __name__ == "__main__":
    args = CreateScriptArgs()

    run_of_websocket(args)
    # run_test_on_existind_data(args)