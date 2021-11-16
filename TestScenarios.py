from TAAnalysis.TATesting import TATester
import pandas_ta as ta
from GetLogger import create_logger
from Helpers import const

def data_test_1(taTester: TATester, df):
    """
    returns a list of individual test results with suggested trade action: [const.TA, TA]
    
    """
    test_result = []
    rsi = ta.rsi(df["close"], length=12)
    test_result.append(taTester.rsi_test(rsi))

    stoch = ta.stoch(df["high"], df["low"], df["close"])
    test_result.append(taTester.stoch_test(stoch, buy=True))

    bb = ta.bbands(df["close"], length=18, std=2)
    # check where price touches and trend
    # iloc[-1, ] 
    # column indexes: 0:BBLow, 1:BBMedian, 2:BBUpper, 3:BBBandwidth, 4:BBPercent
    last_close_value = df.loc[df.index[-1], "close"]
    test_result.append(taTester.bb_test(bb, last_close_value, buy=True))
    
    return test_result

# 2021-11-12 16:22:22,046(INFO): The END: bank_money: 13.626566456607534, coins: 0.01472077367644134, last price recorded: 63209.12
# 2021-11-12 16:22:22,046(INFO): Potential worth (with potential loss): 944.1137162636294
# breaking even
# def test_scenario_2():
#     if data_hq.update_data_on_tick(new_df):
#         # monitor_price = signal_trigger.check_rsi()

#         if session_open is None:
#             # monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode() or signal_trigger.check_rsi()
#             # monitor_price = signal_trigger.check_rsi()
#             rsi = ta.rsi(data_hq.df["close"], length=12)
#             rsi_value = rsi.tail(1).values[0]
#             monitor_price = rsi_value < 30 or rsi_value > 70
        
        
#     # monitor price on PER TICK basis dummy!
#     if monitor_price:
#         current_time_stamp = new_df.iloc[0].name
#         recent_tick_df = ndf[ndf.index <= current_time_stamp].tail(50)
#         current_price = recent_tick_df.at[current_time_stamp, "close"]
        
#         if session_open is None:
#             session_open = PriceCheckSession(logger, new_df.iloc[0].dateTime)


#         if rsi_value < 30:
#             if ta.decreasing(recent_tick_df.close, length=7, asint=False).iat[-1]:
#                 continue
#             elif ledger.propose_buy(current_price, current_time_stamp):
#                 price_df = price_df.append({"timeStamp": current_time_stamp, "bought": current_price}, ignore_index=True)
            
#             # closing session as there might be insufficient bank state
#             session_open.session_to_close()
#             session_open = None
#             monitor_price= False

#         if rsi_value > 70:
#             if ta.increasing(recent_tick_df.close, length=7, asint=False).iat[-1]:
#                 continue
#             elif ledger.propose_sell(current_price, current_time_stamp):
#                 price_df = price_df.append({"timeStamp": current_time_stamp, "sold": current_price}, ignore_index=True)

#             # closing session as there might be insufficient bank state
#             session_open.session_to_close()
#             session_open = None
#             monitor_price= False


# def run_test_on_existind_data_from_db(args):
#     """
#     reads test data from file
#     splits into initial set, and feed set
#     each of feed data is converted:
#     from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
#     """
#     initial_time_stamp = int(time())-12*3600

#     first_hour_records = DBFunctions.get_records_between_timestamps(initial_time_stamp, initial_time_stamp+3600)
#     remaining_raw_records = DBFunctions.get_records_after_timestamp(initial_time_stamp+3600)

#     # get first hour records on 1min interval
#     iterval_seconds = int(helpers.interval_to_milliseconds(args.interval)/1000)
#     first_hour_records_w_interval = [k for k in first_hour_records if not k[0] % iterval_seconds]
#     print(len(first_hour_records_w_interval))

#     idf = PandaFunctions.get_df_from_db_records(first_hour_records_w_interval) # initial df
#     ndf = PandaFunctions.get_df_from_db_records(remaining_raw_records) # next df

