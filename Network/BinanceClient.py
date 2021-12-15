from loguru import logger
from binanceHelper import const
import pandas as pd
import requests
from Network.APIFunctions import getBinanceConfig

symbols_to_ignore = []

class BinanceClient:
    def __init__(self, testNet=False):
        self.config = getBinanceConfig(logger, testNet)
        # pd.set_option('display.max_rows', None)

    def get_exchange_info(self):
        url = f"{self.config['url']}/v3/exchangeInfo"
        res = requests.get(url)
        if not res.ok:
            logger.error(f"Failed to get binance exchange info, status code: {res.status_code}")
            raise
        return res.json()

    def get_historical_klines(self, symbol, startTime=None, endTime=None, limit=500, interval="1m"):
        params = {"symbol": symbol, "interval": interval, "limit": limit} 
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        url = f"{self.config['url']}/v3/klines"
        res = requests.get(url, params=params)

        df = pd.DataFrame().from_records(res.json())
        df.columns = const.KLINE_COLUMNS
        df = df.drop(const.KLINE_COLUMN_TO_DROP, axis=1)

        # # as timestamp is returned in ms, let us convert this back to proper timestamps.
        # df.set_index('timeStamp', drop=False, inplace=True)
        # df.timeStamp = pd.to_datetime(df.timeStamp, unit='ms').dt.strftime(const.date_time_format)
        df["high"] = df.high.astype("float")
        df["low"] = df.low.astype("float")
        df["open"] = df.open.astype("float")
        df["close"] = df.close.astype("float")
        df["volume"] = df.volume.astype("float")
        df["timeStamp"] = (df.timeStamp/1000).astype("int64")
        return df

    def get_usdt_symbols(self):
        exchange_info = self.get_exchange_info()
        all_symbols = exchange_info["symbols"]
        usdt_symbols = [k["symbol"] for k in exchange_info["symbols"] if "USDT" in k["symbol"] and not ("DOWNUSDT" in k["symbol"] or "UPUSDT" in k["symbol"] )]
        logger.info(f"retrieved {len(all_symbols)} all symbols, and {len(usdt_symbols)} usdt symbols")
        return usdt_symbols

    def get_order_book(self, symbol, limit=50):
        url = f"{self.config['url']}/v3/depth?symbol={symbol}&limit={limit}"
        res = requests.get(url)
        if not res.ok:
            logger.error(f"Failed to get order books, status code: {res.status_code}")
            raise
        return res.json()

