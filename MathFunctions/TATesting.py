import math
import pandas_ta as ta
import logging
from Helpers.const import TradeAction

class TATester:
    def __init__(self, logger_name) -> None:
        self.logger = logging.getLogger(logger_name)

    def _set_return_code(self, buy_test, sell_test):
        if buy_test:
            return TradeAction.buy
        if sell_test:
            return TradeAction.sell
        return TradeAction.other

    def stoch_test(self, stoch_df):
        """
        columns: 
        0: STOCHk_14_3_3    k - GREEN
        1: STOCHd_14_3_3    d - RED
        """
        low_treshold = 10

        sufficiently_low = stoch_df.iloc[-1][0] < low_treshold and stoch_df.iloc[-1][1] < low_treshold
        # green_above = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        # green_below = stoch_df.iloc[-1][0] > stoch_df.iloc[-1][1]
        red_below = stoch_df.iloc[-1][0] > stoch_df.iloc[-1][1]

        self.logger.info(f"stoch_test: BUY: sufficiently_low:{sufficiently_low}; red_below:{red_below}")
        buy = sufficiently_low and red_below

        high_treshold = 90

        sufficiently_high = stoch_df.iloc[-1][0] > high_treshold and stoch_df.iloc[-1][1] > high_treshold
        # green_below = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        # green_above = stoch_df.iloc[-1][0] > stoch_df.iloc[-1][1]
        green_below = stoch_df.iloc[-1][0] < stoch_df.iloc[-1][1]

        self.logger.info(f"stoch_test: SELL: sufficiently_high:{sufficiently_high}; green_below:{green_below}")
        sell = sufficiently_high and green_below

        return self._set_return_code(buy, sell)

    def bb_test(self, bb_df, last_close_value):
        """
            BBL: lower
            BBM: mid
            BBU: upper
            BBW: bandwidth
            BBP: percent

            %b - shows where price is in relation to the bands. %b equals 1 at the upper band and 0 at the lower band
        """
        price_below_median = last_close_value < bb_df.iloc[-1][1]
        price_distance_to_lower = math.isclose(last_close_value, bb_df.iloc[-1][0], abs_tol=last_close_value/1000)
        price_is_lower = last_close_value < bb_df.iloc[-1][0]
        
        self.logger.info(f"bb_test: BUY: price_below_median:{price_below_median}; price_distance_to_lower:{price_distance_to_lower}; price_is_lower:{price_is_lower}")
        buy = price_below_median and (price_distance_to_lower or price_is_lower)

        price_above_median = last_close_value > bb_df.iloc[-1][1]
        price_distance_to_upper = math.isclose(last_close_value, bb_df.iloc[-1][2], abs_tol=last_close_value/1000)
        price_is_higher = last_close_value > bb_df.iloc[-1][2]
        
        self.logger.info(f"bb_test: SELL: price_above_median:{price_above_median}; price_distance_to_upper:{price_distance_to_upper}; price_is_higher:{price_is_higher}")
        sell = price_above_median and (price_distance_to_upper or price_is_higher)

        return self._set_return_code(buy, sell)

    def rsi_test(self, rsi_df):
        buy = rsi_df.iloc[-1] < 30
        sell = rsi_df.iloc[-1] > 70
        
        self.logger.info(f"rsi_test: BUY: below: {buy}")
        self.logger.info(f"rsi_test: SELL: above: {sell}")

        return self._set_return_code(buy, sell)