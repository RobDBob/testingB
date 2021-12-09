import time
from time import sleep
import requests
import pandas as pd
from loguru import logger
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


def get_datetime_single(date_time_stamp):
    return datetime.utcfromtimestamp((int(date_time_stamp))).strftime('%Y-%m-%d %H:%M:%S')

logger.add("LOG_binance_notification.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")

class ProcessData:
    vol_increase_x = 8
    not_increase_x = 8
    back_off_after_notification = 3600
    max_kline_storage_count = 360

    def __init__(self):
        self.full_klines_data = {}
        self.anomaly_detected_timestamp = {}
        
        # watch for price change, used to estimate accuracy
        self.watch_symbol = {}

    def check_for_anomaly(self, symbol, data):
        # check if already was hinted
        if symbol in self.anomaly_detected_timestamp and self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification > data["timeStamp"]:
            # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification}")
            return False

        symbol_data = self.full_klines_data.get(symbol, None)
        if symbol_data is None:
            # no data available to compare yet
            return False
        
        volSMAValue_last_avg_value = symbol_data.tail(1)["volSMA"]
        number_of_trades_last_avg_value = symbol_data.tail(1)["NOTSMA"] 

        if (volSMAValue_last_avg_value * self.vol_increase_x < data["volume"]).bool() & (number_of_trades_last_avg_value* self.not_increase_x < data["numberOfTrades"]).bool():
            self.anomaly_detected_timestamp[symbol] = data["timeStamp"]
            
            vol_pct_change = round((float(volSMAValue_last_avg_value)/data["volume"])*100, 4)
            number_of_trades_pct_change = round((float(number_of_trades_last_avg_value)/data["numberOfTrades"])*100, 4)
            
            msg = f"{get_datetime_single(data['timeStamp'])}: {symbol} == ANOMALY == : current ${data['close']}, vol pct: {vol_pct_change}%, number of trades pct: {number_of_trades_pct_change}%"
            logger.info(msg)

    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """

        is_kline_complete = msg["data"]["k"]["x"]
        symbol = msg["data"]["s"]
        
        data = {
            "timeStamp": msg["data"]["E"]/1000,
            "close": round(float(msg["data"]["k"]["c"]), 4), 
            "volume": round(float(msg["data"]["k"]["v"]), 4), 
            "numberOfTrades": msg["data"]["k"]["n"]}

        if not is_kline_complete:
            if len(self.full_klines_data.get(symbol, [])) < 60:
                # logger.info(f"{symbol}: insufficient kline data, continue")
                return
            
            self.check_for_anomaly(symbol, data)

        self.save_data(data, symbol)

    def save_data(self, data, symbol):
        if symbol not in self.full_klines_data:
            logger.debug(f"{symbol} - create new data frame for storage")
            self.full_klines_data[symbol] = pd.DataFrame()

        if len(self.full_klines_data[symbol]) > ( self.max_kline_storage_count * 1.5) :
            logger.debug(f"{symbol} - trimming data down to {self.max_kline_storage_count}")
            self.full_klines_data[symbol] = self.full_klines_data[symbol].tail(self.max_kline_storage_count)

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
    logger.info(f"retrieved {len(all_symbols)} all symbols, and {len(usdt_symbols)} usdt symbols")
    return usdt_symbols

@logger.catch
def start_web_socket(processData):
    """
    listen to websocket, populate postgresql with result
    """
    import traceback

    coin_pairs = get_usdt_symbols()
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")
    websocket_manager.create_stream('kline_1m', coin_pairs, stream_label="dict", output="dict")
    
    previous_time_stamp = 0
    while True:
        time_stamp = int(time.time())
        if (time_stamp%300 == 0 and previous_time_stamp < time_stamp):
            # health check
            logger.info("HEALTH CHECK")
            logger.info(f"Stored coin number: {len(processData.full_klines_data)}")
            logger.info(f"Stored coin number entries (BTCUSDT): {len(processData.full_klines_data.get('BTCUSDT', []))}")
            previous_time_stamp = time_stamp

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
            processData.process_msg(data)

        except Exception:
            logger.error(f"last kline: {data}")
            logger.error(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)
        

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    processData = ProcessData()
    start_web_socket(processData)
