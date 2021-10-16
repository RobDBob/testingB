import json
import sys
import time
import datetime

from binance import ThreadedWebsocketManager

# api_key = '<api_key'>
# api_secret = '<api_secret'>

tick_history = []

def update_tick_history(current_price, max_store_size):
    """
    stores last x-prices 
    """
    current_price = float(current_price)
    if len(tick_history) < max_store_size:
        tick_history.append(current_price)
    else:
        tick_history.pop(0)
        tick_history.append(current_price)

def get_ma_price(lookback=5):
    if len(tick_history) < lookback:
        ma_price = -1
    else:
        recent_tick_prices = tick_history[-lookback:]
        print("--------------------------")
        print(tick_history)
        print(recent_tick_prices)
        print("--------------------------")
        ma_price = sum(recent_tick_prices)/len(recent_tick_prices)

    return ma_price

def getMiniTickerPrices():
    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager() #(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.daemon = True
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg['e']}")
        print(msg)
        
    def symbol_miniticker_socket_handler(msg):
        # print(msg)
        # "o" - opening price for current tick, which is 24hrs before
        # "c" - closing price for current tick, which is most current price

        current_price = msg["c"]
        ma_price_5 = get_ma_price(lookback=5)
        ma_price_8 = get_ma_price(lookback=8)
        update_tick_history(current_price, max_store_size=8)

        print(f"current price: {current_price}")
        print(f"ma_price_5: {ma_price_5}")
        print(f"ma_price_8: {ma_price_8}")

    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    # streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    # <symbol>@kline_<interval>
    # streams = ['bnbbtc@mkline30s']
    streams = ['bnbbtc@miniTicker']
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
    ## twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # twm.start_miniticker_socket(callback=miniticker_socket_handler)

    twm.start_symbol_miniticker_socket(callback=symbol_miniticker_socket_handler, symbol=symbol)
    twm.join(timeout=60.0)

def getAllTickerPrices(call_back):
    twm = ThreadedWebsocketManager() #(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.daemon = True
    twm.start()
    twm.start_ticker_socket(callback=call_back)
    twm.join(timeout=3.0)

def getickerPrices1(call_back):
    twm = ThreadedWebsocketManager() #(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.daemon = True
    twm.start()
    twm.start_symbol_ticker_socket(callback=call_back, symbol='BNBBTC')
    twm.join(timeout=10.0)

def add_data_to_file():
    def load_to_file_callback(msg):
        print(f"reading stuff: {datetime.datetime.now().time()}")
        print(msg)
        json.dump(msg, file_handler)
        file_handler.write(',')

    with open("miniticker.json", mode="w") as file_handler:
        file_handler.write("[")
        # getAllTickerPrices(load_to_file_callback)
        getickerPrices1(load_to_file_callback)
        file_handler.write("]")

def add_data_to_db():
    def load_to_db_callback(msg):
        response = dynamodb.put_item(
            TableName='Prices15min', 
            Item=msg
        )
        print("____________________")
        print(response)
        print("____________________")

    import boto3
    import json
    #dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    dynamodb = boto3.client('dynamodb')
    getickerPrices1(load_to_db_callback)


if __name__ == "__main__":
    add_data_to_file()