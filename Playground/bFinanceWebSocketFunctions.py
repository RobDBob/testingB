from binance import ThreadedWebsocketManager
from financeMathFunctions import get_ma_price, update_tick_history

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