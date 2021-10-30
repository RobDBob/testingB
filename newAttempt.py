from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import os
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

    def __init__(self, symbol, historic_minutes, kline_interval, test_net):
        self.symbol = symbol
        self.kline_interval = kline_interval
        self.test_net = test_net

        self.df = self.getHistoricalData(historic_minutes)

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
        client = getClient(self.test_net)
        # Calculate the timestamps for the binance api function
        untilThisDate = datetime.datetime.utcnow()
        sinceThisDate = untilThisDate - datetime.timedelta(minutes = howLongMinutes)
        # Execute the query from binance - timestamps must be converted to strings !
        candle = client.get_historical_klines(self.symbol, self.kline_interval, str(sinceThisDate), str(untilThisDate))
        
        df = self._get_df_from_candle(candle)
        df.columns = self.all_columns

        
        # # as timestamp is returned in ms, let us convert this back to proper timestamps.
        # df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(self.date_time_format) # self._get_datetime_series(df.dateTime)
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
            df = pd.DataFrame([[msg['E'], msg['o'], msg['h'], msg['l'], msg['c'], msg['v']]])
            df.columns = self.columns_to_keep
            df.set_index('dateTime', inplace=True)
            self.df = self.df.append(df) # , ignore_index=True)

            print("__________________________")
            # self.df.tail(1).dateTime
            print(self.df)
        finally:
            self.locked = False

# test_net = True
data_frame = test(symbol="BTCUSDT", historic_minutes=12, kline_interval="3m", test_net=True)

def main():
    twm = ThreadedWebsocketManager(testnet=data_frame.test_net)
    twm.daemon = True
    twm.start()
    twm.start_symbol_miniticker_socket(callback=data_frame.update_dataframe, symbol=data_frame.symbol)
    twm.join(timeout=20.0)


if __name__ == "__main__":
    main()