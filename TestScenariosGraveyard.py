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

# long run 17/11/21

# def run_test_on_existind_data_from_db(args):
#     """
#     reads test data from file
#     splits into initial set, and feed set
#     each of feed data is converted:
#     from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
#     """
#     # config values
#     bb45_pct_sample_count = 2
#     sma200_pct_sample_count = 2

#     initial_time_stamp = int(time())-5*24*3600
#     # time[s]
#     # initial_time_stamp = 1636670930-3*3600
#     print(f"initial time stamp: {initial_time_stamp}")
#     raw_records = DBFunctions.get_records_between_timestamps(initial_time_stamp, time()) # initial_time_stamp+14*3600)

#     # time [ms]
#     df = PandaFunctions.get_df_from_records(raw_records)

#     ledger = CoinLedger()
#     ledger.bank = 1000
#     ledger.coin_value_to_buy = 100

#     scenario_logger = create_logger("scenario", "LOG_ScenarioLogger.log")

#     trade_price_df = pd.DataFrame({"timeStamp": [], "bought": [], "sold":[]})
    
#     # df_5m[["timeStamp"]] = df_5m[["timeStamp"]].astype(np.int64)
#     df_bb5mL9 = None
    
#     bb_df_1min = pd.DataFrame({"timeStamp": [], "close": [], "BBUpper": [], "BBLower": [], "BBMedian":[]})
#     df_1min = pd.DataFrame({"timeStamp": [], "close": []})

#     from Helpers.PriceCheckSession import PriceCheckSession
#     last_price = 0
#     step5min_ms = 300000
#     step1min_ms = 60000

#     # for record in remaining_records:
#     for dx in range(len(df)):
#         current_timestamp = df.iloc[dx].name
#         tick_df_1sec = df[df.index <= current_timestamp].tail(202)
#         current_price = tick_df_1sec.at[current_timestamp, "close"]

#         tick_df_1sec["sma50"] = ta.sma(tick_df_1sec.close, length=50)
#         tick_df_1sec["sma200"] = ta.sma(tick_df_1sec.close, length=200)

#         # PRICE DATA FRAME
#         if (current_timestamp % step1min_ms) == 0:
#             # ensure added records are on or after 15min mark
#             df_1min = df_1min.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)

#         # BBANDS DATA FRAME
#         if (current_timestamp % step1min_ms) == 0:
#             # ensure added records are on or after 15min mark
#             if len(bb_df_1min) > 0:
#                 previous_timestamp = bb_df_1min.tail(1).timeStamp
#                 if current_timestamp < int(previous_timestamp) + step5min_ms:
#                     continue
            
#             # cast timestamp to str to prevent auto type assigment to float
#             bb_df_1min = bb_df_1min.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)
#             df_bb5mL9 = ta.bbands(bb_df_1min.close, length=45)
            
#             if df_bb5mL9 is not None:
#                 bb_df_1min["BBUpper"] = df_bb5mL9["BBU_45_2.0"]
#                 bb_df_1min["BBLower"] = df_bb5mL9["BBL_45_2.0"]
#                 bb_df_1min["BBMedian"] = df_bb5mL9["BBM_45_2.0"]
#                 bb_df_1min["BBUpperPct1"] = bb_df_1min["BBUpper"].pct_change(periods=1)
#                 bb_df_1min["BBLowerPct1"] = bb_df_1min["BBLower"].pct_change(periods=1)
        
#         if df_bb5mL9 is None or np.any(np.isnan(df_bb5mL9.tail(1))) or len(bb_df_1min) < 3:
#             continue
#         # if pd.isnull(recent_tick_df.at[current_timestamp, "sma200"]):
#         #     continue

#         # rsi9 = ta.rsi(recent_tick_df.close, 9)
#         price_below_bb_median = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBMedian"].tail(1).values[0]
#         price_above_bb_median = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBMedian"].tail(1).values[0]
#         price_above_bb_lower = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBLower"].tail(1).values[0]
#         price_below_bb_lower = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBLower"].tail(1).values[0]
#         price_above_bb_upper = tick_df_1sec.at[current_timestamp, "close"] > bb_df_1min["BBUpper"].tail(1).values[0]
#         price_below_bb_upper = tick_df_1sec.at[current_timestamp, "close"] < bb_df_1min["BBUpper"].tail(1).values[0]

