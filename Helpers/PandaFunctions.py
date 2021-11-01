
from datetime import datetime, timedelta
import pandas as pd
import json
from Helpers import const

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

def saveToFileCSV(results, filePath):
    """
    Save data in TA format
    `Timestamp`, `Open`, `High`, `Low`, `Close` and `Volume` columns.
    """
    import csv
    with open(filePath, "w", newline='') as fp:
        csvriter = csv.writer(fp, delimiter=',')
        csvriter.writerow(["Timestamp","DateTime","Open","High","Low","Close"])
        for record in results:
            csvriter.writerow([
                record["id"],
                datetime.utcfromtimestamp((int(record["id"])/1000)+3600).strftime('%Y-%m-%d %H:%M:%S'),
                record["openPrice"],
                record["highPrice"],
                record["lowPrice"],
                record["lastPrice"]])


def getHistoricalData(client, symbol, howLongMinutes, kline_interval):
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.utcnow()
    sinceThisDate = untilThisDate - timedelta(minutes = howLongMinutes)
    # Execute the query from binance - timestamps must be converted to strings !
    candles = client.get_historical_klines(symbol, kline_interval, str(sinceThisDate), str(untilThisDate))
    
    # df = rewrite_data_cleanup(candle)
    df = pd.DataFrame().from_records(candles)
    df.columns = const.all_columns
    
    # # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.set_index('dateTime', drop=False, inplace=True)
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(const.date_time_format)

    # Get rid of columns we do not need
    df = df.drop(const.columns_to_drop, axis=1)
    df = convert_to_numeric(df, ['open', 'high', 'low', 'close', 'volume'])
    
    return df