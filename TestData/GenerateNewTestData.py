import pandas_ta as ta
from binance import helpers
from binance import helpers
from Helpers import PandaFunctions, DBFunctions 


def generate_from_db(save_to_csv_filename=None, start_timestamp=0, interval="1m"):
    """
    generate test data for comparing results

    get df with interval matching data (i.e. ever 1min)
    get websocket like data with random interval (i.e. secs between requests)

    calculate interval data technical analysis
    join with websocket data 
    save to CSV file

    """
    interval_seconds = int(helpers.interval_to_milliseconds(interval)/1000)

    raw_records = DBFunctions.get_records_after_timestamp(start_timestamp)

    all_df_wo_interval = PandaFunctions.get_df_from_db_records(raw_records)

    all_records_with_interval = [k for k in raw_records if not k[0] % interval_seconds]
    all_df_with_interval = PandaFunctions.get_df_from_db_records(all_records_with_interval)
    # all_df_with_interval = all_df_with_interval.join(ta.rsi(all_df_with_interval["close"], length=12))
    # all_df_with_interval = all_df_with_interval.join(ta.bbands(all_df_with_interval["volume"], length=18, std=2))
    # all_df_with_interval = all_df_with_interval.join(ta.macd(all_df_with_interval["close"], signal_indicators=True, asmode=True))

    df=all_df_wo_interval.join(all_df_with_interval, rsuffix="to_drop")
    columns_to_drop = [column for column in df.columns if "to_drop" in column]
    df.drop(columns_to_drop, axis=1, inplace=True)
    # df.drop(["high","low", "open"], axis=1, inplace=True)

    if save_to_csv_filename:
        df.to_csv(save_to_csv_filename, float_format='%.3f')
    return df
