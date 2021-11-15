import numpy as np
import pandas_ta as ta
from Helpers.ScriptArguments import CreateScriptArgs
from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd

from time import time
from datetime import datetime
import TestScenarios
from FinanceFunctions.Ledger import CoinLedger
from MathFunctions.TATesting import TATester
from Helpers import const, APIHelper, DateHelper, PandaFunctions, DBFunctions , Plotter
from MathFunctions.TATesting import TATester
from PriceWatcher import PriceWatcher
from SignalTrigger import SignalTrigger
import logging
from GetLogger import create_logger

logger_name_detail = "WebSocketPriceUpdaterTester_detail"
create_logger(logger_name_detail, "LOG_TestRecords_detail.log")

logger_name_high_level = "WebSocketPriceUpdaterTester"
create_logger(logger_name_high_level, "LOG_TestRecords.log")
"""
from time import time
import pandas as pd
import pandas_ta as ta
from Helpers import const, APIHelper, DateHelper, PandaFunctions, DBFunctions 
import matplotlib.pyplot as plt

records = DBFunctions.get_records_after_timestamp(time()-3600*12)

records_60s = [k for k in records if not k[0] % 60]
len(records_60s)
df = PandaFunctions.get_df_from_db_records(records_60s)

df.ta.strategy()
df.plot(x="dateTime", y="close")
plt.show()

"""

