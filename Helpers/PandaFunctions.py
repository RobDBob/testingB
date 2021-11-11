
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

def get_df_from_db_records(db_records):
    """
    records in database are stored with timestamp unit: sec instead of milisecs
    need to conver secs to milisecs hence *1000
    """
    db_df = pd.DataFrame().from_records(db_records)
    db_df=db_df.apply(pd.to_numeric)
    db_df.columns=const.columns_to_keep
    db_df.timeStamp = db_df.timeStamp * 1000
    db_df.set_index('timeStamp', inplace=True, drop=False)
    db_df.rename(columns={"timeStamp": 'dateTime'}, inplace=True)
    db_df.dateTime = DateHelper.get_datetime_series(db_df.dateTime)
    return db_df