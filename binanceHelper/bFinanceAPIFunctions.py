from loguru import logger
import requests
from pathlib import Path
from os import path
import json

logger.add("LOG_api.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")

def getBinanceConfig(test_net=False):
    with open(path.join(Path.home(), "binance.json")) as fp:
        b_config = json.loads(fp.read())
    
    if test_net:
        logger.info("running with binance TEST server")
        return {
            "url": "https://testnet.binance.vision/api", 
            "api_key": b_config["api_key_test"], 
            "api_secret":b_config["api_secret_test"]}
    else:
        logger.info("running with binance LIFE server")
        return {
            "url": "https://api.binance.com/api", 
            "api_key": b_config["api_key"], 
            "api_secret": b_config["api_secret"]}

class BinanceClient:
    def __init__(self, testNet=False):
        self.config = getBinanceConfig(testNet)

    def get_exchange_info(self):
        url = f"{self.config}/v3/exchangeInfo"
        res = requests.get(url)
        if not res.ok:
            logger.error(f"Failed to get binance exchange info, status code: {res.status_code}")
            raise
        return res.json()

    def get_usdt_symbols(self):
        exchange_info = self.get_exchange_info()
        all_symbols = exchange_info["symbols"]
        usdt_symbols = [k["symbol"] for k in exchange_info["symbols"] if "USDT" in k["symbol"]]
        logger.info(f"retrieved {len(all_symbols)} all symbols, and {len(usdt_symbols)} usdt symbols")
        return usdt_symbols


def getClient():
    return BinanceClient()
