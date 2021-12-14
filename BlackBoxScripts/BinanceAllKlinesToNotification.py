import traceback
import time
import pandas as pd
from loguru import logger
import pandas_ta as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from binanceHelper.BinanceClient import BinanceClient
from Helpers.DateHelper import get_datetime_single
from BlackBoxScripts.TransactionManager import TransactionManager
from BlackBoxScripts.AnomalyChecker import AnomalyChecker

class ProcessData:
    # run configuration
    vol_increase_x = 15
    not_increase_x = 15
    back_off_after_notification = 3600
    max_kline_storage_count = 360
    ta_average_length = 60

    def __init__(self, api_client: BinanceClient):
        self.api_client = api_client
        self.full_klines_data = {}
        
        self.anomaly_checker = AnomalyChecker(self.vol_increase_x, self.not_increase_x, self.back_off_after_notification)
        self.transactions = TransactionManager()

    def check_for_anomaly(self, symbol, symbol_ticker_data):
        if self.anomaly_checker.anomaly_already_detected_for_symbol(symbol, symbol_ticker_data["eventTime"]):
            return False

        symbol_kline_data = self.full_klines_data.get(symbol, None)
        if symbol_kline_data:
            return self.anomaly_checker.check(symbol, symbol_kline_data, symbol_ticker_data)
        return False

    def process_websocket_data(self, incoming_message):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """
        #  close volume eventTime  numberOfTrades

        is_kline_complete = incoming_message["data"]["k"]["x"]
        symbol = incoming_message["data"]["s"]
        
        data = {
            "close": round(float(incoming_message["data"]["k"]["c"]), 4), 
            "volume": round(float(incoming_message["data"]["k"]["v"]), 4),
            "eventTime": incoming_message["data"]["E"]/1000,
            "numberOfTrades": incoming_message["data"]["k"]["n"]}

        if is_kline_complete:
            self.save_data(data, symbol)
                    
        if self.check_for_anomaly(symbol, data):
            self.record_trade(symbol, data)

        self.transactions.check_trade_was_profitable(symbol, data)

    def add_ta_analysis(self, symbol):
        self.full_klines_data[symbol]["volSMA"]=ta.sma(self.full_klines_data[symbol].volume, length=self.ta_average_length)
        self.full_klines_data[symbol]["NOTSMA"]=ta.sma(self.full_klines_data[symbol].numberOfTrades, length=self.ta_average_length)        

    def record_trade(self, symbol, data):
        self.transactions.record_purchase(symbol, data["eventTime"], data["close"])
        # check if price is below 
        # {symbol: {buy:{time, price}, }}}
        return
        
    def save_data(self, data, symbol):
        # add new data
        if symbol not in self.full_klines_data:
            # logger.debug(f"{symbol} - create new data frame for storage")
            self.full_klines_data[symbol] = self.api_client.get_historical_klines(symbol, limit=self.ta_average_length)

        # get rid of old data
        if len(self.full_klines_data[symbol]) > ( self.max_kline_storage_count * 1.5) :
            # logger.debug(f"{symbol} - trimming data down to {self.max_kline_storage_count}")
            self.full_klines_data[symbol] = self.full_klines_data[symbol].tail(self.max_kline_storage_count)

        self.full_klines_data[symbol] = self.full_klines_data[symbol].append(data, ignore_index=True)
        self.add_ta_analysis(symbol)


@logger.catch
def start_web_socket(processData):
    """
    listen to websocket, populate postgresql with result
    """
    coin_pairs = processData.api_client.get_usdt_symbols()
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")
    websocket_manager.create_stream('kline_1m', coin_pairs, stream_label="dict", output="dict")
    
    previous_time_stamp = 0
    while True:
        time_stamp = int(time.time())
        if (time_stamp%900 == 0 and previous_time_stamp < time_stamp):
            # health check
            logger.info(f"HEALTH CHECK --- Stored coin number: {len(processData.full_klines_data)}, (BTCUSDT): {len(processData.full_klines_data.get('BTCUSDT', []))}")
            previous_time_stamp = time_stamp

        if websocket_manager.is_manager_stopping():
            exit(0)

        data = websocket_manager.pop_stream_data_from_stream_buffer()
        
        if data is False:
            time.sleep(0.01)
            continue

        elif data is None:
            continue

        elif data.get("result", 1) is None:
            # odd case at the start when no result is given
            # dict: {'result': None, 'id': 1}
            continue

        try:
            processData.process_websocket_data(data)

        except Exception:
            logger.error(f"last kline: {data}")
            logger.error(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)
