from binance import ThreadedWebsocketManager
import logging
import http.client, urllib
import pandas as pd
from time import time

def create_logger(logger_name, file_name=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(file_name)
    formatter    = logging.Formatter('%(asctime)s(%(levelname)s): %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logging.getLogger(logger_name)

logger = create_logger(__name__, "LOG_allCoinTickerNotification.log")



class ProcessData:
    records_to_keep = 100*6 # stores per 10sec, so 100 min of data
    volume_multiplier = 10
    alert_snooze = 60 * 60 # 60 minutes [seconds]
    
    def __init__(self):
        self.snoozed_coins = {}
        self.previous_data = {}
        self.clean_data = {}


    def process_msg(self, msg):
        """
        this method is the entry point with logic 
        Save time stamp in seconds rather than miliseconds
        """

        filtered_to_usdt_tokens = [k for k in msg if "usdt" in k["s"].lower()] 
        filtered_time_to_1m_sec_interval = [k for k in filtered_to_usdt_tokens if k["E"] % 10000 > 9500 or k["E"] % 10000 < 500] 
        if len(filtered_time_to_1m_sec_interval) == 0:
            return
        self.update_clean_data(filtered_time_to_1m_sec_interval)
        self.run_numbers()

    def update_clean_data(self, data):
        """
        purpose of this methos is to calculate: 
            - actual volume traded from 24hr rolling window to 1 min rolling period
            - open & close prices
        """
        for coin_entry in data:
            coin_name = coin_entry["s"]

            if coin_name in self.previous_data:
                previous_data = self.previous_data[coin_name]
                
                volume_delta = round(float(coin_entry["v"]) - float(previous_data["v"]), 4)
                volume_delta = volume_delta if volume_delta > 0 else 0
                new_df =pd.DataFrame([{
                        "timeStamp": coin_entry["E"],
                        "close": round(float(coin_entry["c"]), 4),
                        "volume": volume_delta
                    }])
                
                if coin_name in self.clean_data:
                    self.clean_data[coin_name] = self.clean_data[coin_name].append(new_df, ignore_index=True)
                else:
                    self.clean_data[coin_name]=new_df

                if len(self.clean_data[coin_name]) > self.records_to_keep:
                    self.clean_data[coin_name]=self.clean_data[coin_name].tail(self.records_to_keep)

            self.previous_data[coin_name] = coin_entry

    def run_numbers(self):
        current_time_sec = time()
        
        for coin_name in self.clean_data.keys():
            current_data = self.clean_data[coin_name]
            # check if snooze is on

            if len(current_data) < self.records_to_keep / 2:
                continue

            if current_time_sec < self.snoozed_coins.get(coin_name, 0):
                logger.info(f"Snooze active for: {coin_name}")
                continue
            
            if current_data.volume.quantile(0.99) > current_data.volume.quantile(0.50)* self.volume_multiplier:
                self.snoozed_coins[coin_name] = current_time_sec + self.alert_snooze
                self.send_alert(coin_name)

    def send_alert(self, coin_name):
        logger.info(f"sending alert: {coin_name}")
        message = f"{coin_name}: {self.volume_multiplier}x fold volume increase "
        content={"user": "ufv3dchxo6m7jwkn22kcjm6xp3tn9k", "token":"a57fw7ecaq3fwivktb211qv1u1sh7a", "message": message}
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json", urllib.parse.urlencode(content), { "Content-type": "application/x-www-form-urlencoded" })
        return conn.getresponse()


processData = ProcessData()

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start()
    twm.start_ticker_socket(callback=processData.process_msg)
    twm.join()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream
  
    start_web_socket()
    print("done")