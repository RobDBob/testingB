import numpy as np
import pandas_ta as ta
from Helpers.ScriptArguments import CreateScriptArgs
from binance import helpers
# from binanceHelper.bFinanceAPIFunctions import getClient
import pandas as pd

from time import time
from datetime import datetime
import TestScenarios
from FinanceFunctions.Ledger import CoinLedger
from TAAnalysis.TATesting import TATester
from Helpers import const, DateHelper, PandaFunctions, DBFunctions , Plotter
from PriceWatcher import PriceWatcher
from SignalTrigger import SignalTrigger
from GetLogger import create_logger

# logger_name_detail = "WebSocketPriceUpdaterTester_detail"
# create_logger(logger_name_detail, "LOG_TestRecords_detail.log")

# logger_name_high_level = "WebSocketPriceUpdaterTester"
# create_logger(logger_name_high_level, "LOG_TestRecords.log")
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

        self.logger = create_logger("ledger", "LOG_HQBrain.log")
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


def run_test_on_existind_data_from_db(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    # config values
    bb45_pct_sample_count = 2
    sma200_pct_sample_count = 2

    # initial_time_stamp = int(time())-3*3600
    # time[s]
    initial_time_stamp = 1636670930-3*3600
    print(f"initial time stamp: {initial_time_stamp}")
    raw_records = DBFunctions.get_records_between_timestamps(initial_time_stamp, initial_time_stamp+14*3600)

    # time [ms]
    df = PandaFunctions.get_df_from_records(raw_records)

    ledger = CoinLedger()
    ledger.bank = 1000
    ledger.coin_value_to_buy = 100

    scenario_logger = create_logger("scenario", "LOG_ScenarioLogger.log")

    trade_price_df = pd.DataFrame({"timeStamp": [], "bought": [], "sold":[]})
    
    # df_5m[["timeStamp"]] = df_5m[["timeStamp"]].astype(np.int64)
    df_bb5mL9 = None
    
    bb_df_1min = pd.DataFrame({"timeStamp": [], "close": [], "BBUpper": [], "BBLower": [], "BBMedian":[]})
    df_1min = pd.DataFrame({"timeStamp": [], "close": []})

    from Helpers.PriceCheckSession import PriceCheckSession
    last_price = 0
    step5min_ms = 300000
    step1min_ms = 60000

    # for record in remaining_records:
    for dx in range(len(df)):
        current_timestamp = df.iloc[dx].name
        tick_df_1sec = df[df.index <= current_timestamp].tail(202)
        current_price = tick_df_1sec.at[current_timestamp, "close"]

        tick_df_1sec["sma50"] = ta.sma(tick_df_1sec.close, length=50)
        tick_df_1sec["sma200"] = ta.sma(tick_df_1sec.close, length=200)

        # PRICE DATA FRAME
        if (current_timestamp % step1min_ms) == 0:
            # ensure added records are on or after 15min mark
            df_1min = df_1min.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)

        # BBANDS DATA FRAME
        if (current_timestamp % step1min_ms) == 0:
            # ensure added records are on or after 15min mark
            if len(bb_df_1min) > 0:
                previous_timestamp = bb_df_1min.tail(1).timeStamp
                if current_timestamp < int(previous_timestamp) + step5min_ms:
                    continue
            
            # cast timestamp to str to prevent auto type assigment to float
            bb_df_1min = bb_df_1min.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)
            df_bb5mL9 = ta.bbands(bb_df_1min.close, length=45)
            
            if df_bb5mL9 is not None:
                bb_df_1min["BBUpper"] = df_bb5mL9["BBU_45_2.0"]
                bb_df_1min["BBLower"] = df_bb5mL9["BBL_45_2.0"]
                bb_df_1min["BBMedian"] = df_bb5mL9["BBM_45_2.0"]
                bb_df_1min["BBUpperPct1"] = bb_df_1min["BBUpper"].pct_change(periods=1)
                bb_df_1min["BBLowerPct1"] = bb_df_1min["BBLower"].pct_change(periods=1)
        
        if df_bb5mL9 is None or np.any(np.isnan(df_bb5mL9.tail(1))) or len(bb_df_1min) < 3:
            continue
        # if pd.isnull(recent_tick_df.at[current_timestamp, "sma200"]):
        #     continue

        # rsi9 = ta.rsi(recent_tick_df.close, 9)
        price_below_bb_median = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBMedian"].tail(1).values[0]
        price_above_bb_median = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBMedian"].tail(1).values[0]
        price_above_bb_lower = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBLower"].tail(1).values[0]
        price_below_bb_lower = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBLower"].tail(1).values[0]
        price_above_bb_upper = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBUpper"].tail(1).values[0]
        price_below_bb_upper = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBUpper"].tail(1).values[0]

        bb_lower_trend_slowing_decrease_trend_pct = bb_df_1min["BBLower"].pct_change(periods=bb45_pct_sample_count).tail(1).values[0]
        bb_upper_trend_slowing_increase_trend_pct = bb_df_1min["BBUpper"].pct_change(periods=bb45_pct_sample_count).tail(1).values[0]

        price_below_sma50 =  tick_df_1sec.at[current_timestamp, "close"] < tick_df_1sec.at[current_timestamp, "sma50"]
        price_above_sma50 =  tick_df_1sec.at[current_timestamp, "close"] > tick_df_1sec.at[current_timestamp, "sma50"]
        price_below_sma200 =  tick_df_1sec.at[current_timestamp, "close"] < tick_df_1sec.at[current_timestamp, "sma200"]
        price_above_sma200 =  tick_df_1sec.at[current_timestamp, "close"] > tick_df_1sec.at[current_timestamp, "sma200"]

        sma200_trend_trend_pct_1sec = tick_df_1sec["sma200"].pct_change(periods=sma200_pct_sample_count).tail(1).values[0] * 1000


        if np.isnan(bb_lower_trend_slowing_decrease_trend_pct) or np.isnan(bb_upper_trend_slowing_increase_trend_pct):
            continue

        if price_below_bb_median:

            # trend is increasing- skip all
            if sma200_trend_trend_pct_1sec > 0 :
                continue
            
            # price between median and lower: check for bb 
            if price_above_bb_lower and bb_lower_trend_slowing_decrease_trend_pct < 0 and abs(bb_lower_trend_slowing_decrease_trend_pct) > 0.0005:
                scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}, bb: {bb_lower_trend_slowing_decrease_trend_pct}")
                #trend decreasing  at high velocity
                continue

            # trend is decreasing, so wait for a better price
            if sma200_trend_trend_pct_1sec < 0 and abs(sma200_trend_trend_pct_1sec) > 0.02:
                continue
            else:
                scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}, sma200: {sma200_trend_trend_pct_1sec}")

            
            
            if price_below_bb_lower:
                if ledger.propose_buy(current_price, current_timestamp):
                    scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}: Bought below lower")
                    trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
                    continue
            # else:
            #     if ledger.propose_buy(current_price, current_timestamp):
            #         scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}: Bought above lower")
            #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
            #         continue




            # if rsi9.iat[-1] < 30:
            #     prep_to_buy = True
            # elif prep_to_buy and ta.decreasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
            #     pass
            # elif prep_to_buy and price_below_sma50:
            #     if ledger.propose_buy(current_price, current_timestamp):
            #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
            #         prep_to_buy = False
        
        if price_above_bb_median:
            # trend is decreasing - skip all

            if price_above_bb_upper:
                if ledger.propose_sell(current_price, current_timestamp, pct=1):
                    scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}: Sold above Upper")
                    trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
                    continue
                
            if sma200_trend_trend_pct_1sec < 0 :
                continue

            if price_below_bb_upper and bb_upper_trend_slowing_increase_trend_pct > 0 and abs(bb_upper_trend_slowing_increase_trend_pct) > 0.0005:
                #trend increasing  at high velocity
                continue
            
            if sma200_trend_trend_pct_1sec > 0.03:
                continue

            if price_above_bb_upper:
                if ledger.propose_sell(current_price, current_timestamp):
                    scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}: Sold above Upper")
                    trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
                    continue
            # else:
            #     if ledger.propose_sell(current_price, current_timestamp):
            #         scenario_logger.info(f"{DateHelper.get_datetime_single_from_ms(current_timestamp)}: Sold below Upper")
            #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
            #         continue




            # if rsi9.iat[-1] > 70:
            #     prep_to_sell = True
            # elif prep_to_sell and ta.increasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
            #     pass
            # elif prep_to_sell and price_above_sma50:
            #     if ledger.propose_sell(current_price, current_timestamp):
            #         prep_to_sell = False
            #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
            
        
    # last_price = data_hq.df.tail(1).close.values[0]

    last_price = tick_df_1sec.tail(1).close.values[0]
    df["sma50"] = ta.sma(df.close, length=50)
    df["sma200"] = ta.sma(df.close, length=200)
    df.to_csv("test_data_output.csv")
    trade_price_df.to_csv("csv_test_data_trades.csv")
    trade_price_df.to_pickle("pikle_price.pkl")
    df_bb5mL9.to_pickle("pikle_df_bb5mL9.pkl")
    

    scenario_logger.info(f"The END: bank_money: {ledger.bank}, coins: {ledger.available_coins}")
    scenario_logger.info(f"With sold stock at most recent price ({last_price}): {last_price*ledger.available_coins+ledger.bank}")
    scenario_logger.info(f"Worth if sold at purchase price: {ledger.sum_of_active_transactions()+ledger.bank}")
    scenario_logger.info(f"All transactions: {len(ledger.transaction_history)}, active_transactions: {len([k for k in ledger.transaction_history if k.active])}")
    scenario_logger.info(f"All open transactions: {[k.coin_value for k in ledger.transaction_history if k.active]}")

    # Plotter.plot_data(df, price_df)
    # df.reset_index(inplace=True)
    df.to_pickle("pickle.pkl")
    bb_df_1min["timeStamp"] = bb_df_1min[["timeStamp"]].astype(np.int64)
    # df_5m["date"] = DateHelper.get_datetime_series(df_5m.timeStamp)
    bb_df_1min.set_index("timeStamp", inplace=True)
    bb_df_1min.to_pickle("df_5m.pkl")
    df_1min["timeStamp"] = df_1min[["timeStamp"]].astype(np.int64)
    df_1min.set_index("timeStamp", inplace=True)
    df_1min.to_pickle("pikle_df_coin_price_1min.pkl")

    mx=df.plot(y="close", c="orange")
    df.plot(y="sma50", c="green", ax=mx)
    df.plot(y="sma200", c="darkblue", ax=mx)
    
    df_1min.plot(y="close", c="red", ax=mx)
    bb_df_1min.plot(y="BBUpper", c="black", ax=mx)
    bb_df_1min.plot(y="BBLower", c="black", ax=mx)
    bb_df_1min.plot(y="BBMedian", c="black", ax=mx)
    ax=trade_price_df.plot.scatter(x="timeStamp", y="bought", c="red", ax=mx)
    for i, txt in enumerate(trade_price_df.bought):
        ax.annotate(txt, (trade_price_df.timeStamp.iat[i], trade_price_df.bought.iat[i]))

    bx=trade_price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
    for i, txt in enumerate(trade_price_df.sold):
        bx.annotate(txt, (trade_price_df.timeStamp.iat[i], trade_price_df.sold.iat[i]))

    # ## bb decreasing
    # bx=price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
    # for i, txt in enumerate(price_df.sold):
    #     bx.annotate(txt, (price_df.timeStamp.iat[i], price_df.sold.iat[i]))
    
    import matplotlib.pyplot as plt
    # plt.savefig("figure.png")
    plt.show()

            
if __name__ == "__main__":
    args = CreateScriptArgs()
    # start_web_socket(args)
    run_test_on_existind_data_from_db(args)