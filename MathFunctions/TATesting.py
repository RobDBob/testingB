import math
import pandas_ta as ta

def stoch_test(stoch_df, buy=True):
    """
    columns: 
    0: STOCHk_14_3_3    k - GREEN
    1: STOCHd_14_3_3    d - RED
    """
    # K - GREEN
    # D - RED
    if buy:
        low_treshold = 10

        sufficiently_low = stoch_df.iloc[-1][0] < low_treshold and stoch_df.iloc[-1][1] < low_treshold
        green_above = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        green_below = stoch_df.iloc[-1][0] > stoch_df.iloc[-1][1]

        print(f"stoch_test: BUY: sufficiently_low:{sufficiently_low}; green_below:{green_below}; green_above:{green_above}")
        return sufficiently_low and green_above and green_below

    if not buy: # aka sell
        high_treshold = 90

        sufficiently_high = stoch_df.iloc[-1][0] > high_treshold and stoch_df.iloc[-1][1] > high_treshold
        green_below = stoch_df.iloc[-2][0] < stoch_df.iloc[-2][1]
        green_above = stoch_df.iloc[-1][0] > stoch_df.iloc[-1][1]

        print(f"stoch_test: SELL: sufficiently_high:{sufficiently_high}; green_below:{green_below}; green_above:{green_above}")
        return sufficiently_high and green_below and green_above

def bb_test(df, buy=True):
    bb_df = ta.bbands(df["close"], length=18, std=2)
    # check where price touches and trend
    # iloc[-1, ] 
    # column indexes: 0:BBLow, 1:BBMedian, 2:BBUpper, 3:BBBandwidth, 4:BBPercent
    last_close_value = df.loc[df.index[-1], "close"]

    if buy:
        price_below_median = last_close_value < bb_df.iloc[-1][1]
        price_distance_to_lower = math.isclose(last_close_value, bb_df.iloc[-1][0], abs_tol=last_close_value/1000)
        price_is_lower = last_close_value < bb_df.iloc[-1][0]
        
        print(f"bb_test: BUY: price_below_median:{price_below_median}; price_distance_to_lower:{price_distance_to_lower}; price_is_lower:{price_is_lower}")
        return price_below_median and (price_distance_to_lower or price_is_lower)

    if not buy: #aka sell
        price_above_median = last_close_value > bb_df.iloc[-1][1]
        price_distance_to_upper = math.isclose(last_close_value, bb_df.iloc[-1][2], abs_tol=last_close_value/1000)
        price_is_higher = last_close_value > bb_df.iloc[-1][2]
        
        print(f"bb_test: SELL: price_above_median:{price_above_median}; price_distance_to_upper:{price_distance_to_upper}; price_is_higher:{price_is_higher}")
        return price_above_median and (price_distance_to_upper or price_is_higher)

def rsi_test(rsi_df, buy=True):
    if buy:
        below = rsi_df.iloc[-1] < 30
        
        print(f"rsi_test: BUY: below: {below}")
        return below
    
    if not buy: # aka sell
        above = rsi_df.iloc[-1] > 70
        
        print(f"rsi_test: SELL: above: {above}")
        return above