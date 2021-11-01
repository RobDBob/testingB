from binance import ThreadedWebsocketManager, helpers
from binance.enums import KLINE_INTERVAL_1MINUTE
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
from datetime import datetime
import pandas_ta as ta
from MathFunctions import TATesting
from Helpers import PandaFunctions, const
import logging


class DataUpdater:
    def __init__(self, symbol, kline_interval, historic_data=None):
        self.symbol = symbol
        self.kline_interval = kline_interval

        if historic_data is None:
            self.df = pd.DataFrame()
        else:
            self.df = historic_data

        self.logger = logging.getLogger("test")
    
    def _get_datetime_series(self, date_time_stamps_ms):
        # print(f"---- type: {type(date_time_stamps_ms)}, value: {date_time_stamps_ms}")
        return pd.to_datetime(date_time_stamps_ms, unit='ms').dt.strftime(const.date_time_format)

    def _get_datetime_single(self, date_time_stamp_ms):
        return datetime.utcfromtimestamp((int(date_time_stamp_ms)/1000)).strftime(const.date_time_format)

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
            
            self.logger.info(f"{self.df.loc[self.df.index[-1], 'dateTime']} - {self.df.loc[self.df.index[-1], 'close']}. BUY: {all(buy)}, SELL: {all(sell)}")

            # self.df.to_json("output.json")

    def update_dataframe(self, msg):
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.utcfromtimestamp(msg['E']/1000) > datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.locked = True
            try:
                df = pd.DataFrame([[msg['E'], float(msg['k']['o']), float(msg['k']['h']), float(msg['k']['l']), float(msg['k']['c']), float(msg['k']['v'])]])
                df.columns = const.columns_to_keep
                df.set_index('dateTime', drop=False, inplace=True)
                df.dateTime = self._get_datetime_single(df.dateTime)
                self.df = self.df.append(df)

            except Exception as e:
                print(e)

                
            finally:
                self.locked = False
                return True

                # print(f"Updated: TRUE: {df.loc[df.index[-1], 'dateTime']}")
        else:
            # print(f"Updated: FALSE: {self._get_datetime_single(msg['E'])} > {counted}")
            print(f"ping________________________ {self._get_datetime_single(msg['E'])}")
            return False

def main(data_updater, test_net):
    twm = ThreadedWebsocketManager(testnet=test_net)
    twm.daemon = True
    twm.start()
    #twm.start_symbol_miniticker_socket(callback=data_frame.do_stuff, symbol=data_frame.symbol)
    twm.start_kline_socket(callback=data_updater.do_stuff, symbol=data_updater.symbol)
    twm.join(timeout=60.0)


if __name__ == "__main__":
    test_net = True
    symbol = "BTCUSDT"
    interval = KLINE_INTERVAL_1MINUTE
    client = getClient(test_net=test_net)
    historic_data = PandaFunctions.getHistoricalData(client, symbol, howLongMinutes=60, kline_interval=interval)
    data_updater = DataUpdater(symbol=symbol, kline_interval=interval, historic_data=historic_data)

    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('TATestRecords.log')
    formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    main(data_updater, test_net)