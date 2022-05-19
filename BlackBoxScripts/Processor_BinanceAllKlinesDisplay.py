from pprint import pprint
import pandas_ta as ta
from Network.BinanceClient import BinanceClient

# payload
# {
#   "e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BNBBTC",  // Symbol
#     "i": "1m",      // Interval
#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
#     "B": "123456"   // Ignore
#   }
# }

class Processor_BinanceAllKlinesDisplay:
    def __init__(self, stable_coin: str):
        self.stable_coin = stable_coin
        
    def process_websocket_data(self, incoming_message):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """
        is_kline_complete = incoming_message["data"]["k"]["x"]
        symbol = incoming_message["data"]["s"]

        if self.stable_coin.lower() not in symbol.lower():
            return
        
        tick_data = {
            "open": round(float(incoming_message["data"]["k"]["o"]), 4), 
            "close": round(float(incoming_message["data"]["k"]["c"]), 4), 
            "volume": round(float(incoming_message["data"]["k"]["v"]), 4),
            "eventTime": incoming_message["data"]["E"]/1000,
            "numberOfTrades": incoming_message["data"]["k"]["n"]}

        if is_kline_complete:
            pprint(tick_data)