import pandas_ta as ta

from Helpers.ScriptArguments import CreateScriptArgs
from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
from datetime import datetime
import TestScenarios

from MathFunctions.TATesting import TATester
from Helpers import const, APIHelper, DateHelper
import logging
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
        if (self.update_data_on_tick(df)):
            self.action_time()

    def action_time(self):
        test_result = TestScenarios.data_test_1(self.taTester, self.df)

        # set cannot have dups, so if list len is == 1, it contains an uniformed decision
        set_trade_result = set(test_result)

        if len(set_trade_result) > 1:
            "mixed messages, returning without action"
            return

        if const.TradeAction.buy in set_trade_result:
            self.buy()
        elif const.TradeAction.sell in set_trade_result:
            self.sell()

    def buy(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: BUY at: {self.df.loc[last_loc, 'close']} ")

    def sell(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: SELL at: {self.df.loc[last_loc, 'close']} ")

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

    def update_data_on_tick(self, df):
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
            # print(f"ping________________________ {df.loc[df.index[-1], 'dateTime']}")
            return False


def start_web_socket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, timeWindowMinutes=60, kline_interval=args.interval)
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
    from MathFunctions.TATesting import TATester
    log_strong_action = create_logger("strong", "ExistingData_strong.log")
    log_mixed_action =  create_logger("mixed", "ExistingData_weak.log")
    test_df = pd.read_pickle("4weekWorthBTCUSDT1mLive.pkl")
    # test_df = pd.read_pickle("1dayWorthBTCUSDT1mLive.pkl")
    initial_df = test_df[:60]
    incoming_data = test_df[60:]

    data_updater = TAAnalyzer(kline_interval=args.interval, historic_data=initial_df)

    monitor_price = False
    monitored_prices = []
    price_trend = 0

    for dx in range(len(incoming_data)):
        new_df = incoming_data.iloc[[dx]]
        
        
        if data_updater.update_data_on_tick(new_df):
            # updates data only on matching interval: true / false from update_test_data
            # interval tick landed
            bbvol = ta.bbands(data_updater.df["volume"], length=18, std=2)

            if bbvol.tail(1)["BBP_18_2.0"].values[0] > 1:
                # abnormal market volume trading , maybe singal to buy or sell
                # might influence price move
                monitor_price = True
                # log.info("bbvol: monitor price: TRUE")

        # controlling flags:
        if monitor_price:
            recent_prices = data_updater.df.tail(2)["close"].values # order index 0: most recent
            trend_decreasing = recent_prices[0] < recent_prices[1]
            monitored_prices.append(trend_decreasing)

            if len(set(monitored_prices)) == 1: # set cannot have duplicates, so 1 for all elements being same
                # same trend, carry on
                continue
            else:
                # trend changed, hard stop to evaluate other tests
                rsi = ta.rsi(data_updater.df["close"], length=12)
                rsi_test_result = data_updater.taTester.rsi_test(rsi, buy=trend_decreasing)

                stoch = ta.stoch(data_updater.df["high"], data_updater.df["low"], data_updater.df["close"])
                stoch_test_result = data_updater.taTester.stoch_test(stoch, buy=trend_decreasing)

                data_updater.df["close"]
                
                if len(set([trend_decreasing, rsi_test_result, stoch_test_result]))==1:
                    log_strong_action.info(f"BUY: {trend_decreasing}? Stamp: {data_updater.df.dateTime.tail(1).values[0]}, Price: {data_updater.df.close.tail(1).values[0]}")
                else:
                    log_mixed_action.info(f"BUY: {trend_decreasing}? Stamp: {data_updater.df.dateTime.tail(1).values[0]}, Price: {data_updater.df.close.tail(1).values[0]}; rsi:{rsi_test_result}, sto:{stoch_test_result}")

                monitor_price = False
                monitored_prices.clear()

        else:
            monitored_prices.clear()
        
        
        
        
        # TestScenarios.data_test_1(data_updater.taTester, data_updater.df)
        
        # TestScenarios.data_test_1(data_updater.taTester, data_updater.df)


if __name__ == "__main__":
    args = CreateScriptArgs()

    # start_web_socket(args)
    run_test_on_existind_data(args)