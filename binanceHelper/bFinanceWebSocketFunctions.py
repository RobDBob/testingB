from binance import ThreadedWebsocketManager


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


def getKlines(call_back, timeout=None):
    twm = ThreadedWebsocketManager() #(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=call_back, symbol='MDTUSDT')
    twm.join(timeout=timeout)

def callback(msg):
    print(msg)