#     logger = create_logger("DataTest2", "LOG_Scenario_price_check_from_db.log")
#     data_hq = HQBrain(kline_interval=args.interval, historic_data=idf, logger=logger)

#     monitor_price = False
    
#     ledger = CoinLedger(logger)
#     ledger.bank = 1000
#     ledger.coin_value_to_buy = 50
#     price_df = pd.DataFrame({"timeStamp": [], "bought": [], "sold":[]})

#     from Helpers.PriceCheckSession import PriceCheckSession
#     session_open = None
#     rsi_value = None

#     last_price = 0

#     # for record in remaining_records:
#     for dx in range(len(ndf)):
#         new_df = ndf.iloc[[dx]]

#         if dx < 60:
#             continue

#         # if data_hq.update_data_on_tick(new_df):
#         #     # monitor_price = signal_trigger.check_rsi()

#         #     if session_open is None:
#         #         # monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode() or signal_trigger.check_rsi()
#         #         # monitor_price = signal_trigger.check_rsi()
#         #         rsi = ta.rsi(data_hq.df["close"], length=12)
#         #         rsi_value = rsi.tail(1).values[0]
#         #         monitor_price = rsi_value < 30 or rsi_value > 70
            
#         current_time_stamp = new_df.iloc[0].name
#         recent_tick_df = ndf[ndf.index <= current_time_stamp].tail(50)

#         if session_open is None:
#             # monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode() or signal_trigger.check_rsi()
#             # monitor_price = signal_trigger.check_rsi()
#             rsi = ta.rsi(recent_tick_df.close, length=12)
#             rsi_value = rsi.tail(1).values[0]
#             monitor_price = rsi_value < 20 or rsi_value > 80
            
#         # monitor price on PER TICK basis dummy!
#         if monitor_price:
#             current_time_stamp = new_df.iloc[0].name
#             recent_tick_df = ndf[ndf.index <= current_time_stamp].tail(50)
#             current_price = recent_tick_df.at[current_time_stamp, "close"]
            
#             if session_open is None:
#                 session_open = PriceCheckSession(logger, new_df.iloc[0].dateTime)
            
#             ema12 = ta.ema(recent_tick_df.close, length=6)

#             if rsi_value < 20:
#                 if ta.decreasing(ema12, length=3, asint=False).iat[-1]:
#                     continue
#                 elif ledger.propose_buy(current_price, current_time_stamp):
#                     price_df = price_df.append({"timeStamp": current_time_stamp, "bought": current_price}, ignore_index=True)
                
#                 # closing session as there might be insufficient bank state
#                 session_open.session_to_close()
#                 session_open = None
#                 monitor_price= False

#             if rsi_value > 50:
#                 if ta.increasing(ema12, length=3, asint=False).iat[-1]:
#                     continue
#                 elif ledger.propose_sell(current_price, current_time_stamp):
#                     price_df = price_df.append({"timeStamp": current_time_stamp, "sold": current_price}, ignore_index=True)

#                 # closing session as there might be insufficient bank state
#                 session_open.session_to_close()
#                 session_open = None
#                 monitor_price= False
        
#     # last_price = data_hq.df.tail(1).close.values[0]
    
#     # data_hq.df["sma21"] = ta.sma(data_hq.df.close, length=21)
#     # data_hq.df["sma9"] = ta.sma(data_hq.df.close, length=9)
#     # data_hq.df["rsi12"] = ta.rsi(data_hq.df.close, length=12)
#     # data_hq.df.to_csv("test_data_output.csv")
#     # price_df.to_csv("test_data_trades.csv")
#     last_price = data_hq.df.tail(1).close.values[0]
    
