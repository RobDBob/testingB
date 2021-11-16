import pandas_ta as ta

from datetime import datetime, timedelta
import pandas as pd
import json
from Helpers import DateHelper, const

def print_data_types(df):
    print(df.dtypes)

def load_from_json(file_path="output - Copy.json"):
    #return pd.io.json.read_json(file_path)
    return pd.io.json.read_json(file_path)

def convert_to_numeric(df, columns):
    for column in columns:
        df[column] = pd.to_numeric(df[column])
    return df

def readFromList(records):
    return pd.DataFrame().from_records(records)

def saveToFile(results, filePath):
    with open(filePath, "w") as fp:
        json.dump(results, fp)

def get_df_from_records(db_records):
    """
    records in database are stored with timestamp unit: sec instead of milisecs
    need to conver secs to milisecs hence *1000
    """
    db_df = pd.DataFrame().from_records(db_records)
    db_df=db_df.apply(pd.to_numeric)
    db_df.columns=const.columns_to_keep
    db_df.drop(["open", "high", "low"], axis=1, inplace=True)
    
    # keeping df data in ms unit as that's what binance is working of
    db_df.timeStamp = db_df.timeStamp * 1000

    # db_df["dateTime"] = DateHelper.get_datetime_series(db_df.timeStamp)
    db_df.set_index('timeStamp', inplace=True, drop=False)
    db_df.rename(columns={"timeStamp": 'dateTime'}, inplace=True)
    db_df.dateTime = DateHelper.get_datetime_series(db_df.dateTime)
    return db_df

def update_bb_on_15min_mark(df, current_timestamp, current_price):
    if len(df) == 0:
        return None

    previous_timestamp = df.tail(1).timeStamp
    if current_timestamp < int(previous_timestamp) + 900000:
        return None

    df = df.append({"timeStamp": str(current_timestamp), "close": current_price}, ignore_index=True)
    df_bb15mL9 = ta.bbands(df.close, length=9)
    
    if df_bb15mL9 is not None:
        df["BBUpper"] = df_bb15mL9["BBU_9_2.0"]
        df["BBLower"] = df_bb15mL9["BBL_9_2.0"]
        df["BBMedian"] = df_bb15mL9["BBM_9_2.0"]
    return df

# def bb_trend_slowing_decrease_trend(df_bblower):
#     """
#     period 5 appears to be stable
#     """
#     previous_value = df_bblower.pct_change(periods=5).tail(2).values[0]
#     current_value = df_bblower.pct_change(periods=5).tail(2).values[1]
#     if previous_value > previous_value:
#         return False
#     return current_value < 0 and (abs(current_value) > 0 and abs(current_value) < 0.0002)
#     current_value = df_bblower.pct_change(periods=5).tail(2).values[1]