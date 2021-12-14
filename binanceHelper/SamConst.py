
API_URL = 'https://api.binance.{}/api'
API_TESTNET_URL = 'https://testnet.binance.vision/api'
MARGIN_API_URL = 'https://api.binance.{}/sapi'
WEBSITE_URL = 'https://www.binance.{}'
FUTURES_URL = 'https://fapi.binance.{}/fapi'
FUTURES_TESTNET_URL = 'https://testnet.binancefuture.com/fapi'
FUTURES_DATA_URL = 'https://fapi.binance.{}/futures/data'
FUTURES_DATA_TESTNET_URL = 'https://testnet.binancefuture.com/futures/data'
FUTURES_COIN_URL = "https://dapi.binance.{}/dapi"
FUTURES_COIN_TESTNET_URL = 'https://testnet.binancefuture.com/dapi'
FUTURES_COIN_DATA_URL = "https://dapi.binance.{}/futures/data"
FUTURES_COIN_DATA_TESTNET_URL = 'https://testnet.binancefuture.com/futures/data'
OPTIONS_URL = 'https://vapi.binance.{}/vapi'
OPTIONS_TESTNET_URL = 'https://testnet.binanceops.{}/vapi'
PUBLIC_API_VERSION = 'v1'
PRIVATE_API_VERSION = 'v3'
MARGIN_API_VERSION = 'v1'
FUTURES_API_VERSION = 'v1'
FUTURES_API_VERSION2 = "v2"
OPTIONS_API_VERSION = 'v1'

REQUEST_TIMEOUT: float = 10

SYMBOL_TYPE_SPOT = 'SPOT'

ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'

ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

FUTURE_ORDER_TYPE_LIMIT = 'LIMIT'
FUTURE_ORDER_TYPE_MARKET = 'MARKET'
FUTURE_ORDER_TYPE_STOP = 'STOP'
FUTURE_ORDER_TYPE_STOP_MARKET = 'STOP_MARKET'
FUTURE_ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
FUTURE_ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

ORDER_RESP_TYPE_ACK = 'ACK'
ORDER_RESP_TYPE_RESULT = 'RESULT'
ORDER_RESP_TYPE_FULL = 'FULL'

# For accessing the data returned by Client.aggregate_trades().
AGG_ID = 'a'
AGG_PRICE = 'p'
AGG_QUANTITY = 'q'
AGG_FIRST_TRADE_ID = 'f'
AGG_LAST_TRADE_ID = 'l'
AGG_TIME = 'T'
AGG_BUYER_MAKES = 'm'
AGG_BEST_MATCH = 'M'

# new asset transfer api enum
SPOT_TO_FIAT = "MAIN_C2C"
SPOT_TO_USDT_FUTURE = "MAIN_UMFUTURE"
SPOT_TO_COIN_FUTURE = "MAIN_CMFUTURE"
SPOT_TO_MARGIN_CROSS = "MAIN_MARGIN"
SPOT_TO_MINING = "MAIN_MINING"
FIAT_TO_SPOT = "C2C_MAIN"
FIAT_TO_USDT_FUTURE = "C2C_UMFUTURE"
FIAT_TO_MINING = "C2C_MINING"
USDT_FUTURE_TO_SPOT = "UMFUTURE_MAIN"
USDT_FUTURE_TO_FIAT = "UMFUTURE_C2C"
USDT_FUTURE_TO_MARGIN_CROSS = "UMFUTURE_MARGIN"
COIN_FUTURE_TO_SPOT = "CMFUTURE_MAIN"
MARGIN_CROSS_TO_SPOT = "MARGIN_MAIN"
MARGIN_CROSS_TO_USDT_FUTURE = "MARGIN_UMFUTURE"
MINING_TO_SPOT = "MINING_MAIN"
MINING_TO_USDT_FUTURE = "MINING_UMFUTURE"
MINING_TO_FIAT = "MINING_C2C"