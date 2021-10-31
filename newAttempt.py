from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
import datetime, time
import pandas_ta as ta
from main1dbstuff import saveToFile, readFromFile
from MathFunctions import TATesting

class test:
    all_columns = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
    columns_to_drop = ['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore']
    columns_to_keep = ['dateTime', 'open', 'high', 'low', 'close', 'volume']
    date_time_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, symbol, historic_minutes, kline_interval, test_net):
        self.symbol = symbol
        self.kline_interval = kline_interval
        self.test_net = test_net

        self.df = self.getHistoricalData(historic_minutes)
        print(self.df)

    def _rewrite_data_cleanup(self, json_data):
        """
        Save and read from json, clean up data
        to investigate why this is needed
        """
        temp_file_name = "temp_json.json"
        saveToFile(json_data, temp_file_name)
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
        
        df = self._rewrite_data_cleanup(candle)
        df.columns = self.all_columns
        
        # # as timestamp is returned in ms, let us convert this back to proper timestamps.
        df.set_index('dateTime', drop=False, inplace=True)
        df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime(self.date_time_format)

        # Get rid of columns we do not need
        return df.drop(self.columns_to_drop, axis=1)

    

    def do_stuff(self, msg):
        if (self.update_dataframe(msg)):
            buy = []
            sell = []
            buy.append(TATesting.rsi_test(ta.rsi(self.df["close"], length=12), buy=True))
            sell.append(TATesting.rsi_test(ta.rsi(self.df["close"], length=12), buy=False))

            buy.append(TATesting.stoch_test(ta.stoch(self.df["high"], self.df["low"], self.df["close"]), buy=True))
            sell.append(TATesting.stoch_test(ta.stoch(self.df["high"], self.df["low"], self.df["close"]), buy=False))

            buy.append(TATesting.bb_test(self.df, buy=True))
            sell.append(TATesting.bb_test(self.df, buy=False))
            
            print(f"____________________________________________{self.df.loc[self.df.index[-1], 'dateTime']}:{self.df.loc[self.df.index[-1], 'close']}")
            print(f"BUY: {all(buy)}")
            print(f"SELL: {all(sell)}")
            print("____________________________________________")


            # self.df.to_json("output.json")

    def update_dataframe(self, msg):
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.datetime.utcfromtimestamp(msg['E']/1000) > datetime.datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.locked = True
            try:
                df = pd.DataFrame([[msg['E'], float(msg['k']['o']), float(msg['k']['h']), float(msg['k']['l']), float(msg['k']['c']), float(msg['k']['v'])]])
                df.columns = self.columns_to_keep
                df.set_index('dateTime', drop=False, inplace=True)
                df.dateTime = self._get_datetime_single(df.dateTime)
                self.df = self.df.append(df)
                
            finally:
                self.locked = False
                return True

                # print(f"Updated: TRUE: {df.loc[df.index[-1], 'dateTime']}")
        else:
            counted = datetime.datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000).strftime(self.date_time_format)
            # print(f"Updated: FALSE: {self._get_datetime_single(msg['E'])} > {counted}")
            print(f"ping________________________ {self._get_datetime_single(msg['E'])}")
            return False


data_frame = test(symbol="BTCUSDT", historic_minutes=60, kline_interval="1m", test_net=True)

def main():
    twm = ThreadedWebsocketManager(testnet=data_frame.test_net)
    twm.daemon = True
    twm.start()
    #twm.start_symbol_miniticker_socket(callback=data_frame.do_stuff, symbol=data_frame.symbol)
    twm.start_kline_socket(callback=data_frame.do_stuff, symbol=data_frame.symbol)
    twm.join(timeout=300.0)


if __name__ == "__main__":
    main()