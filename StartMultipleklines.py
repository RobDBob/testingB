from binance import enums
from binance import ThreadedWebsocketManager
import psycopg2
import logging
from time import sleep
from binanceHelper.bFinanceAPIFunctions import getClient


class ProcessData:
    query_result_table_name_index = 2

    # vol adjustment for gaps in data
    min_time_gap_secs = 10
    average_time_delay_secs = 3

    def __init__(self):
        self.sorted_data = {}
        self.previous_data = {}

        

    def get_coin_pairs(self):
        #
        client = getClient(test_net=False)
        products = client.get_products()
        return [k["s"] for k in products["data"] if "USDT" in k["s"]]

    def get_kline_steam_names(self):
        coin_pairs = self.get_coin_pairs()
        print(f"retrieved {len(coin_pairs)} coin pairs")
        return [f"{symbol.lower()}@kline_{enums.KLINE_INTERVAL_1MINUTE}" for symbol in coin_pairs]
        
    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """

        print(msg)

processData = ProcessData()

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start()
    twm.start_multiplex_socket(callback=processData.process_msg, streams=processData.get_kline_steam_names()[:3])
    twm.join(300)
    twm.stop()


if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream

    start_web_socket()