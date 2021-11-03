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

    def do_stuff_with_klline(self, msg):
        df = self.convert_to_df_from_kline(msg)
        if (self.update_test_data(df)):
            self.run_tests_with_new_data()
    
    def run_tests_with_new_data(self):
        buy = []
        sell = []
        rsi = ta.rsi(self.df["close"], length=12)
        buy.append(self.taTester.rsi_test(rsi, buy=True))
        sell.append(self.taTester.rsi_test(rsi, buy=False))

        stoch = ta.stoch(self.df["high"], self.df["low"], self.df["close"])
        buy.append(self.taTester.stoch_test(stoch, buy=True))
        sell.append(self.taTester.stoch_test(stoch, buy=False))

        bb = ta.bbands(self.df["close"], length=18, std=2)
        # check where price touches and trend
        # iloc[-1, ] 
        # column indexes: 0:BBLow, 1:BBMedian, 2:BBUpper, 3:BBBandwidth, 4:BBPercent
        last_close_value = self.df.loc[self.df.index[-1], "close"]
        buy.append(self.taTester.bb_test(bb, last_close_value, buy=True))
        sell.append(self.taTester.bb_test(bb, last_close_value, buy=False))
        
        #self.logger.info(f"Close: . BUY: {all(buy)}, SELL: {all(sell)}")

        if all(buy):
            last_loc = self.df.index[-1]
            self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: BUY action, at close price: {self.df.loc[last_loc, 'close']} ")
            # self.buy()

        if all(sell):
            last_loc = self.df.index[-1]
            self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: SELL action, at close price: {self.df.loc[last_loc, 'close']} ")
            # self.sell()

    def buy(self):
        # order = self.client.create_order(symbol=self.symbol, side="BUY", type="MARKET", quantity=0.0001)
        # self.logger(pprint(order))
        return

    def sell(self):
        # order = self.client.create_order(symbol=self.symbol, side="SELL", type="MARKET", quantity=0.0001)
        # self.logger(pprint(order))
        return

    def convert_to_df_from_kline(self, msg):
        data = {
            "dateTime": [msg['E']], 
            "open": [float(msg['k']['o'])], 
            "high": [float(msg['k']['h'])], 
            "low": [float(msg['k']['l'])], 
            "close": [float(msg['k']['c'])], 
            "volume": [float(msg['k']['v'])]}
        return self.convert_to_df(data)

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
        """
        index: single value, timeStamp
        """
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.utcfromtimestamp(df.index[-1]/1000) > datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.df = self.df.append(df)
            return True
        else:
            # print(f"Updated: FALSE: {self._get_datetime_single(msg['E'])} > {counted}")
            print(f"ping________________________ {df.loc[df.index[-1], 'dateTime']}")
            return False


def start_web_socket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, howLongMinutes=60, kline_interval=args.interval)
    data_updater = TAAnalyzer(kline_interval=args.interval, historic_data=historic_data)

    twm = ThreadedWebsocketManager(testnet=args.test_net)
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=data_updater.do_stuff_with_klline, symbol=args.symbol)
    twm.join(timeout=args.timeout)

def run_test_on_existind_data(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    df = pd.read_pickle("2weekWorthBTCUSDT3m.pkl")
    initial_df = df[:60]
    later_df = df[60:]

    data_updater = TAAnalyzer(kline_interval=args.interval, historic_data=initial_df)
    dataseries_columns = df.columns.tolist()

    for dx in range(len(later_df)):
        dataseries = later_df.iloc[dx]
        dataseries_values = [[k] for k in dataseries.values.tolist()]

        # assume first column is dataTime (string format; converted timestamp)
        # this needs to be datatime (int format; timestamp)
        dataseries_values[0][0] = dataseries.name
        temp_dict = dict(zip(dataseries_columns, dataseries_values))
        new_df = data_updater.convert_to_df(temp_dict)
        
        data_updater.update_test_data(new_df)
        data_updater.run_tests_with_new_data()


if __name__ == "__main__":
    args = CreateScriptArgs()

    # start_web_socket(args)
    run_test_on_existind_data(args)