from binance import ThreadedWebsocketManager
import logging
import http.client, urllib
import pandas as pd

def create_logger(logger_name, file_name=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(file_name)
    formatter    = logging.Formatter('%(asctime)s(%(levelname)s): %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logging.getLogger(logger_name)

logger = create_logger(__name__, "LOG_binancealltickers.log")


def send_notification():
    message={"user": "ufv3dchxo6m7jwkn22kcjm6xp3tn9k", "token":"a57fw7ecaq3fwivktb211qv1u1sh7a", "message": "code test"}
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json", urllib.parse.urlencode(message), { "Content-type": "application/x-www-form-urlencoded" })
    return conn.getresponse()

class ProcessData:
    records_to_keep = 50*60
    
    def __init__(self):
        self.sorted_data = {}
        self.previous_data = {}

        self.clean_data = {}


    def process_msg(self, msg):
        """
        this method is the entry point with logic 
        Save time stamp in seconds rather than miliseconds
        """

        filtered_to_usdt_tokens = [k for k in msg if "usdt" in k["s"].lower()] 
        filtered_time_to_1m_sec_interval = [k for k in filtered_to_usdt_tokens if k["E"] % 60000 > 59500 or k["E"] % 60000 < 500] 
        if len(filtered_time_to_1m_sec_interval) == 0:
            return
        # self.update_clean_data(filtered_time_to_1m_sec_interval)
        self.update_clean_data(msg)

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

    # def check_shit(self):
    #     ds[ds>ds[ds>0].quantile(0.50)*25]
    #     return


processData = ProcessData()

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start()
    twm.start_ticker_socket(callback=processData.process_msg)
    twm.join(timeout=240)

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream
  
    start_web_socket()
    print("done")