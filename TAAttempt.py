from main1dbstuff import saveToFile, readFromFile
import pandas as pd
import pandas_ta as ta
from CleanFunctions import ToKeep


def test1():
    df = pd.read_json("filepath")
    # df["sma3"] = ta.sma(df["lastPrice"], length=3)
    # df["sma6"] = ta.sma(df["lastPrice"], length=6)
    df["sma12"] = ta.sma(df["lastPrice"], length=12)
    df["rsi12"] = ta.rsi(df["lastPrice"], length=12)
    
    print(df.tail(50))

def do_some_trades():
    import json
    records = ToKeep.get_last_records(minutesBack=60)
    dict_records =  {k['closeTime']:k for k in records}
    # clean_dictionary(records)
    # df = pd.read_json(path_or_buf=json.dumps(records), index=["closeTime"], exclude=["_rid", "_self"])
    df = pd.DataFrame.from_records(records, index=["closeTime"], exclude=columns_to_exclude)

    # df = pd.DataFrame.from_dict(dict_records, orient='index')
    print(df)

    df["sma12"] = ta.sma(df["lastPrice"], length=12)
    # df["rsi12"] = ta.rsi(df["lastPrice"], length=12)
    print(df)

def get_updated_date():
    import json
    records = ToKeep.get_last_records(minutesBack=60)
    saveToFile(records, "temp.json")
    df = pd.read_json("temp.json")

    [df.drop(k, axis=1, inplace=True) for k in columns_to_exclude]
    df.set_index(["closeTime"], inplace=True)

    df["sma12"] = ta.sma(df["lastPrice"], length=12)
    df["rsi12"] = ta.rsi(df["lastPrice"], length=12)
    print(df)


if __name__ == "__main__":
    get_updated_date()