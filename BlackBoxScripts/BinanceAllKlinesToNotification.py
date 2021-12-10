import traceback
import time
import pandas as pd
from loguru import logger
from datetime import datetime
import pandas_ta as ta
from binanceHelper.bFinanceAPIFunctions import getClient
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from binanceHelper.BinanceClient import BinanceClient


def get_datetime_single(date_time_stamp):
    return datetime.utcfromtimestamp((int(date_time_stamp))).strftime('%Y-%m-%d %H:%M:%S')

logger.add("LOG_binance_notification.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")

class ProcessData:
    vol_increase_x = 15
    not_increase_x = 15
    back_off_after_notification = 3600
    max_kline_storage_count = 360

    ta_average_length = 60

    def __init__(self, api_client: BinanceClient):
        self.api_client = api_client
        self.full_klines_data = {}
        self.anomaly_detected_timestamp = {}
        
        # watch for price change, used to estimate accuracy
        self.trade_record = {}

    def check_for_anomaly(self, symbol, data):
        if len(self.full_klines_data.get(symbol, [])) < self.ta_average_length:
            self.full_klines_data["symbol"] = self.api_client.get_historical_klines(symbol, limit=self.ta_average_length)
            # logger.info(f"{symbol}: insufficient kline data, continue")
            return

        # check if already was hinted
        if symbol in self.anomaly_detected_timestamp and self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification > data["timeStamp"]:
            # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification}")
            return False

        symbol_data = self.full_klines_data.get(symbol, None)
        if symbol_data is None:
            # no data available to compare yet
            return False
        
        volSMAValue_last_avg_value = round(float(symbol_data.tail(1)["volSMA"].values[0]), 4)
        number_of_trades_last_avg_value = round(float(symbol_data.tail(1)["NOTSMA"].values[0]), 4)

        if (volSMAValue_last_avg_value * self.vol_increase_x < data["volume"]) and (number_of_trades_last_avg_value * self.not_increase_x < data["numberOfTrades"]):
            self.anomaly_detected_timestamp[symbol] = data["timeStamp"]
            
            vol_pct_change = round((volSMAValue_last_avg_value/data["volume"])*100, 4)
            number_of_trades_pct_change = round((float(number_of_trades_last_avg_value)/data["numberOfTrades"])*100, 4)
            
            vol_msg = f"\nVOL: {volSMAValue_last_avg_value}->{data['volume']}({vol_pct_change})%"
            trades_msg  = f"\nNOT: {data['numberOfTrades']}->{number_of_trades_last_avg_value}({number_of_trades_pct_change})%"
            logger.info(f"{symbol}: at ${data['close']}; {vol_msg}; {trades_msg}\n")
            return True
        return False

    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """
        #  close       volume      timeStamp  numberOfTrades

        is_kline_complete = msg["data"]["k"]["x"]
        symbol = msg["data"]["s"]
        
        data = {
            "close": round(float(msg["data"]["k"]["c"]), 4), 
            "volume": round(float(msg["data"]["k"]["v"]), 4),
            "timeStamp": msg["data"]["E"]/1000,
            "numberOfTrades": msg["data"]["k"]["n"]}

        if is_kline_complete:
            self.save_data(data, symbol)
                    
        if self.check_for_anomaly(symbol, data):
            self.record_trade(symbol, data)

    def record_trade(self, symbol, data):
        # check if price is below 
        # {symbol: {buy:{time, price}, }}}
        return

    def save_data(self, data, symbol):
        if symbol not in self.full_klines_data:
            logger.debug(f"{symbol} - create new data frame for storage")
            self.full_klines_data[symbol] = pd.DataFrame()

        if len(self.full_klines_data[symbol]) > ( self.max_kline_storage_count * 1.5) :
            logger.debug(f"{symbol} - trimming data down to {self.max_kline_storage_count}")
            self.full_klines_data[symbol] = self.full_klines_data[symbol].tail(self.max_kline_storage_count)

        self.full_klines_data[symbol]=self.full_klines_data[symbol].append(data, ignore_index=True)

        # in addition
        self.full_klines_data[symbol]["volSMA"]=ta.sma(self.full_klines_data[symbol].volume, length=self.ta_average_length)
        self.full_klines_data[symbol]["NOTSMA"]=ta.sma(self.full_klines_data[symbol].numberOfTrades, length=self.ta_average_length)


@logger.catch
def start_web_socket(processData):
    """
    listen to websocket, populate postgresql with result
    """
    

    coin_pairs = getClient().get_usdt_symbols()
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")
    websocket_manager.create_stream('kline_1m', coin_pairs, stream_label="dict", output="dict")
    
    previous_time_stamp = 0
    while True:
        time_stamp = int(time.time())
        if (time_stamp%900 == 0 and previous_time_stamp < time_stamp):
            # health check
            logger.info("HEALTH CHECK")
            logger.info(f"Stored coin number: {len(processData.full_klines_data)}")
            logger.info(f"Stored coin number entries (BTCUSDT): {len(processData.full_klines_data.get('BTCUSDT', []))}")
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
            processData.process_msg(data)

        except Exception:
            logger.error(f"last kline: {data}")
            logger.error(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)
