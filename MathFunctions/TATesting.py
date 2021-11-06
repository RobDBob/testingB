import math
import pandas_ta as ta
from Helpers.const import TA

class TATester:
    def __init__(self, logger) -> None:
        self.logger = logger

    def _set_return_code(self, buy_test, sell_test):
        if buy_test:
            return TA.buy
        if sell_test:
            return TA.sell
        return TA.other

    def stoch_test(self, stoch_df):
        """
        columns: 
        0: STOCHk_14_3_3    k - GREEN
        1: STOCHd_14_3_3    d - RED
        """
        buy_treshold = 10
        k_line = stoch_df.iloc[-1][0]
        d_line = stoch_df.iloc[-1][1]

        sufficiently_low = k_line < buy_treshold and d_line < buy_treshold
        # green_above = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        # k_below_d = k_line > d_line
        d_below_k = k_line > d_line

        self.logger.info(f"stoch_test: BUY: sufficiently_low:{sufficiently_low}; d_below_k:{d_below_k}")
        buy = sufficiently_low and d_below_k

        sell_treshold = 90
        sufficiently_high = k_line > sell_treshold and d_line > sell_treshold
        # k_below_d = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        # green_above = k_line > d_line
        k_below_d = k_line < d_line

        self.logger.info(f"stoch_test: SELL: sufficiently_high:{sufficiently_high}; k_below_d:{k_below_d}")
        sell = sufficiently_high and k_below_d

        return self._set_return_code(buy, sell)

    def bb_test(self, bb_df, last_close_value):
        """
            BBL: lower     -1 
            BBM: mid       -2 
            BBU: upper     -3
            BBW: bandwidth -4
            BBP: percent   -5 

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
        """
            plot line, most recent value: index -1
        """
        buy = rsi_df.iloc[-1] < 30
        sell = rsi_df.iloc[-1] > 70

        if buy:
            self.logger.info(f"rsi test. BUY. value: {rsi_df.iloc[-1]}")
        if sell:
            self.logger.info(f"rsi test. SELL. value: {rsi_df.iloc[-1]}")

        return self._set_return_code(buy, sell)

    def macd_test(self, macd_df):
        """
        MACDAS_12_26_9  MACDASh_12_26_9  MACDASs_12_26_9  MACDASh_12_26_9_XA_0  MACDASh_12_26_9_XB_0  MACDAS_12_26_9_A_0
        """
        buy = False
        sell = False
        return self._set_return_code(buy, sell)