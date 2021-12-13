import traceback
import time
import pandas as pd
from loguru import logger
import pandas_ta as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from binanceHelper.BinanceClient import BinanceClient
from Helpers.DateHelper import get_datetime_single
from BlackBoxScripts.RecordedActions import RecordedActions

class ProcessData:
    vol_increase_x = 15
    not_increase_x = 15
    back_off_after_notification = 3600
    max_kline_storage_count = 360

    ta_average_length = 60

    def __init__(self, api_client: BinanceClient):
        self.api_client = api_client
        self.full_klines_data = {}
        self.anomaly_detected_eventTime = {}
        
        # watch for price change, used to estimate accuracy
        self.transactions = RecordedActions()

    def check_for_anomaly(self, symbol, data):
        if len(self.full_klines_data.get(symbol, [])) < self.ta_average_length:
            self.full_klines_data[symbol] = self.api_client.get_historical_klines(symbol, limit=self.ta_average_length)
            self.calculate_aditionals(symbol)
            # logger.info(f"{symbol}: insufficient kline data, continue")
            return

        # check if already was hinted
        if symbol in self.anomaly_detected_eventTime and self.anomaly_detected_eventTime[symbol] + self.back_off_after_notification > data["eventTime"]:
            # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_eventTime[symbol] + self.back_off_after_notification}")
            return False

        symbol_data = self.full_klines_data.get(symbol, None)
        if symbol_data is None:
            # no data available to compare yet
            return False
        
        volSMAValue_last_avg_value = round(float(symbol_data.tail(1)["volSMA"].values[0]), 4)
        number_of_trades_last_avg_value = round(float(symbol_data.tail(1)["NOTSMA"].values[0]), 4)

        if (volSMAValue_last_avg_value * self.vol_increase_x < data["volume"]) and (number_of_trades_last_avg_value * self.not_increase_x < data["numberOfTrades"]):
            self.anomaly_detected_eventTime[symbol] = data["eventTime"]
            
            vol_pct_change = round((data["volume"]/volSMAValue_last_avg_value)*100, 4)
            number_of_trades_pct_change = round((float(data["numberOfTrades"]/number_of_trades_last_avg_value))*100, 4)
            
            vol_msg = f"\nVOL: {volSMAValue_last_avg_value}->{data['volume']}({vol_pct_change})%"
            trades_msg  = f"\nNOT: {number_of_trades_last_avg_value}->{data['numberOfTrades']}({number_of_trades_pct_change})%"
            logger.info(f"{symbol}: at ${data['close']}; {vol_msg}; {trades_msg}\n")
            return True
        return False

    def deal_with_it(self, incoming):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """
        #  close       volume      eventTime  numberOfTrades

        is_kline_complete = incoming["data"]["k"]["x"]
        symbol = incoming["data"]["s"]
        
        data = {
            "close": round(float(incoming["data"]["k"]["c"]), 4), 
            "volume": round(float(incoming["data"]["k"]["v"]), 4),
            "eventTime": incoming["data"]["E"]/1000,
            "numberOfTrades": incoming["data"]["k"]["n"]}

        if is_kline_complete:
            self.save_data(data, symbol)
                    
        if self.check_for_anomaly(symbol, data):
            self.record_trade(symbol, data)

        self.check_trade_was_profitable(symbol, data)

    def calculate_aditionals(self, symbol):
        self.full_klines_data[symbol]["volSMA"]=ta.sma(self.full_klines_data[symbol].volume, length=self.ta_average_length)
        self.full_klines_data[symbol]["NOTSMA"]=ta.sma(self.full_klines_data[symbol].numberOfTrades, length=self.ta_average_length)        

    def record_trade(self, symbol, data):
        self.transactions.record_purchase(symbol, data["eventTime"], data["close"])
        # check if price is below 
        # {symbol: {buy:{time, price}, }}}
        return

    def check_trade_was_profitable(self, symbol, data):
        if symbol not in self.transactions.records:
            return
        
        # what time lapse we are interested in
        # what percentage increase we are interested in
        # the moment it increases by 5% - sell
        # if it does not increase within 1hr - mark it as failed invest
        # stop loss? - 5% ??
        event_time = data["eventTime"] # in seconds
        current_price = data["close"]
        (purchase_time, purchase_price) = self.transactions.records[symbol]


        # after 10min - emergency sell?
        emergency_sell_time = 10 * 60
        if purchase_time + emergency_sell_time < event_time :
            logger.info(f"{symbol}: OUT OF TIME sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.transactions.records[symbol])

        # stop loss, after 2min
        stop_loss_time = 2 * 60
        percentage_loss = 0.95
        if (purchase_time + stop_loss_time < event_time) and ( current_price < purchase_price * percentage_loss):
            logger.info(f"{symbol}: STOP LOSS sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.transactions.records[symbol])

        # good sell
        percentage_gain = 1.1
        if current_price > purchase_price * percentage_gain:
            logger.info(f"{symbol}: GOOD sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.transactions.records[symbol])
        



    def save_data(self, data, symbol):
        if symbol not in self.full_klines_data:
            # logger.debug(f"{symbol} - create new data frame for storage")
            self.full_klines_data[symbol] = pd.DataFrame()

        if len(self.full_klines_data[symbol]) > ( self.max_kline_storage_count * 1.5) :
            # logger.debug(f"{symbol} - trimming data down to {self.max_kline_storage_count}")
            self.full_klines_data[symbol] = self.full_klines_data[symbol].tail(self.max_kline_storage_count)

        self.full_klines_data[symbol]=self.full_klines_data[symbol].append(data, ignore_index=True)

        # in addition
        self.calculate_aditionals(symbol)


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
            processData.deal_with_it(data)

        except Exception:
            logger.error(f"last kline: {data}")
            logger.error(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)
