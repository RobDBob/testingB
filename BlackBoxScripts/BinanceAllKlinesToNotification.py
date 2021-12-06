import pandas as pd
import logging
from binance import enums
from binance import ThreadedWebsocketManager
from binanceHelper.bFinanceAPIFunctions import getClient

# def create_logger(logger_name, file_name=None):
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.DEBUG)
#     file_handler = logging.FileHandler(file_name)
#     formatter    = logging.Formatter('%(asctime)s(%(levelname)s): %(message)s')
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#     return logging.getLogger(logger_name)

# logger = create_logger(__name__, "LOG_binancealltickers.log")

class ProcessData:
    def __init__(self):
        self.full_klines_data = {}

    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """

        is_kline_complete = msg["data"]["k"]["x"]
        symbol = msg["data"]["s"]

        if not is_kline_complete:
            if self.is_volume_an_anomaly():
                self.notify()
            return

        close_price = round(float(msg["data"]["k"]["c"], 4))
        number_of_trades = msg["data"]["k"]["n"]
        base_asset_volume = round(float(msg["data"]["k"]["v"], 4))
        taker_buy_base_asset_volume = round(float(msg["data"]["k"]["V"], 4))
        taker_buy_quote_asset_volume = round(float(msg["data"]["k"]["Q"], 4))

        data = {
            "symbol": msg["data"]["s"],
            "klineEndTime": msg["data"]["k"]["T"]/1000,
            "close": close_price, 
            "numberOfTrades": number_of_trades, 
            "baseVolume": base_asset_volume, 
            "takerBaseVolume": taker_buy_base_asset_volume,
            "takerQuoteVolume": taker_buy_quote_asset_volume}

        self.save_data(data)

    def save_data(self, data):
        if data["symbol"] not in self.full_klines_data:
            self.full_klines_data[data["symbol"]] = pd.DataFrame()
        self.full_klines_data[data["symbol"]].append(data)


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
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start_multiplex_socket(callback=processData.process_msg, streams=get_kline_steam_names())
    twm.join(60)
    twm.stop()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream

    start_web_socket()