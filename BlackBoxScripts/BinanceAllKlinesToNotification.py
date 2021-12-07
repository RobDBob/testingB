import pandas as pd
import logging
from datetime import datetime
import pandas_ta as ta
from binance import Client,ThreadedWebsocketManager, enums


def getClient(test_net=False):
    api_key_test = "fjwtEFGgh3rAO29WVPJ7IjQl3dN0Ml0147iLblPPZPQHsm6DGMkJ77LGQkLie20S"
    api_secret_test = "fSKO7rQtgWKePuLZf2IZuTYDl7RDZnniKUCoN9VAgQyjqsCKjza7ftQM00yEivkW"
    return Client(api_key=api_key_test, api_secret=api_secret_test, testnet=test_net)


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
        
        # mark purchase, so we'll need time, timestop
        self.purchased_symbol = {}

    def check_for_anomaly(self, symbol, number_of_trades, volume, time_stamp):
        # check if already was hinted
        if symbol in self.anomaly_detected_timestamp and self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification > time_stamp:
            logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_timestamp[symbol] + self.back_off_after_notification}")
            return False

        symbol_data = self.full_klines_data.get(symbol, None)
        if symbol_data is None:
            # no data available to compare yet
            return False

        anomaly_detected = (symbol_data.tail(1).volSMA * self.vol_increase_x < volume).bool() & (symbol_data.tail(1).NOTSMA * self.not_increase_x < number_of_trades).bool()
        
        if anomaly_detected:
            logger.info(f"{get_datetime_single(time_stamp)}: {symbol}, v:{volume}, not: {number_of_trades} - anomaly detected")
            self.anomaly_detected_timestamp[symbol] = time_stamp

        return anomaly_detected

    def notify(self, symbol, price, time_stamp):
        logger.info(f"{get_datetime_single(time_stamp)}: {symbol} =============== NOTIFICATION =============== : price: {price}")
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
        time_stamp = msg["data"]["k"]["T"]/1000

        if not is_kline_complete:
            if len(self.full_klines_data.get(symbol, [])) < 60:
                # logger.info(f"{symbol}: insufficient kline data, continue")
                return
            
            if self.check_for_anomaly(symbol, number_of_trades, volume, time_stamp):
                self.notify(symbol, close, time_stamp)
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


processData = ProcessData()

def get_kline_steam_names():
    client = getClient(test_net=False)
    products = client.get_products()
    coin_pairs = [k["s"] for k in products["data"] if "USDT" in k["s"]]
    print(f"retrieved {len(coin_pairs)} coin pairs")
    return [f"{symbol.lower()}@kline_{enums.KLINE_INTERVAL_1MINUTE}" for symbol in coin_pairs]

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    streams = get_kline_steam_names()[:3]
    logger.info(streams)
    twm = ThreadedWebsocketManager()
    twm.daemon = True
    twm.start()
    twm.start_multiplex_socket(callback=processData.process_msg, streams=streams)
    twm.join(120)
    twm.stop()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream
    start_web_socket()