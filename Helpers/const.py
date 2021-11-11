from enum import Enum

date_time_format = '%Y-%m-%d %H:%M:%S'
all_columns = ['timeStamp', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
columns_to_drop = ['closeTime', 'quoteAssetVolume', 'takerBuyBaseVol','takerBuyQuoteVol','ignore']
columns_to_keep = ['timeStamp', 'open', 'high', 'low', 'close', 'volume', 'numberOfTrades']

class TransactionType(Enum):
    buy = "buy"
    sell = "sell"