#     # data_hq.df["sma21"] = ta.sma(data_hq.df.close, length=21)
#     # data_hq.df["sma9"] = ta.sma(data_hq.df.close, length=9)
#     # data_hq.df["rsi12"] = ta.rsi(data_hq.df.close, length=12)
#     # data_hq.df.to_csv("test_data_output.csv")
#     # price_df.to_csv("test_data_trades.csv")

#     logger.info(f"The END: bank_money: {ledger.bank}, coins: {ledger.available_coins}")
#     logger.info(f"With sold stock at most recent price ({last_price}): {last_price*ledger.available_coins+ledger.bank}")
#     logger.info(f"Actual worth (without loss): {ledger.sum_of_active_transactions()+ledger.bank}")
#     logger.info(f"All transactions: {len(ledger.transaction_history)}, active_transactions: {len([k for k in ledger.transaction_history if k.active])}")
#     logger.info(f"All open transactions: {[k.coin_value for k in ledger.transaction_history if k.active]}")

            

# # for record in remaining_records:
# for dx in range(len(df)):
    
#     if dx < 60:
#         continue

#     current_timestamp = df.iloc[dx].name    
#     current_datetime = df.iloc[dx].dateTime
#     recent_tick_df = df[df.index <= current_timestamp].tail(50)

#     if session_open is None:
#         # monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode() or signal_trigger.check_rsi()
#         # monitor_price = signal_trigger.check_rsi()
#         rsi = ta.rsi(recent_tick_df.close, length=12)
#         rsi_value = rsi.tail(1).values[0]
#         monitor_price = rsi_value < 20 or rsi_value > 80
        
#     # monitor price on PER TICK basis dummy!
#     if monitor_price:
#         recent_tick_df = df[df.index <= current_timestamp].tail(50)
#         current_price = recent_tick_df.at[current_timestamp, "close"]
        
#         if session_open is None:
#             session_open = PriceCheckSession(logger, current_datetime)
        
#         ema12 = ta.ema(recent_tick_df.close, length=12)

#         if rsi_value < 20:
#             if ta.decreasing(ema12, length=3, asint=False).iat[-1]:
#                 continue
#             elif ledger.propose_buy(current_price, current_timestamp):
#                 price_df = price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
            
#             # closing session as there might be insufficient bank state
#             session_open.session_to_close()
#             session_open = None
#             monitor_price= False

#         if rsi_value > 50:
#             if ta.increasing(ema12, length=3, asint=False).iat[-1]:
#                 continue
#             elif ledger.propose_sell(current_price, current_timestamp):
#                 price_df = price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)

#             # closing session as there might be insufficient bank state
#             session_open.session_to_close()
#             session_open = None
#             monitor_price= False




    # for dx in range(len(df)):
        
    #     if dx < 60:
    #         continue

    #     current_timestamp = df.iloc[dx].name    
    #     recent_tick_df = df[df.index <= current_timestamp].tail(50)

    #     rsi = ta.rsi(recent_tick_df.close, length=21)
    #     rsi_value = rsi.tail(1).values[0]
            
    #     # monitor price on PER TICK basis dummy!
    #     recent_tick_df = df[df.index <= current_timestamp].tail(50)
    #     current_price = recent_tick_df.at[current_timestamp, "close"]
        
    #     ema12 = ta.ema(recent_tick_df.close, length=12)

    #     if rsi_value < 30 or prep_to_buy:
    #         if ta.decreasing(ema12, length=3, asint=False).iat[-1]:
    #             prep_to_buy = True
    #             continue
    #         elif ledger.propose_buy(current_price, current_timestamp):
    #             price_df = price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
    #             prep_to_buy = False
            
    #         # closing session as there might be insufficient bank state

    #     if rsi_value > 70 or prep_to_sell:
    #         if ta.increasing(ema12, length=3, asint=False).iat[-1]:
    #             prep_to_sell = True
    #             continue
    #         elif ledger.propose_sell(current_price, current_timestamp):
    #             prep_to_sell = False
    #             price_df = price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)

class baseScenario:
    
    pass

class Scenario1(baseScenario):
    pass