#         price_below_sma50 =  tick_df_1sec.at[current_timestamp, "close"] < tick_df_1sec.at[current_timestamp, "sma50"]
#         price_above_sma50 =  tick_df_1sec.at[current_timestamp, "close"] > tick_df_1sec.at[current_timestamp, "sma50"]
#         price_below_sma200 =  tick_df_1sec.at[current_timestamp, "close"] < tick_df_1sec.at[current_timestamp, "sma200"]
#         price_above_sma200 =  tick_df_1sec.at[current_timestamp, "close"] > tick_df_1sec.at[current_timestamp, "sma200"]

#         bb_lower_trend_slowing_decrease_trend_pct = bb_df_1min["BBLower"].pct_change(periods=bb45_pct_sample_count).tail(1).values[0] * 1000
#         bb_upper_trend_slowing_increase_trend_pct = bb_df_1min["BBUpper"].pct_change(periods=bb45_pct_sample_count).tail(1).values[0] * 1000
#         sma200_trend_trend_pct_1sec = tick_df_1sec["sma200"].pct_change(periods=sma200_pct_sample_count).tail(1).values[0] * 1000


#         if np.isnan(bb_lower_trend_slowing_decrease_trend_pct) or np.isnan(bb_upper_trend_slowing_increase_trend_pct):
#             continue

#         if price_below_bb_median:
#             human_date = DateHelper.get_datetime_single_from_ms(current_timestamp)
#             if price_below_bb_lower:
#                 if ledger.propose_buy(current_price, current_timestamp):
#                     scenario_logger.info(f"{human_date}: B: below lower: {current_price:1.2f}. sma200: {sma200_trend_trend_pct_1sec}, bb45_lower: {bb_lower_trend_slowing_decrease_trend_pct}")
#                     trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
#                     continue


#             # trend is increasing- skip all
#             if sma200_trend_trend_pct_1sec > 0 :
#                 continue
            
#             # price between median and lower: check for bb 
#             if bb_lower_trend_slowing_decrease_trend_pct < 0 and abs(bb_lower_trend_slowing_decrease_trend_pct) > 0.5:
#                 #trend decreasing  at high velocity
#                 continue

#             # trend is decreasing, so wait for a better price
#             if sma200_trend_trend_pct_1sec < 0 and abs(sma200_trend_trend_pct_1sec) > 0.02:
#                 continue
            
#             # else:
#             #     if ledger.propose_buy(current_price, current_timestamp):
#             #         scenario_logger.info(f"{human_date}: Bought above lower")
#             #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
#             #         continue




#             # if rsi9.iat[-1] < 30:
#             #     prep_to_buy = True
#             # elif prep_to_buy and ta.decreasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
#             #     pass
#             # elif prep_to_buy and price_below_sma50:
#             #     if ledger.propose_buy(current_price, current_timestamp):
#             #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "bought": current_price}, ignore_index=True)
#             #         prep_to_buy = False
        
#         if price_above_bb_median:
#             # trend is decreasing - skip all

#             if price_above_bb_upper:
#                 if ledger.propose_sell(current_price, current_timestamp, pct=1):
#                     scenario_logger.info(f"{human_date}: S: above Upper: {current_price:1.2f}. sma200: {sma200_trend_trend_pct_1sec}, bb_upper: {bb_upper_trend_slowing_increase_trend_pct}")
#                     trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
#                     continue
                
#             if sma200_trend_trend_pct_1sec < 0 :
#                 # scenario_logger.info(f"{human_date}: S: above Upper: {current_price:1.2f}. sma200: {sma200_trend_trend_pct_1sec}, bb_upper: {bb_upper_trend_slowing_increase_trend_pct}")
#                 continue

#             if bb_upper_trend_slowing_increase_trend_pct > 0.5:
#                 #trend increasing  at high velocity
#                 scenario_logger.info(f"{human_date}: SKIP BB (above median): {current_price:1.2f} bb_upper: {bb_upper_trend_slowing_increase_trend_pct}")
#                 continue
            
#             if sma200_trend_trend_pct_1sec > 0.02:
#                 scenario_logger.info(f"{human_date}: SKIP SMA (above median): {current_price:1.2f} sma200 {sma200_trend_trend_pct_1sec}")
#                 continue

