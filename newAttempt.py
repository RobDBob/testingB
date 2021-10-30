from binance import ThreadedWebsocketManager
from Playground.bFinanceAPIFunctions import getClient
import os
from binance.client import Client
import pandas as pd
import datetime, time
import pandas_ta as ta
from main1dbstuff import saveToFile, readFromFile

class test:
    all_columns = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
    columns_to_drop = ['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore']

    # ['dateTime', 'open', 'high', 'low', 'close', 'volume']
    columns_to_keep = ['dateTime', 'open', 'high', 'low', 'close', 'volume']

    date_time_format = '%Y-%m-%d %H:%M:%S'
    symbol = "BTCUSDT"

    def __init__(self, minutes):
        self.df = self.getHistoricalData(minutes)

    def _get_df_from_candle(self, candle):
        """
        Save and read from json, clean up data
        to investigate why this is needed
        """
        temp_file_name = "candle.json"
        saveToFile(candle, temp_file_name)
        return pd.read_json(temp_file_name)
    
    def _get_datetime_series(self, date_time_stamps_ms):
        # print(f"---- type: {type(date_time_stamps_ms)}, value: {date_time_stamps_ms}")
        return pd.to_datetime(date_time_stamps_ms, unit='ms').dt.strftime(self.date_time_format)

    def _get_datetime_single(self, date_time_stamp_ms):
        return datetime.datetime.utcfromtimestamp((int(date_time_stamp_ms)/1000)).strftime(self.date_time_format)

    def getHistoricalData(self, howLongMinutes):
        client = getClient()
        # Calculate the timestamps for the binance api function
        untilThisDate = datetime.datetime.utcnow()
        sinceThisDate = untilThisDate - datetime.timedelta(minutes = howLongMinutes)
        # Execute the query from binance - timestamps must be converted to strings !
        candle = client.get_historical_klines(self.symbol, Client.KLINE_INTERVAL_3MINUTE, str(sinceThisDate), str(untilThisDate))
        
        df = self._get_df_from_candle(candle)
        df.columns = self.all_columns

        
        # # as timestamp is returned in ms, let us convert this back to proper timestamps.
        df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(self.date_time_format) # self._get_datetime_series(df.dateTime)
        df.set_index('dateTime', inplace=True)

        # Get rid of columns we do not need
        df = df.drop(self.columns_to_drop, axis=1)


        print(df)
        return df

    def generate_TA(self):
        self.df["sma12"] = ta.sma(self.df["close"], length=12)
        self.df["rsi12"] = ta.rsi(self.df["close"])
        self.df["ao"] = ta.ao(self.df["high"], self.df["low"])

    def update_dataframe(self, msg):
        # ['dateTime', 'open', 'high', 'low', 'close', 'volume']
        try:
            self.locked = True
            # series = [self._get_datetime_single(msg['E']), msg['o'], msg['h'], msg['l'], msg['v']]
            # df = pd.Series(series)
            df = pd.DataFrame([[self._get_datetime_single(msg['E']), msg['o'], msg['h'], msg['l'], msg['c'], msg['v']]])
            df.columns = self.columns_to_keep
            df.set_index('dateTime', inplace=True)
            self.df = self.df.append(df) # , ignore_index=True)

            print("__________________________")
            print(self.df)
        finally:
            self.locked = False


data_frame = test(minutes=10)

def main():
    twm = ThreadedWebsocketManager(testnet=True)
    twm.daemon = True
    twm.start()
    twm.start_symbol_miniticker_socket(callback=data_frame.update_dataframe, symbol=data_frame.symbol)
    twm.join(timeout=20.0)


if __name__ == "__main__":
    main()