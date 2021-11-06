from MathFunctions.TATesting import TATester
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

