from enum import Enum

date_time_format = '%Y-%m-%d %H:%M:%S'
all_columns = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
columns_to_drop = ['closeTime', 'quoteAssetVolume', 'takerBuyBaseVol','takerBuyQuoteVol','ignore']
columns_to_keep = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'numberOfTrades']

class TA(Enum):
    buy = 1
    sell = -1
    other = 0