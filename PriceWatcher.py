import pandas_ta as ta
from Helpers import const

class PriceWatcher:
    def __init__(self, df, logger) -> None:
        self.df = df
        self.logger = logger
        self.monitored_trend = []
        self.log_flag_monitor_price = False

    def recalculate_rsi(self):
        rsi = ta.rsi(self.df["close"], length=12)
        rsi_test_result = self.data_holder.taTester.rsi_test(rsi)
        self.logger.info(f"RSI: {rsi_test_result}")
        return rsi_test_result

    def recalculate_stoch(self):
        stoch = ta.stoch(self.df["high"], self.df["low"], self.df["close"])
        stoch_test_result = self.data_holder.taTester.stoch_test(stoch)
        self.logger.info(f"STOCH: {stoch_test_result}")
        return stoch_test_result

    def recalculate_conditions(self):
        # controlling flags:
        recent_prices = self.df.tail(2)["close"].values # order index 1: most recent
        self.monitored_trend.append(recent_prices[0] < recent_prices[1])

        if len(set(self.monitored_trend)) == 1: # set cannot have duplicates, so 1 for all elements being same
            # same trend, carry on
            return True
        else:
            # trend changed, hard stop to evaluate other tests
            results = [self.recalculate_rsi()] # self.recalculate_stoch(), 

            if len(set(results)) == 1 and const.TransactionType.other not in results:
                # log_strong_action.info(f"Action: {rsi_test_result}, Price: {self.data_updater.df.close.tail(1).values[0]}")
                self.logger.info(f"{self.data_holder.current_datetime}: SOLID _____________________ , Price: {recent_prices[1]}")
            # else:
            #     self.logger.info(f"{self.data_holder.current_datetime}: Action: {rsi_test_result}, Price: {recent_prices[0]}; rsi:{rsi_test_result}, sto:{stoch_test_result}")

            self.monitored_trend.clear()
            return False

    def scenario_some_profit(self, session_open):
        if session_open.initial_trend_increasing is None:
            # if rsi_value < 30 and ta.increasing(ta.sma(data_hq.df.close, length=21), asint=False).tail(1).values[0] == False:
            # rsi_value
            df_sma = ta.sma(self.df.close, length=9)
            session_open.initial_trend_increasing = ta.increasing(df_sma, length=4, asint=False).tail(1).values[0]

        # check if trend continues
        # check if trend is increasing over last 3 values for sma length = 21
        df_sma = ta.sma(self.df.close, length=9)
        updated_trend = ta.increasing(df_sma, length=4, asint=False).tail(1).values[0]
        if len({session_open.initial_trend_increasing, updated_trend}) == 1:
            return False

        else: # change of trend - ACTION TIME
            return True

    def simple(self):
        return 