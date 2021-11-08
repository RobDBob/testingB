from datetime import datetime
from Helpers import const
import pandas as pd


def get_datetime_single_from_ms(date_time_stamp_ms):
    return datetime.utcfromtimestamp((int(date_time_stamp_ms)/1000)).strftime(const.date_time_format)

def get_datetime_series(date_time_stamps_ms):
    # print(f"---- type: {type(date_time_stamps_ms)}, value: {date_time_stamps_ms}")
    return pd.to_datetime(date_time_stamps_ms, unit='ms').dt.strftime(const.date_time_format)