class HQBrain:
    def __init__(self, kline_interval, historic_data=None, logger=None):
        self.kline_interval = kline_interval

        if historic_data is None:
            self.df = pd.DataFrame()
        else:
            self.df = historic_data
        
        # to indicate trades, for last drawning / analysis
        # self.df["bought"]=np.nan
        # self.df["sold"]=np.nan

        self.logger = logging.getLogger(logger_name_high_level)
        # self.taTester = TATester(logger_name_detail)
        self.taTester = TATester(logger)

    @property
    def current_datetime(self):
        return DateHelper.get_datetime_single_from_ms(self.df.index[-1])

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

        if const.TransactionType.buy in set_trade_result:
            self.buy()
        elif const.TransactionType.sell in set_trade_result:
            self.sell()

    def buy(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: BUY at: {self.df.loc[last_loc, 'close']} ")

    def sell(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: SELL at: {self.df.loc[last_loc, 'close']} ")

    def convert_to_df_from_kline(self, msg):
        data = {
            "timeStamp": [msg['E']], 
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
        df.set_index('timeStamp', drop=False, inplace=True)
        df.rename(columns={"timeStamp": 'dateTime'}, inplace=True)
        df.dateTime = DateHelper.get_datetime_single_from_ms(df.dateTime)
        return df

    def update_data_on_tick(self, df):
        """
        tick may / may not land exactly on a interval mark, hence it might be of by a sec or few
        index: single value, timeStamp
        """
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.utcfromtimestamp(df.index[-1]/1000) > datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.df = self.df.append(df)
            return True
        else:
            return False


def start_web_socket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, timeWindowMinutes=60, kline_interval=args.interval)
    data_updater = HQBrain(kline_interval=args.interval, historic_data=historic_data)

    twm = ThreadedWebsocketManager(testnet=args.test_net)
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=data_updater.do_stuff_with_klline, symbol=args.symbol)
    twm.join(timeout=args.timeout)

def run_test_on_existind_data_from_file(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    from MathFunctions.TATesting import TATester
    from PriceWatcher import PriceWatcher
    from SignalTrigger import SignalTrigger
    
    # test_df = pd.read_pickle("4weekWorthBTCUSDT1mLive.pkl")
    # test_df = pd.read_pickle("1dayWorthBTCUSDT1mLive.pkl")
    test_df = pd.read_pickle("1weekWorthBTCUSDT1mLive.pkl")
    initial_df = test_df[:60]
    incoming_data = test_df[60:]

    logger = create_logger("DataTest2", "LOG_Scenario_price_check.log")
    
    data_holder = HQBrain(kline_interval=args.interval, historic_data=initial_df, logger=logger)

    monitor_price = False
    log_flag_monitor_price = False
    
    price_watcher = PriceWatcher(data_holder, logger)
    signal_trigger = SignalTrigger(data_holder, logger)

    for dx in range(len(incoming_data)):
        new_df = incoming_data.iloc[[dx]]

        # if data_holder.update_data_on_tick(new_df):
        data_holder.df = data_holder.df.append(new_df)
        monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode()
                
        if monitor_price:
            if log_flag_monitor_price is False:
                logger.info(f"{data_holder.current_datetime}: START WATCHING")
                log_flag_monitor_price = True
            
            monitor_price = price_watcher.recalculate_conditions()
            
            if monitor_price is False:
                logger.info(f"{data_holder.current_datetime}: STOP WATCHING \n")
                log_flag_monitor_price = False
                # change of price- what's the plan?

def run_test_on_existind_data_from_db(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    # initial_time_stamp = int(time())-3*3600
    # time[s]
    initial_time_stamp = 1636670930
    print(f"initial time stamp: {initial_time_stamp}")
    raw_records = DBFunctions.get_records_between_timestamps(initial_time_stamp, initial_time_stamp+14*3600)

    # time [ms]
    df = PandaFunctions.get_df_from_records(raw_records)

    logger = create_logger("DataTest2", "LOG_Scenario_price_check_from_db.log")
    
    ledger = CoinLedger(logger)
    ledger.bank = 1000
    price_df = pd.DataFrame({"timeStamp": [], "bought": [], "sold":[]})
    df_5m = pd.DataFrame({"timeStamp": [], "close": [], "BBUpper": [], "BBLower": [], "BBMedian":[]})
    df_5m[["timeStamp"]] = df_5m[["timeStamp"]].astype(np.int64)
    df_bb5mL9 = None

    from Helpers.PriceCheckSession import PriceCheckSession
    last_price = 0
    prep_to_sell = False
    prep_to_buy = False

    # for record in remaining_records:
    for dx in range(len(df)):
        current_timestamp = df.iloc[dx].name
        recent_tick_df = df[df.index <= current_timestamp].tail(202)
        current_price = recent_tick_df.at[current_timestamp, "close"]

        recent_tick_df["sma200"] = ta.sma(recent_tick_df.close, length=200)
        recent_tick_df["sma50"] = ta.sma(recent_tick_df.close, length=50)

        if (current_timestamp % 300000) == 0:
            # ensure added records are on or after 15min mark
            if len(df_5m) > 0:
                previous_timestamp = df_5m.tail(1).timeStamp
                if current_timestamp < int(previous_timestamp) + 300000:
                    continue
            
            # cast timestamp to str to prevent auto type assigment to float
            df_5m = df_5m.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)
            df_bb5mL9 = ta.bbands(df_5m.close, length=9)
            
            if df_bb5mL9 is not None:
                df_5m["BBUpper"] = df_bb5mL9["BBU_9_2.0"]
                df_5m["BBLower"] = df_bb5mL9["BBL_9_2.0"]
                df_5m["BBMedian"] = df_bb5mL9["BBM_9_2.0"]
        
        if df_bb5mL9 is None or np.any(np.isnan(df_bb5mL9.tail(1))):
            continue
        # if pd.isnull(recent_tick_df.at[current_timestamp, "sma200"]):
        #     continue

        rsi9 = ta.rsi(recent_tick_df.close, 9)
        # sma9 = ta.sma(recent_tick_df.close, 9)

        current_price_below_sma200 =  recent_tick_df.at[current_timestamp, "close"] < recent_tick_df.at[current_timestamp, "sma200"]
        current_price_above_sma200 =  recent_tick_df.at[current_timestamp, "close"] > recent_tick_df.at[current_timestamp, "sma200"]
        current_price_below_sma50 =  recent_tick_df.at[current_timestamp, "close"] < recent_tick_df.at[current_timestamp, "sma50"]
        current_price_above_sma50 =  recent_tick_df.at[current_timestamp, "close"] > recent_tick_df.at[current_timestamp, "sma50"]

        if current_price_below_sma200 and current_price_below_sma50:
            if rsi9.iat[-1] < 5:
                if ledger.propose_buy(current_price, current_timestamp):
                    price_df = price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
                    continue

            if rsi9.iat[-1] < 30:
                prep_to_buy = True
            elif prep_to_buy and ta.decreasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
                pass
            elif prep_to_buy and current_price_below_sma200:
                if ledger.propose_buy(current_price, current_timestamp):
                    price_df = price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
                    prep_to_buy = False
        
        if current_price_above_sma200 and current_price_above_sma50:
            if rsi9.iat[-1] > 95:
                if ledger.propose_sell(current_price, current_timestamp):
                    price_df = price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
                    continue

            if rsi9.iat[-1] > 70:
                prep_to_sell = True
            elif prep_to_sell and ta.increasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
                pass
            elif prep_to_sell:
                if ledger.propose_sell(current_price, current_timestamp):
                    prep_to_sell = False
                    price_df = price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
            
        
    # last_price = data_hq.df.tail(1).close.values[0]

    last_price = recent_tick_df.tail(1).close.values[0]
    df["sma9"] = ta.sma(df.close, length=9)
    df["sma50"] = ta.sma(df.close, length=50)
    df["sma200"] = ta.sma(df.close, length=200)
    df["decSMA50"] = ta.decreasing(df["sma50"], length=3, asint=False)
    df.to_csv("test_data_output.csv")
    price_df.to_csv("test_data_trades.csv")
    price_df.to_pickle("price.pkl")

    logger.info(f"The END: bank_money: {ledger.bank}, coins: {ledger.available_coins}")
    logger.info(f"With sold stock at most recent price ({last_price}): {last_price*ledger.available_coins+ledger.bank}")
    logger.info(f"Actual worth (without loss): {ledger.sum_of_active_transactions()+ledger.bank}")
    logger.info(f"All transactions: {len(ledger.transaction_history)}, active_transactions: {len([k for k in ledger.transaction_history if k.active])}")
    logger.info(f"All open transactions: {[k.coin_value for k in ledger.transaction_history if k.active]}")

    # Plotter.plot_data(df, price_df)
    # df.reset_index(inplace=True)
    df.to_pickle("pickle.pkl")
    df_5m["timeStamp"] = df_5m[["timeStamp"]].astype(np.int64)
    df_5m.set_index("timeStamp", inplace=True)
    df_5m.to_pickle("df_5m.pkl")
    print(df.tail(10))
    print(df_5m.tail(10))

    mx=df.plot(y="close", c="orange")
    df.plot(y="sma50", c="green", ax=mx)
    df.plot(y="sma200", c="fuchsia", ax=mx)
    df_5m.plot(y="BBUpper", c="black", ax=mx)
    df_5m.plot(y="BBLower", c="black", ax=mx)
    df_5m.plot(y="BBMedian", c="black", ax=mx)
    ax=price_df.plot.scatter(x="timeStamp", y="bought", c="red", ax=mx)
    for i, txt in enumerate(price_df.bought):
        ax.annotate(txt, (price_df.timeStamp.iat[i], price_df.bought.iat[i]))

    bx=price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
    for i, txt in enumerate(price_df.sold):
        bx.annotate(txt, (price_df.timeStamp.iat[i], price_df.sold.iat[i]))
    
    import matplotlib.pyplot as plt
    plt.show()

            

if __name__ == "__main__":
    args = CreateScriptArgs()
    # start_web_socket(args)
    run_test_on_existind_data_from_db(args)