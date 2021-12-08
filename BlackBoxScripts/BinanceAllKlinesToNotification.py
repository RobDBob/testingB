from time import sleep
import requests
import pandas as pd
import logging
from datetime import datetime
import pandas_ta as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager


def getClient(test_net=False):
    from pathlib import Path
    from os import path
    import json
    with open(path.join(Path.home(), "binance.json")) as fp:
        b_config = json.loads(fp.read())
    if test_net:
        api_key = b_config["api_key_test"]
        api_secret = b_config["api_secret_test"]
    else:
        api_key = b_config["api_key"]
        api_secret = b_config["api_secret"]
    return (api_key, api_secret)


date_time_format = '%Y-%m-%d %H:%M:%S'

def get_datetime_single(date_time_stamp):
    return datetime.utcfromtimestamp((int(date_time_stamp))).strftime(date_time_format)

def create_logger(logger_name, file_name=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(file_name)
    formatter    = logging.Formatter('%(asctime)s(%(levelname)s): %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logging.getLogger(logger_name)

logger = create_logger(__name__, "LOG_binanceKline.log")

class ProcessData:
    vol_increase_x = 6
    not_increase_x = 6
    back_off_after_notification = 3600

    def __init__(self):
        self.full_klines_data = {}
        self.anomaly_detected_timestamp = {}
        
        # watch for price change, used to estimate accuracy
        self.watch_symbol = {}

    def check_for_anomaly(self, symbol, number_of_trades, volume, time_stamp):
        # check if already was hinted
        if symbol in self.anomaly_detected_timestamp and self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification > time_stamp:
            # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification}")
            return False

        symbol_data = self.full_klines_data.get(symbol, None)
        if symbol_data is None:
            # no data available to compare yet
            return False

        anomaly_detected = (symbol_data.tail(1).volSMA * self.vol_increase_x < volume).bool() & (symbol_data.tail(1).NOTSMA * self.not_increase_x < number_of_trades).bool()
        
        if anomaly_detected:
            # logger.info(f"{get_datetime_single(time_stamp)}: {symbol}, v:{volume}, not: {number_of_trades} - anomaly detected")
            self.anomaly_detected_timestamp[symbol] = time_stamp

        return anomaly_detected

    def notify(self, symbol, volume, price, time_stamp):
        logger.info(f"{get_datetime_single(time_stamp)}: {symbol} =============== NOTIFICATION =============== : price: {price}, volume: {volume}")
        return

    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """

        is_kline_complete = msg["data"]["k"]["x"]
        symbol = msg["data"]["s"]
        number_of_trades = msg["data"]["k"]["n"]
        volume = round(float(msg["data"]["k"]["v"]), 4)
        close = round(float(msg["data"]["k"]["c"]), 4)
        time_stamp = msg["data"]["E"]/1000

        if not is_kline_complete:
            if len(self.full_klines_data.get(symbol, [])) < 60:
                # logger.info(f"{symbol}: insufficient kline data, continue")
                return
            
            if self.check_for_anomaly(symbol, number_of_trades, volume, time_stamp):
                self.notify(symbol, volume, close, time_stamp)
            return

        data = {
            "timeStamp": time_stamp,
            "close": close, 
            "volume": volume, 
            "numberOfTrades": number_of_trades}

        self.save_data(data, symbol)

    def save_data(self, data, symbol):
        # logger.info(f"Symbol: {symbol} - new data added")
        if symbol not in self.full_klines_data:
            self.full_klines_data[symbol] = pd.DataFrame()

        if len(self.full_klines_data[symbol]) > 150:
            self.full_klines_data[symbol] = self.full_klines_data[symbol].tail(120)

        self.full_klines_data[symbol]=self.full_klines_data[symbol].append(data, ignore_index=True)
        self.full_klines_data[symbol]["volSMA"]=ta.sma(self.full_klines_data[symbol].volume, length=60)
        self.full_klines_data[symbol]["NOTSMA"]=ta.sma(self.full_klines_data[symbol].numberOfTrades, length=60)




def get_usdt_symbols():
    res = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    if not res.ok:
        logger.error(f"Failed to get binance exchange info, status code: {res.status_code}")
        raise
    response_json = res.json()
    all_symbols = response_json["symbols"]
    usdt_symbols = [k["symbol"] for k in response_json["symbols"] if "USDT" in k["symbol"]]
    print(f"retrieved {len(all_symbols)} all symbols, and {len(usdt_symbols)} usdt symbols")
    return usdt_symbols

def start_web_socket(processData):
    """
    listen to websocket, populate postgresql with result
    """
    import traceback

    coin_pairs = get_usdt_symbols()
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")
    websocket_manager.create_stream('kline_1m', coin_pairs, stream_label="dict", output="dict")
    
    
    while True:
        if websocket_manager.is_manager_stopping():
            exit(0)

        data = websocket_manager.pop_stream_data_from_stream_buffer()

        
        if data is False:
            sleep(0.01)
            continue

        elif data is None:
            continue

        elif data.get("result", 1) is None:
            # odd case at the start when no result is given
            # dict: {'result': None, 'id': 1}
            continue

        try:
            # print(data)
            processData.process_msg(data)

        except Exception:
            print(f"last kline: {data}")
            print(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)
        

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    processData = ProcessData()
    start_web_socket(processData)