#             if ledger.propose_sell(current_price, current_timestamp):
#                 scenario_logger.info(f"{human_date}: S: below Upper: {current_price:1.2f} sma200: {sma200_trend_trend_pct_1sec}, bb_upper: {bb_upper_trend_slowing_increase_trend_pct}")
#                 trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
#                 continue
#             # else:
#             #     if ledger.propose_sell(current_price, current_timestamp):
#             #         scenario_logger.info(f"{human_date}: Sold below Upper")
#             #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
#             #         continue




#             # if rsi9.iat[-1] > 70:
#             #     prep_to_sell = True
#             # elif prep_to_sell and ta.increasing(recent_tick_df.close, length=3, asint=False).iat[-1]:
#             #     pass
#             # elif prep_to_sell and price_above_sma50:
#             #     if ledger.propose_sell(current_price, current_timestamp):
#             #         prep_to_sell = False
#             #         trade_price_df = trade_price_df.append({"timeStamp": current_timestamp, "sold": current_price}, ignore_index=True)
            
        
#     # last_price = data_hq.df.tail(1).close.values[0]

#     last_price = tick_df_1sec.tail(1).close.values[0]
#     df["sma50"] = ta.sma(df.close, length=50)
#     df["sma200"] = ta.sma(df.close, length=200)
#     df.to_csv("test_data_output.csv")
#     trade_price_df.to_csv("csv_test_data_trades.csv")
#     trade_price_df.to_pickle("pikle_price.pkl")
#     df_bb5mL9.to_pickle("pikle_df_bb5mL9.pkl")
    

#     scenario_logger.info(f"The END: bank_money: {ledger.bank}, coins: {ledger.available_coins}")
#     scenario_logger.info(f"With sold stock at most recent price ({last_price}): {last_price*ledger.available_coins+ledger.bank}")
#     scenario_logger.info(f"Worth if sold at purchase price: {ledger.sum_of_active_transactions()+ledger.bank}")
#     scenario_logger.info(f"All transactions: {len(ledger.transaction_history)}, active_transactions: {len([k for k in ledger.transaction_history if k.active])}")
#     scenario_logger.info(f"All open transactions: {[k.coin_value for k in ledger.transaction_history if k.active]}")

#     # Plotter.plot_data(df, price_df)
#     # df.reset_index(inplace=True)
#     df.to_pickle("pickle.pkl")
#     bb_df_1min["timeStamp"] = bb_df_1min[["timeStamp"]].astype(np.int64)
#     # df_5m["date"] = DateHelper.get_datetime_series(df_5m.timeStamp)
#     bb_df_1min.set_index("timeStamp", inplace=True)
#     bb_df_1min.to_pickle("df_5m.pkl")
#     df_1min["timeStamp"] = df_1min[["timeStamp"]].astype(np.int64)
#     df_1min.set_index("timeStamp", inplace=True)
#     df_1min.to_pickle("pikle_df_coin_price_1min.pkl")

#     mx=df.plot(y="close", c="orange")
#     df.plot(y="sma50", c="green", ax=mx)
#     df.plot(y="sma200", c="darkblue", ax=mx)
    
#     df_1min.plot(y="close", c="red", ax=mx)
#     bb_df_1min.plot(y="BBUpper", c="black", ax=mx)
#     bb_df_1min.plot(y="BBLower", c="black", ax=mx)
#     bb_df_1min.plot(y="BBMedian", c="black", ax=mx)
#     ax=trade_price_df.plot.scatter(x="timeStamp", y="bought", c="red", ax=mx)
#     for i, txt in enumerate(trade_price_df.bought):
#         ax.annotate(txt, (trade_price_df.timeStamp.iat[i], trade_price_df.bought.iat[i]))

#     bx=trade_price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
#     for i, txt in enumerate(trade_price_df.sold):
#         bx.annotate(txt, (trade_price_df.timeStamp.iat[i], trade_price_df.sold.iat[i]))

#     # ## bb decreasing
#     # bx=price_df.plot.scatter(x="timeStamp", y="sold", c="green", ax=mx)
#     # for i, txt in enumerate(price_df.sold):
#     #     bx.annotate(txt, (price_df.timeStamp.iat[i], price_df.sold.iat[i]))
    
#     import matplotlib.pyplot as plt
#     # plt.savefig("figure.png")
#     plt.show()
