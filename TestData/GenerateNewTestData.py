import pandas_ta as ta
from binance import helpers
from binance import helpers
from Helpers import PandaFunctions, DBFunctions 


def generate_from_db(interval="1m", save_to_csv_filename=None, start_timestamp=0):
    """
    generate test data for comparing results

    get df with interval matching data (i.e. ever 1min)
    get websocket like data with random interval (i.e. secs between requests)

    calculate interval data technical analysis
    join with websocket data 
    save to CSV file

    --== do not delete, needed for visual verification ==--

    all_records_1m_interval = [k for k in first_hour_records+remaining_records if not k[0]%60]
    adf = pd.DataFrame().from_records(all_records_1m_interval)
    >>> adf=adf.apply(pd.to_numeric)
    >>> adf.columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'numberOfTrades']
    >>> adf.dateTime = adf.dateTime * 1000
    >>> adf.set_index('dateTime', inplace=True, drop=False)
    >>> adf.dateTime = DateHelper.get_datetime_series(adf.dateTime)

    bbvol_df = ta.bbands(adf["volume"], length=18, std=2)
    macd_df = ta.macd(adf.close, signal_indicators=True, asmode=True)
    rsi = ta.rsi(adf["close"], length=12)
    df=adf.join(rsi)
    df=df.join(macd_df)
    df=df.join(bbvol_df)

    >>> df.index.name=None
    >>> ndf.index.name=None

        >>> jdf=ndf.join(df, rsuffix='r')
        >>> jdf.to_csv("joined.csv")
    """
    interval_seconds = int(helpers.interval_to_milliseconds(interval)/1000)

    raw_records = DBFunctions.get_records_after_timestamp(start_timestamp)

    all_df_wo_interval = PandaFunctions.get_df_from_db_records(raw_records)

    all_records_with_interval = [k for k in raw_records if not k[0] % interval_seconds]
    all_df_with_interval = PandaFunctions.get_df_from_db_records(all_records_with_interval)
    all_df_with_interval = all_df_with_interval.join(ta.rsi(all_df_with_interval["close"], length=12))
    all_df_with_interval = all_df_with_interval.join(ta.bbands(all_df_with_interval["volume"], length=18, std=2))
    all_df_with_interval = all_df_with_interval.join(ta.macd(all_df_with_interval["close"], signal_indicators=True, asmode=True))

    df=all_df_wo_interval.join(all_df_with_interval, rsuffix="to_drop")
    columns_to_drop = [column for column in df.columns if "to_drop" in column]
    df.drop(columns_to_drop, axis=1, inplace=True)
    df.drop(["high","low", "open"], axis=1, inplace=True)

    if save_to_csv_filename:
        df.to_csv(save_to_csv_filename, float_format='%.3f')
    return df
