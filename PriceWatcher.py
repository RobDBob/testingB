from MathFunctions.TATesting import TATester
import pandas_ta as ta
from GetLogger import create_logger
from Helpers import const
from newAttempt import HQBrain

class PriceWatcher:
    def __init__(self, data_holder: HQBrain, logger) -> None:
        self.data_holder = data_holder
        self.logger = logger
        self.monitored_trend = []
        self.log_flag_monitor_price = False

    def recalculate_rsi(self):
        rsi = ta.rsi(self.data_holder.df["close"], length=12)
        rsi_test_result = self.data_holder.taTester.rsi_test(rsi)
        self.logger.info(f"RSI: {rsi_test_result}")
        return rsi_test_result

    def recalculate_stoch(self):
        stoch = ta.stoch(self.data_holder.df["high"], self.data_holder.df["low"], self.data_holder.df["close"])
        stoch_test_result = self.data_holder.taTester.stoch_test(stoch)
        self.logger.info(f"STOCH: {stoch_test_result}")
        return stoch_test_result

    def recalculate_conditions(self):
        # controlling flags:
        recent_prices = self.data_holder.df.tail(2)["close"].values # order index 1: most recent
        self.monitored_trend.append(recent_prices[0] < recent_prices[1])

        if len(set(self.monitored_trend)) == 1: # set cannot have duplicates, so 1 for all elements being same
            # same trend, carry on
            return True
        else:
            # trend changed, hard stop to evaluate other tests
            results = [self.recalculate_rsi()] # self.recalculate_stoch(), 

            if len(set(results)) == 1 and const.TA.other not in results:
                # log_strong_action.info(f"Action: {rsi_test_result}, Price: {self.data_updater.df.close.tail(1).values[0]}")
                self.logger.info(f"{self.data_holder.current_datetime}: SOLID _____________________ , Price: {recent_prices[1]}")
            # else:
            #     self.logger.info(f"{self.data_holder.current_datetime}: Action: {rsi_test_result}, Price: {recent_prices[0]}; rsi:{rsi_test_result}, sto:{stoch_test_result}")

            self.monitored_trend.clear()
            return False